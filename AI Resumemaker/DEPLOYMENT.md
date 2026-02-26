# Deployment Guide

Use this guide to deploy AI Resume Analyzer to production (e.g. Railway, Render, Heroku, or a VPS).

---

## Environment Variables

Set these in your hosting dashboard or on the server:

| Variable            | Example                    | Notes                                      |
|---------------------|----------------------------|--------------------------------------------|
| `DJANGO_SECRET_KEY` | `your-long-random-secret` | Generate with Django’s `get_random_secret_key()` |
| `DJANGO_DEBUG`      | `False`                    | Must be `False` in production              |
| `ALLOWED_HOSTS`     | `yourdomain.com,www.yourdomain.com` | Comma-separated, no spaces        |
| `OPENAI_API_KEY`    | `sk-...`                   | Your OpenAI API key                        |

---

## Gunicorn Setup

Install Gunicorn:

```bash
pip install gunicorn
```

Run the WSGI application:

```bash
gunicorn ai_resume_analyzer.wsgi:application --bind 0.0.0.0:8000
```

For production, run behind a reverse proxy (e.g. Nginx) and use a process manager (e.g. systemd, Supervisor) or your platform’s recommended method.

---

## Collect Static Files

Before going live, collect static files so the web server can serve them:

```bash
python manage.py collectstatic --noinput
```

Configure your web server or CDN to serve the contents of the `STATIC_ROOT` directory (set in `settings.py` for production if needed).

---

## Security Checklist

- [ ] `DEBUG = False` (e.g. `DJANGO_DEBUG=False`)
- [ ] `SECRET_KEY` from environment (`DJANGO_SECRET_KEY`)
- [ ] `ALLOWED_HOSTS` set to your domain(s)
- [ ] `OPENAI_API_KEY` and other secrets never committed to version control
- [ ] HTTPS enabled at the reverse proxy / load balancer
- [ ] Static files collected and served securely
