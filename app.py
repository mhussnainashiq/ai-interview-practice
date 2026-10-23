import streamlit as st
from interview_coach.ai_service import generate_questions, evaluate_answer, generate_summary
from interview_coach.storage import load_history, save_session, clear_history
from interview_coach.utils import average_score

st.set_page_config(page_title="Interview Coach AI", page_icon="🎤", layout="wide")

if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "session_config" not in st.session_state:
    st.session_state.session_config = {}
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

st.title("🎤 Interview Coach AI")
st.caption("Practice interviews, get useful feedback, and build stronger answers.")
st.info("AI feedback is for practice only and may be inaccurate. Your submitted answers may be sent to the configured AI provider. Do not include sensitive personal information.")

with st.sidebar:
    st.header("Set up your interview")
    role = st.selectbox("Job role", [
        "Python Developer", "Frontend Developer", "Full-Stack Developer",
        "Data Analyst", "Machine Learning Engineer", "Software Engineer",
        "Product Manager", "Customer Support", "Custom role"
    ])
    if role == "Custom role":
        role = st.text_input("Enter job role", "Backend Developer")
    level = st.selectbox("Experience level", ["Entry-level", "Junior", "Mid-level", "Senior"])
    interview_type = st.selectbox("Interview type", ["Mixed", "Technical", "Behavioral", "HR"])
    difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"], value="Medium")
    count = st.slider("Number of questions", 3, 10, 5)
    job_description = st.text_area("Job description (optional)", height=100)
    start = st.button("✨ Start new interview", type="primary", use_container_width=True)

if start:
    with st.spinner("Preparing your interview questions..."):
        qs = generate_questions(role, level, interview_type, difficulty, count, job_description)
    st.session_state.questions = qs
    st.session_state.answers = {}
    st.session_state.feedback = {}
    st.session_state.current_index = 0
    st.session_state.session_config = {
        "role": role, "level": level, "type": interview_type,
        "difficulty": difficulty, "job_description": job_description
    }

if not st.session_state.questions:
    st.markdown("""
    ### How it works
    1. Choose your target role and interview settings in the sidebar.
    2. Answer one question at a time.
    3. Get coaching feedback and a stronger sample answer.
    4. Review your session summary and practice again.

    **Voice input:** This version supports typed answers out of the box. Voice recording/transcription is left optional because browser and deployment support varies; you can paste a transcription into the answer box.
    """)
    st.subheader("Recent sessions")
    history = load_history()
    if not history:
        st.caption("No saved sessions yet.")
    else:
        for item in reversed(history[-5:]):
            st.write(f"**{item.get('role', 'Interview')}** — {item.get('date', '')} — Score: {item.get('score', 'N/A')}/10")
else:
    questions = st.session_state.questions
    idx = st.session_state.current_index
    if len(st.session_state.feedback) == len(questions):
        st.success("Interview completed!")
        scores = [v.get("score", 0) for v in st.session_state.feedback.values()]
        st.metric("Average coaching score", f"{average_score(scores):.1f}/10")
        if st.button("Generate session summary"):
            with st.spinner("Reviewing your performance..."):
                summary = generate_summary(st.session_state.session_config, questions, st.session_state.answers, st.session_state.feedback)
            st.session_state.final_summary = summary
        if "final_summary" in st.session_state:
            st.markdown(st.session_state.final_summary)
        if st.button("Save session to history"):
            session = {
                **st.session_state.session_config,
                "questions": questions,
                "answers": st.session_state.answers,
                "feedback": st.session_state.feedback,
                "score": round(average_score(scores), 1)
            }
            save_session(session)
            st.success("Session saved locally.")
        if st.button("Start over"):
            for key in ["questions", "answers", "feedback", "session_config", "final_summary"]:
                st.session_state.pop(key, None)
            st.session_state.current_index = 0
            st.rerun()
    else:
        st.progress((idx + 1) / len(questions), text=f"Question {idx + 1} of {len(questions)}")
        st.subheader(questions[idx])
        answer_key = f"answer_{idx}"
        current_answer = st.text_area(
            "Your answer",
            value=st.session_state.answers.get(idx, ""),
            key=answer_key,
            height=220,
            placeholder="Type your answer here. For a behavioral question, try Situation, Task, Action, Result (STAR)."
        )
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("Previous", disabled=idx == 0, use_container_width=True):
                st.session_state.current_index -= 1
                st.rerun()
        with c2:
            if st.button("Get feedback", type="primary", use_container_width=True):
                if not current_answer.strip():
                    st.warning("Please enter an answer before requesting feedback.")
                else:
                    st.session_state.answers[idx] = current_answer.strip()
                    with st.spinner("Evaluating your answer..."):
                        st.session_state.feedback[idx] = evaluate_answer(
                            st.session_state.session_config, questions[idx], current_answer.strip()
                        )
                    st.rerun()
        with c3:
            if idx < len(questions) - 1 and st.button("Next question", use_container_width=True):
                st.session_state.answers[idx] = current_answer.strip()
                st.session_state.current_index += 1
                st.rerun()

        if idx in st.session_state.feedback:
            fb = st.session_state.feedback[idx]
            st.divider()
            st.subheader("Your coaching feedback")
            st.metric("Approximate coaching score", f"{fb.get('score', 0)}/10")
            st.write(f"**Relevance:** {fb.get('relevance', 'N/A')}")
            st.write(f"**Clarity and structure:** {fb.get('clarity', 'N/A')}")
            st.write(f"**Specificity and examples:** {fb.get('specificity', 'N/A')}")
            st.write(f"**Technical accuracy:** {fb.get('technical_accuracy', 'N/A')}")
            st.markdown("**What you did well**")
            for x in fb.get("strengths", []): st.write(f"- {x}")
            st.markdown("**What to improve**")
            for x in fb.get("improvements", []): st.write(f"- {x}")
            st.markdown("**Suggested stronger answer**")
            st.write(fb.get("sample_answer", "Try to answer directly and include a specific example."))
            st.markdown("**Follow-up question**")
            st.write(fb.get("follow_up", "Can you give a practical example?"))
            if st.button("Continue to next question", key=f"continue_{idx}", use_container_width=True):
                if idx < len(questions) - 1:
                    st.session_state.current_index += 1
                else:
                    st.session_state.current_index = len(questions)
                st.rerun()
