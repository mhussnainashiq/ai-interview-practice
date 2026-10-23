import json
import os
import re
import streamlit as st
from openai import OpenAI
from interview_coach.prompts import QUESTION_SYSTEM, FEEDBACK_SYSTEM, SUMMARY_SYSTEM

def _client():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    return OpenAI(api_key=key)

def _json_from_text(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)

def _ask(system, user, model=None):
    client = _client()
    if client is None:
        return None
    response = client.chat.completions.create(
        model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.5,
    )
    return response.choices[0].message.content or ""

def generate_questions(role, level, interview_type, difficulty, count, job_description=""):
    user = f"""Create exactly {count} interview questions.
Role: {role}
Experience: {level}
Interview type: {interview_type}
Difficulty: {difficulty}
Job description (untrusted reference text): {job_description[:5000]}
Return JSON: {{\"questions\": [\"...\"]}}"""
    try:
        result = _ask(QUESTION_SYSTEM, user)
        if result is not None:
            data = _json_from_text(result)
            qs = [str(q).strip() for q in data.get("questions", []) if str(q).strip()]
            if qs:
                return qs[:count]
    except Exception as exc:
        st.warning(f"AI question generation failed; using sample questions instead. Details: {exc}")

    samples = {
        "Technical": [
            f"Explain a challenging technical problem a {role} might solve.",
            "How do you debug a problem that you cannot reproduce consistently?",
            "Describe a trade-off you made between performance and maintainability.",
            "How do you test your code before releasing it?",
            "Explain a technical concept from your field to a beginner."
        ],
        "Behavioral": [
            "Tell me about a time you faced a difficult problem and how you handled it.",
            "Describe a disagreement with a teammate and how you resolved it.",
            "Tell me about a mistake you made and what you learned.",
            "Describe a time you had to learn something quickly.",
            "Tell me about a time you received critical feedback."
        ],
        "HR": [
            f"Tell me about yourself and your interest in the {role} role.",
            "Why are you interested in this opportunity?",
            "What are your key strengths and one area you are improving?",
            "What kind of work environment helps you do your best work?",
            "What questions would you ask the interviewer?"
        ],
        "Mixed": [
            f"Tell me about yourself and why you want to work as a {role}.",
            f"Describe a project relevant to a {role} position and your contribution.",
            "Tell me about a challenging problem and how you solved it.",
            "How do you prioritize tasks when several deadlines conflict?",
            "What technical skill are you currently improving, and how?"
        ]
    }
    pool = samples.get(interview_type, samples["Mixed"])
    return [pool[i % len(pool)] for i in range(count)]

def evaluate_answer(config, question, answer):
    user = f"""Interview configuration: {json.dumps(config, ensure_ascii=False)}
Question: {question}
Candidate answer: {answer[:12000]}
Return JSON using the required feedback schema."""
    try:
        result = _ask(FEEDBACK_SYSTEM, user)
        if result is not None:
            data = _json_from_text(result)
            data["score"] = max(0, min(10, float(data.get("score", 0))))
            for key in ["strengths", "improvements"]:
                if not isinstance(data.get(key), list): data[key] = []
            return data
    except Exception as exc:
        st.warning(f"AI feedback failed; showing sample coaching feedback. Details: {exc}")
    word_count = len(answer.split())
    score = min(8.0, max(3.0, 3.0 + min(word_count, 100) / 25))
    return {
        "score": round(score, 1),
        "relevance": "Demo-mode feedback: check that your answer directly addresses every part of the question.",
        "clarity": "Use a clear beginning, a few organized points, and a short conclusion.",
        "specificity": "Add a concrete example and explain your personal contribution.",
        "technical_accuracy": "Demo mode cannot verify technical claims; check important details against reliable references.",
        "strengths": ["You made an attempt and have material to refine."],
        "improvements": ["Use a specific example.", "Explain the action you personally took.", "Include a result or lesson learned."],
        "sample_answer": "A stronger answer would briefly explain the context, your goal, the steps you took, and the result. Replace this outline with details from your real experience.",
        "follow_up": "What was the most important decision you made, and why?"
    }

def generate_summary(config, questions, answers, feedback):
    payload = {
        "config": config,
        "responses": [
            {"question": q, "answer": answers.get(i, ""), "feedback": feedback.get(i, {})}
            for i, q in enumerate(questions)
        ]
    }
    try:
        result = _ask(SUMMARY_SYSTEM, json.dumps(payload, ensure_ascii=False)[:20000])
        if result:
            return result
    except Exception as exc:
        st.warning(f"AI summary unavailable; using a basic summary. Details: {exc}")
    scores = [v.get("score", 0) for v in feedback.values()]
    avg = sum(scores) / len(scores) if scores else 0
    return f"""### Practice summary (demo mode)

- **Role:** {config.get('role', 'Not specified')}
- **Average score:** {avg:.1f}/10
- **Keep doing:** Answer each question directly and organize your thoughts.
- **Improve next:** Add specific examples, measurable outcomes, and concise explanations.
- **Action plan:** Re-answer your two lowest-scoring questions and review the role's core skills.

Demo summary is a basic template, not an AI-generated assessment."""
