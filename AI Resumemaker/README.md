# AI Resume Analyzer

A full-stack Django web application that analyzes resumes using the OpenAI API. Upload a PDF or text resume and get AI-generated insights: detected skills, suggested skills to add, suitable job roles, and resume improvement tips.

---

## Project Overview

AI Resume Analyzer lets users upload a resume (PDF or TXT), extracts the text, sends it to the OpenAI API, and displays structured results on a clean dashboard. It supports both text-based PDFs and **scanned/image-based PDFs** via an OCR fallback (pytesseract + pdf2image). The project includes strong error handling, success messages, and a mobile-responsive UI suitable for production use.

---

## Feature List

- **Landing page** — Hero section, feature highlights, and clear call-to-action
- **Resume upload** — PDF and .txt only; file size limit 5 MB with clear validation messages
- **Text extraction** — From PDF (pdfplumber, PyPDF2, pypdf) and plain text files; **OCR support for scanned resumes** (image-based PDFs) via pdf2image + pytesseract
- **AI analysis results** — Detected skills, missing skills, suggested job roles, resume improvement tips
- **Dashboard** — Clean view of all analysis results by section
- **Error handling** — File type/size validation, extraction and API errors with user-friendly messages
- **Success messages** — Confirmation after successful analysis (Django messages: success, warning, error)
- **Mobile responsive UI** — Works on phones and tablets

---

## Tech Stack

| Technology  | Purpose                |
|------------|------------------------|
| Python     | Backend language       |
| Django     | Web framework          |
| SQLite     | Database               |
| OpenAI     | AI analysis API        |
| pdfplumber | PDF text extraction    |
| PyPDF2     | PDF text extraction    |
| pypdf      | PDF text extraction    |

---

## Project Folder Structure

```
AI Resumemaker/
├── manage.py
├── requirements.txt
├── README.md
├── DEPLOYMENT.md
├── .env.example
├── .gitignore
├── db.sqlite3              # Created after migrate
├── media/                  # Uploaded resume files
│   └── resumes/
├── static/
│   └── css/
│       ├── style.css
│       └── dashboard.css
├── templates/
│   └── base.html
├── ai_resume_analyzer/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── resume_analyzer/
    ├── __init__.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── services/
    │   ├── __init__.py
    │   ├── text_extraction.py
    │   └── openai_service.py
    └── templates/resume_analyzer/
        ├── index.html
        ├── dashboard.html
        └── analysis_list.html
```

---

## Prerequisites

- **Python 3.10+**
- **OpenAI API key** — [Create one](https://platform.openai.com/api-keys)
- **For scanned PDF / OCR:** [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and [poppler](https://poppler.freedesktop.org/) installed on your system (e.g. `brew install tesseract poppler` on macOS). Normal text-based PDFs work without these.

---

## How to Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-resume-analyzer.git
   cd ai-resume-analyzer
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add OPENAI_API_KEY in .env**
   ```bash
   cp .env.example .env
   # Edit .env and set: OPENAI_API_KEY=your_api_key_here
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Open in browser**
   Navigate to **http://127.0.0.1:8000/**

---

## Environment Variables

| Variable         | Required | Description                                      |
|-----------------|----------|--------------------------------------------------|
| `OPENAI_API_KEY` | Yes      | Your OpenAI API key for AI analysis.            |

**Never commit secrets.** Keep `.env` out of version control (it is in `.gitignore`). Use `.env.example` as a template only; production should use the host’s environment or secrets manager.

---

## Deployment

For production:

- Set **DEBUG** to `False` (e.g. via `DJANGO_DEBUG=False`).
- Set **SECRET_KEY** from environment (e.g. `DJANGO_SECRET_KEY`).
- Set **ALLOWED_HOSTS** to your domain(s) (e.g. `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`).
- **Static files:** Run `python manage.py collectstatic` and serve via your web server or CDN.
- **Database:** SQLite is fine for small scale; use PostgreSQL for production at scale.
- **WSGI:** Use `gunicorn ai_resume_analyzer.wsgi:application` (or your platform’s equivalent).

See **DEPLOYMENT.md** for a full deployment guide and security checklist.

---

## License

MIT License. Use and modify as you like.

---

## Contributing

1. Fork the repository.
2. Create a feature branch and make your changes.
3. Run tests if applicable.
4. Open a pull request with a clear description of the change.
