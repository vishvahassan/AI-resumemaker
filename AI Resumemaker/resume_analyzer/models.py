from django.db import models


class UploadedResume(models.Model):
    """
    Django model for uploaded resume.
    - Accepts PDF and TXT files.
    - File is saved in the media folder: MEDIA_ROOT/resumes/YYYY/MM/DD/
    - After upload, analysis results (skills, suggestions, roles) are stored here.
    """

    # Upload: PDF or TXT — saved in media/resumes/%Y/%m/%d/
    file = models.FileField(upload_to='resumes/%Y/%m/%d/', help_text='PDF or TXT; stored in media folder')
    original_filename = models.CharField(max_length=255)

    # Extracted text and AI analysis results
    extracted_text = models.TextField(blank=True)
    skills = models.JSONField(default=list, help_text='Detected skills')
    missing_skills = models.JSONField(default=list, help_text='Suggested skills to add')
    suggested_roles = models.JSONField(default=list, help_text='Suitable job roles')
    improvement_tips = models.JSONField(default=list, help_text='Resume improvement tips from AI')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Uploaded resumes'

    def __str__(self):
        return self.original_filename
