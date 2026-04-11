import json
from groq import Groq
from Backend.app.core.config import settings


def get_groq_client() -> Groq:
    return Groq(api_key=settings.GROQ_API_KEY)


# ── Main Screening Function ────────────────────────────────────────────────────
async def screen_resume(
    resume_text: str,
    job_description: str,
    required_skills: str
) -> tuple[int, str]:
    """
    Screens a resume against a job description using Groq (Llama3).
    Returns: (score: int 0-100, feedback: str)
    """
    if not settings.GROQ_API_KEY:
        print("GROQ_API_KEY not set — skipping AI screening")
        return None, None

    if not resume_text or len(resume_text.strip()) < 50:
        return None, "Resume text too short to analyze."

    prompt = f"""You are an expert HR recruiter and resume evaluator.

Analyze the candidate resume against the job description and required skills.
Give an honest match score from 0 to 100.

JOB DESCRIPTION:
{job_description[:1500]}

REQUIRED SKILLS:
{required_skills}

CANDIDATE RESUME:
{resume_text[:2000]}

Respond ONLY in this exact JSON format (no extra text, no markdown):
{{
  "score": <integer between 0 and 100>,
  "strengths": "<one sentence about what matches well>",
  "gaps": "<one sentence about what is missing>",
  "recommendation": "<one of: Strong Match, Good Match, Moderate Match, Weak Match>",
  "feedback": "<2-3 sentences combining strengths and gaps for the recruiter>"
}}"""

    try:
        client = get_groq_client()

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert HR recruiter. Always respond only in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=400,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if Groq adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)

        score    = int(result.get("score", 0))
        feedback = result.get("feedback", "")

        # Clamp score between 0 and 100
        score = max(0, min(100, score))

        return score, feedback

    except json.JSONDecodeError as e:
        print(f"Groq JSON parse error: {e}")
        return None, "AI screening failed — invalid response format."

    except Exception as e:
        print(f"Groq API error: {e}")
        return None, "AI screening temporarily unavailable."


# ── Detailed Analysis (Recruiter dashboard) ────────────────────────────────────
async def get_detailed_analysis(
    resume_text: str,
    job_description: str,
    required_skills: str
) -> dict:
    """
    Returns full detailed analysis for recruiter dashboard.
    """
    if not settings.GROQ_API_KEY:
        return {}

    prompt = f"""You are a senior HR recruiter. Give a detailed evaluation.

JOB DESCRIPTION:
{job_description[:1500]}

REQUIRED SKILLS:
{required_skills}

RESUME:
{resume_text[:2000]}

Respond ONLY in this exact JSON format:
{{
  "score": <0-100>,
  "recommendation": "<Strong Match | Good Match | Moderate Match | Weak Match>",
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "experience_match": "<Exceeds | Meets | Below> requirements",
  "strengths": "<2 sentences>",
  "gaps": "<2 sentences>",
  "interview_questions": ["question1", "question2", "question3"]
}}"""

    try:
        client = get_groq_client()

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior HR recruiter. Respond only in valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=700,
        )

        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        return json.loads(raw)

    except Exception as e:
        print(f"Detailed analysis error: {e}")
        return {}
    
def get_recommendation(score: int) -> str:
    if score >= 80: return "Strong Match"
    elif score >= 60: return "Good Match"
    elif score >= 40: return "Moderate Match"
    else: return "Weak Match"