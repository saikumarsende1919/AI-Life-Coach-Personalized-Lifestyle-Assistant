import streamlit as st
from src.agent import Agent
from src.memory import Memory
import random
from typing import Dict, Any

# -----------------------------
# UTIL: Personalized Plan Generator
# -----------------------------
def generate_personalized_plans(snapshot: Dict[str, Any], agent_result: Dict[str, Any]) -> Dict[str, str]:
    """
    Create personalized short messages for each domain using snapshot values and agent outputs.
    Returns dictionary with keys: health, finance, learning, productivity -> short message strings.
    """
    plans = {}

    # ----- HEALTH -----
    health_snap = snapshot.get("health", {})
    steps = health_snap.get("steps_per_day", 0)
    sleep = health_snap.get("sleep_hours", 0)
    stress = health_snap.get("stress_level", "low")
    health_plan_list = agent_result.get("health", {}).get("plan", [])
    # Personalize
    health_msgs = []
    if steps and steps < 5000:
        health_msgs.append(f"Increase daily steps: you have {steps} steps — aim for +20% or a 20–30 min walk.")
    else:
        health_msgs.append(f"Your steps ({steps}) look decent — keep the routine.")
    if sleep and sleep < 7:
        health_msgs.append(f"Improve sleep: you average {sleep}h — aim for consistent 7–8h schedule.")
    if stress in ("high",):
        health_msgs.append("Stress is high — try short breathing breaks (3–5 min) twice daily.")
    if health_plan_list:
        health_msgs.append("Actions: " + " • ".join(health_plan_list[:3]))
    plans["health"] = " ".join(health_msgs) if health_msgs else agent_result.get("health", {}).get("message", "")

    # ----- FINANCE -----
    fin_snap = snapshot.get("finance", {})
    income = fin_snap.get("monthly_income", 0)
    expenses = fin_snap.get("monthly_expenses", 0)
    subs = fin_snap.get("subscriptions", [])
    fin_plan_list = agent_result.get("finance", {}).get("plan", [])
    fin_msgs = []
    if income and expenses:
        balance = income - expenses
        fin_msgs.append(f"Monthly balance: ₹{balance} ({'surplus' if balance>=0 else 'deficit'}).")
    if subs:
        fin_msgs.append(f"Subscriptions: {', '.join(subs)} — consider reviewing them.")
    if fin_plan_list:
        fin_msgs.append("Actions: " + " • ".join(fin_plan_list[:2]))
    plans["finance"] = " ".join(fin_msgs) if fin_msgs else agent_result.get("finance", {}).get("message", "")

    # ----- LEARNING -----
    learn_snap = snapshot.get("learning", {})
    study = learn_snap.get("study_minutes_daily", 0)
    skill = learn_snap.get("current_skill", "")
    learn_plan_list = agent_result.get("learning", {}).get("plan", [])
    learn_msgs = []
    if skill:
        learn_msgs.append(f"Skill: {skill}.")
    if study:
        learn_msgs.append(f"Study time: {study} min/day — try short focused sessions.")
    if learn_plan_list:
        learn_msgs.append("Actions: " + " • ".join(learn_plan_list[:2]))
    else:
        learn_msgs.append(agent_result.get("learning", {}).get("message", "Keep a consistent learning habit."))
    plans["learning"] = " ".join(learn_msgs)

    # ----- PRODUCTIVITY -----
    prod_snap = snapshot.get("productivity", {})
    tasks = prod_snap.get("tasks", [])
    completed = prod_snap.get("completed_today", 0)
    prod_plan = agent_result.get("productivity", {})
    prod_msgs = []
    if tasks:
        prod_msgs.append(f"You listed {len(tasks)} tasks; {completed} completed today.")
    if prod_plan.get("scheduled"):
        ev = prod_plan["scheduled"].get("event", {})
        prod_msgs.append(f"Scheduled: {ev.get('title','task')} at {ev.get('start','TBD')} ({ev.get('duration','TBD')} mins).")
    else:
        prod_msgs.append(prod_plan.get("message", "No tasks scheduled."))
    plans["productivity"] = " ".join(prod_msgs)

    return plans


# -----------------------------
# ENHANCED CHAT RESPONSE (CONTEXT-AWARE)
# -----------------------------
def generate_chat_response(message: str, snapshot: Dict[str, Any], agent_result: Dict[str, Any]) -> str:
    """
    Context-aware chat replies: uses the user's snapshot and agent result to form specific advice.
    Falls back to concise domain-driven guidance if message is generic.
    """
    msg = message.lower().strip()

    # CAREER / JOB
    if any(k in msg for k in ["job", "career", "interview", "resume", "dream job", "apply"]):
        reply = [
            "To get your target job: 1) Define the exact role and 2) tailor your resume to the JD (keywords & projects).",
            "Build one relevant project and put it on GitHub/portfolio that demonstrates required skills.",
            "Practice interview problems and behavioral stories. Apply consistently (3–5 roles/day).",
            "If you share your target role, I can suggest a 30-day plan (projects, skills, interview prep)."
        ]
        return random.choice(reply)

    # HEALTH QUESTIONS
    if any(k in msg for k in ["health", "sleep", "steps", "exercise", "fitness", "diet", "tired", "weight"]):
        health = snapshot.get("health", {})
        steps = health.get("steps_per_day", 0)
        sleep = health.get("sleep_hours", 0)
        suggestions = []
        if steps and steps < 5000:
            suggestions.append(f"Walk at least 20–30 minutes daily — you currently do {steps} steps.")
        if sleep and sleep < 7:
            suggestions.append(f"Improve sleep routine; aim for 7–8 hours (you average {sleep}h).")
        suggestions.append("Try short breathing or mindfulness (3–5 minutes) when stressed.")
        return " ".join(suggestions)

    # FINANCE QUESTIONS
    if any(k in msg for k in ["finance", "money", "salary", "expenses", "budget", "savings"]):
        fin = snapshot.get("finance", {})
        income = fin.get("monthly_income", 0)
        expenses = fin.get("monthly_expenses", 0)
        subs = fin.get("subscriptions", [])
        advice = []
        if income and expenses:
            bal = income - expenses
            advice.append(f"Your monthly balance is ₹{bal}.")
            if bal < 0:
                advice.append("You are spending more than you earn — prioritize reducing expenses or increasing income.")
        if subs:
            advice.append(f"Review subscriptions: {', '.join(subs)} — cancel ones you don't use.")
        advice.append("Track all expenses for 30 days to find quick savings.")
        return " ".join(advice)

    # LEARNING QUESTIONS
    if any(k in msg for k in ["learn", "study", "skill", "practice", "course"]):
        learning = snapshot.get("learning", {})
        study = learning.get("study_minutes_daily", 0)
        advice = []
        if study and study < 20:
            advice.append(f"You study {study} min/day — try 15–25 focused minutes using active recall.")
        advice.append("Use spaced repetition and build a 30-day mini-project aligned to your goal.")
        return " ".join(advice)

    # PRODUCTIVITY QUESTIONS
    if any(k in msg for k in ["task", "productivity", "focus", "routine", "todo"]):
        prod = snapshot.get("productivity", {})
        tasks = prod.get("tasks", [])
        completed = prod.get("completed_today", 0)
        advice = []
        advice.append(f"You have {len(tasks)} tasks; completed {completed} today.")
        advice.append("Try the Pomodoro technique (25min focus + 5min break) and pick 3 MITs daily.")
        return " ".join(advice)

    # GENERAL / DEFAULT
    return (
        "Good question — can you be a bit more specific? "
        "Tell me which area you want to improve (health, finance, learning, productivity, career)."
    )


# -----------------------------
# STREAMLIT UI
# -----------------------------
memory = Memory()
st.set_page_config(layout="wide", page_title="AI Life Coach")
st.markdown("""
<style>
.title-container {
    width: 100%;
    padding: 25px 20px;
    border-radius: 12px;
    background: linear-gradient(90deg, #007bff, #00c6ff);
    margin-top: -20px;
    margin-bottom: 20px;
}
.title-text {
    color: white;
    font-size: 38px;
    font-weight: 800;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="title-container">
    <h1 class="title-text">🧠 AI Life Coach – Personalized Lifestyle Assistant</h1>
</div>
""", unsafe_allow_html=True)

st.write("Improve your day-to-day life with tailored recommendations.")

# Two-column layout: left (inputs), right (cards)
left_col, right_col = st.columns([0.4, 0.6])

# Persist last snapshot and results in session state
if "last_snapshot" not in st.session_state:
    st.session_state["last_snapshot"] = None
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "personal_plans" not in st.session_state:
    st.session_state["personal_plans"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ------------- LEFT: Input Form -------------
with left_col:
    st.subheader("📋 Enter Your Daily Details")

    with st.form("user_form"):
        user_id = st.text_input("User ID", "user001")
        name = st.text_input("Name", "")

        st.markdown("### 💰 Finance")
        monthly_income = st.number_input("Monthly Income", value=0, min_value=0)
        monthly_expenses = st.number_input("Monthly Expenses", value=0, min_value=0)
        subscriptions = st.text_input("Subscriptions (comma separated)", "Netflix, Spotify")

        st.markdown("### 🏃 Health")
        steps = st.number_input("Steps per Day", value=0, min_value=0)
        sleep = st.number_input("Sleep Hours", value=0.0, min_value=0.0)
        water = st.number_input("Water Intake (liters)", value=0.0, min_value=0.0)
        stress = st.selectbox("Stress Level", ["low", "medium", "high"])

        st.markdown("### 📘 Learning")
        skill = st.text_input("Current Skill", "")
        study = st.number_input("Daily Study Minutes", value=0, min_value=0)
        goal = st.text_input("Learning Goal", "")

        st.markdown("### 📅 Productivity")
        tasks = st.text_input("Tasks (comma separated)", "study 30 min, walk, drink water")
        completed = st.number_input("Tasks Completed Today", value=0, min_value=0)

        submitted = st.form_submit_button("✨ Generate Recommendations")

# ------------- RIGHT: Beautiful Cards -------------
with right_col:
    st.subheader("🌟 Your Personalized Plans")

    if submitted:
        # build snapshot
        snapshot = {
            "user_id": user_id,
            "name": name,
            "finance": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "subscriptions": [s.strip() for s in subscriptions.split(",") if s.strip()]
            },
            "health": {
                "steps_per_day": steps,
                "sleep_hours": sleep,
                "water_intake_liters": water,
                "stress_level": stress,
            },
            "learning": {
                "current_skill": skill,
                "study_minutes_daily": study,
                "goal": goal
            },
            "productivity": {
                "tasks": [t.strip() for t in tasks.split(",") if t.strip()],
                "completed_today": completed
            }
        }

        # run agent logic (keeps your agent unchanged)
        agent = Agent(Memory())
        result = agent.run(snapshot)

        # generate personalized plan text from snapshot + agent result
        personal_plans = generate_personalized_plans(snapshot, result)

        # save to session for chat usage
        st.session_state["last_snapshot"] = snapshot
        st.session_state["last_result"] = result
        st.session_state["personal_plans"] = personal_plans

    # If we have plans (either freshly generated or earlier), show them
    plans_to_render = st.session_state.get("personal_plans", None)
    if plans_to_render:
        def card(title, content, bgcolor="#ffffff"):
            st.markdown(
                f"""
                <div style="
                    background:{bgcolor};
                    border-radius:12px;
                    padding:16px;
                    margin-bottom:12px;
                    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
                ">
                    <h3 style="margin:0 0 8px 0;">{title}</h3>
                    <div style="font-size:14px; color:#222;">{content}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        card("🏃 Health", plans_to_render.get("health", "—"), "#E8F5E9")
        card("💰 Finance", plans_to_render.get("finance", "—"), "#FFF3E0")
        card("📘 Learning", plans_to_render.get("learning", "—"), "#E3F2FD")
        card("📅 Productivity", plans_to_render.get("productivity", "—"), "#F3E5F5")

# -----------------------------
# BOTTOM: Chat Section (Full Width)
# -----------------------------
st.markdown("---")
st.subheader("💬 Chat with Your AI Life Coach")

# Input for chat (preserve snapshot/result in session)
chat_prompt = st.text_input("Ask something about your plans, or request a step-by-step action:")

if st.button("Send"):
    if chat_prompt.strip():
        # append user message
        st.session_state["chat_history"].append(("You", chat_prompt))

        # build context for chat from last snapshot/result if available
        snap = st.session_state.get("last_snapshot", {})
        res = st.session_state.get("last_result", {})

        # generate context-aware reply
        reply = generate_chat_response(chat_prompt, snap, res)
        st.session_state["chat_history"].append(("Coach", reply))

# show chat history
for sender, text in st.session_state["chat_history"]:
    if sender == "You":
        st.markdown(f"**You:** {text}")
    else:
        st.markdown(f"**Coach:** {text}")