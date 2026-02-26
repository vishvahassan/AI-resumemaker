"""
OpenAI API integration for resume analysis.

API key: set OPENAI_API_KEY in the environment (never commit it to code).
See README or .env.example for secure setup.
"""

import json
import os
import re


def _get_api_key() -> str | None:
    """Read OpenAI API key from environment. Prefer OPENAI_API_KEY."""
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY") or None


def analyze_resume_with_ai(resume_text: str) -> dict:
    """
    Analyze resume text using the OpenAI API and return structured JSON.

    The AI returns:
    1. detected_skills   — list of skills identified in the resume
    2. missing_skills   — suggested skills the candidate could add
    3. suggested_roles  — suitable job roles for the candidate
    4. improvement_tips — resume improvement tips (actionable advice)

    API key must be set in the environment: OPENAI_API_KEY.

    Args:
        resume_text: Raw text extracted from the resume.

    Returns:
        Dict with keys: detected_skills, missing_skills, suggested_roles, improvement_tips.
        On error, includes an "error" key and empty lists where applicable.
    """
    api_key = _get_api_key()
    if not api_key:
        return {
            "detected_skills": [],
            "missing_skills": [],
            "suggested_roles": [],
            "improvement_tips": [
                "Set OPENAI_API_KEY in your environment to enable AI analysis.",
            ],
            "error": "OPENAI_API_KEY not set",
        }

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except ImportError:
        return {
            "detected_skills": [],
            "missing_skills": [],
            "suggested_roles": [],
            "improvement_tips": ["Install the openai package: pip install openai"],
            "error": "openai package not installed",
        }

    system_prompt = """You are an expert resume analyst and career advisor. Your task is to analyze resume text and respond with a single valid JSON object—no markdown, no code fences, no extra text.

Your response must be parseable by json.loads() and contain exactly these four keys:
- "detected_skills": array of strings — skills clearly present or implied in the resume (technical, soft, tools, languages).
- "missing_skills": array of strings — 3–5 skills the candidate could add to strengthen their profile for their likely target roles.
- "suggested_roles": array of strings — 3–5 job titles that fit this candidate's experience and skills.
- "improvement_tips": array of strings — 3–5 specific, actionable tips to improve the resume (e.g., quantify achievements, add keywords, clarify role, fix formatting). Each tip should be one short sentence.

Be concise and professional. Output only the JSON object."""

    user_prompt = """Analyze the following resume text and return the JSON object with detected_skills, missing_skills, suggested_roles, and improvement_tips.

Resume text:
---
"""
    text_snippet = (resume_text[:14000] or "No content provided.").strip()
    user_prompt += text_snippet + "\n---"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        raw = (response.choices[0].message.content or "").strip()

        # Strip markdown code block if present
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```\s*$", "", raw)
        data = json.loads(raw)

        return {
            "detected_skills": data.get("detected_skills", []) or data.get("skills", []),
            "missing_skills": data.get("missing_skills", []),
            "suggested_roles": data.get("suggested_roles", []),
            "improvement_tips": data.get("improvement_tips", []),
        }
    except json.JSONDecodeError as e:
        return {
            "detected_skills": [],
            "missing_skills": [],
            "suggested_roles": [],
            "improvement_tips": [],
            "error": f"Invalid JSON from API: {e}",
        }
    except Exception as e:
        return {
            "detected_skills": [],
            "missing_skills": [],
            "suggested_roles": [],
            "improvement_tips": [],
            "error": str(e),
        }


def analyze_resume_with_openai(resume_text: str) -> dict:
    """
    Legacy alias: same as analyze_resume_with_ai but returns keys
    skills / missing_skills / suggested_roles for backward compatibility.
    """
    result = analyze_resume_with_ai(resume_text)
    return {
        "skills": result.get("detected_skills", []),
        "missing_skills": result.get("missing_skills", []),
        "suggested_roles": result.get("suggested_roles", []),
        "improvement_tips": result.get("improvement_tips", []),
        "error": result.get("error"),
    }
