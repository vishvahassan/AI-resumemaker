"""
Resume analyzer views with robust error handling and logging.
"""
import io
import logging
import tempfile
from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from django.core.files.base import ContentFile

from .models import UploadedResume
from .services.text_extraction import (
    extract_resume_text,
    extract_text_from_pdf,
    OCR_FALLBACK_THRESHOLD,
)
from .services.openai_service import analyze_resume_with_ai

logger = logging.getLogger(__name__)

# Max file size (bytes); use Django setting FILE_UPLOAD_MAX_MEMORY_SIZE
MAX_UPLOAD_SIZE = getattr(
    settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 5 * 1024 * 1024
)


def index(request):
    """Landing page with hero and upload section."""
    return render(request, 'resume_analyzer/index.html')


@require_http_methods(['GET', 'POST'])
def upload(request):
    """
    Handle resume upload: validate file type (.pdf/.txt only) and size (max 5 MB),
    save to media, extract text, run AI analysis. Robust error handling throughout.
    """
    if request.method != 'POST':
        return redirect('index')

    file = request.FILES.get('resume_file')
    if not file:
        messages.error(request, 'Please select a PDF or text file to upload.')
        return redirect('index')

    name = getattr(file, 'name', '') or 'resume'
    # Accept ONLY .pdf and .txt files
    if not (name.lower().endswith('.pdf') or name.lower().endswith('.txt')):
        messages.error(request, 'Only PDF and .txt files are allowed. Please upload a valid file.')
        return redirect('index')

    # File size validation: max 5 MB (use Django setting FILE_UPLOAD_MAX_MEMORY_SIZE)
    try:
        file_size = file.size
    except Exception:
        file_size = 0
    if file_size > MAX_UPLOAD_SIZE:
        max_mb = MAX_UPLOAD_SIZE // (1024 * 1024)
        messages.error(
            request,
            f'File is too large. Maximum size is {max_mb} MB. Please choose a smaller file.'
        )
        return redirect('index')

    # Read file content once (avoids seek/rewind issues with some upload handlers)
    try:
        file.seek(0)
        content = file.read()
    except Exception as e:
        logger.exception('Failed to read uploaded file')
        messages.error(request, f'Could not read file. Error: {e!s}')
        return redirect('index')

    if not content:
        messages.error(request, 'The file is empty.')
        return redirect('index')

    # Extract text from in-memory content (no dependency on saved file path)
    extracted_text = ""
    if name.lower().endswith('.pdf'):
        try:
            extracted_text = extract_text_from_pdf(io.BytesIO(content))
        except Exception as e:
            logger.warning('PDF extraction failed: %s', e, exc_info=True)
            # Fallback: write to temp file and use full pipeline (includes OCR for scanned PDFs)
            try:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                try:
                    extracted_text = extract_resume_text(tmp_path)
                finally:
                    Path(tmp_path).unlink(missing_ok=True)
            except FileNotFoundError:
                messages.error(request, 'The uploaded file could not be processed. Please try again.')
                return redirect('index')
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('index')
            except Exception as e2:
                logger.exception('PDF extraction (with fallback) failed')
                messages.error(
                    request,
                    f'Could not read text from PDF. Error: {e2!s}. '
                    'If this is a scanned PDF, install Tesseract and poppler: brew install tesseract poppler'
                )
                return redirect('index')
        # If we got no text or very little, try OCR via temp file (scanned PDF).
        # We intentionally DO NOT swallow OCR errors, because scanned PDFs require
        # extra system dependencies (tesseract + poppler) and the user needs a clear message.
        if not extracted_text.strip() or len(extracted_text.strip()) < OCR_FALLBACK_THRESHOLD:
            try:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                try:
                    ocr_text = extract_resume_text(tmp_path)
                    if ocr_text and ocr_text.strip():
                        extracted_text = ocr_text
                finally:
                    Path(tmp_path).unlink(missing_ok=True)
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('index')
            except Exception as e:
                logger.exception('OCR extraction failed')
                messages.error(
                    request,
                    f'Could not extract text from scanned PDF. Error: {e!s}. '
                    'Install Tesseract and poppler: brew install tesseract poppler'
                )
                return redirect('index')
    else:
        try:
            extracted_text = content.decode('utf-8', errors='replace').strip() or content.decode('latin-1', errors='replace').strip()
        except Exception as e:
            messages.error(request, f'Could not read text file. Error: {e!s}')
            return redirect('index')

    if not extracted_text or not extracted_text.strip():
        messages.error(
            request,
            'No text could be extracted. Try a different file or a text-based PDF. '
            'For scanned PDFs, install: brew install tesseract poppler'
        )
        return redirect('index')

    # Save resume with file content and extracted text
    try:
        resume = UploadedResume(original_filename=name, extracted_text=extracted_text.strip())
        resume.save()  # save model first so file upload_to can use it
        resume.file.save(name, ContentFile(content), save=True)
    except Exception as e:
        logger.exception('Failed to save uploaded file')
        messages.error(request, f'Could not save file. Error: {e!s}')
        return redirect('index')

    # OpenAI API: wrap in try/except; on failure log, keep resume record, redirect to dashboard with error
    try:
        result = analyze_resume_with_ai(resume.extracted_text)
    except Exception:
        logger.exception('OpenAI API call failed')
        messages.error(
            request,
            'Analysis failed due to a server error. Your resume was saved; you can view it and try again later.'
        )
        return redirect('dashboard', analysis_id=resume.pk)

    resume.skills = result.get('detected_skills', [])
    resume.missing_skills = result.get('missing_skills', [])
    resume.suggested_roles = result.get('suggested_roles', [])
    resume.improvement_tips = result.get('improvement_tips', [])
    resume.save(update_fields=['skills', 'missing_skills', 'suggested_roles', 'improvement_tips'])

    if result.get('error'):
        messages.warning(
            request,
            f'Analysis completed with a warning: {result["error"]}'
        )
    else:
        messages.success(
            request,
            'Your resume was analyzed successfully. Review your results below.'
        )

    return redirect('dashboard', analysis_id=resume.pk)


def dashboard(request, analysis_id):
    """Analysis page: show results for one uploaded resume."""
    analysis = get_object_or_404(UploadedResume, pk=analysis_id)
    context = {
        'analysis': analysis,
        'skills': analysis.skills,
        'missing_skills': analysis.missing_skills,
        'suggested_roles': analysis.suggested_roles,
        'improvement_tips': analysis.improvement_tips,
    }
    return render(request, 'resume_analyzer/dashboard.html', context)


def analysis_list(request):
    """List all uploaded resumes / analyses."""
    analyses = UploadedResume.objects.all()[:50]
    return render(request, 'resume_analyzer/analysis_list.html', {'analyses': analyses})
