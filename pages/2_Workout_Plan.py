# pages/2_Workout_Plan.py
import streamlit as st

st.set_page_config(page_title="Workout Plan", page_icon="🏋", layout="wide")
st.title("🏋️ Workout Plan")

level = st.selectbox("Choose Level", ["Beginner", "Intermediate", "Advanced"], index=0)

# Structured plan: Warm-up, Strength, Cardio, Cool-down + Weekly split
PLANS = {
    "Beginner": {
        "Daily Template": {
            "Warm-up": "5–8 min brisk walk or easy cycle + dynamic stretches",
            "Strength (3x/week)": "Push-ups 3×8, Bodyweight Squats 3×12, Glute Bridge 3×12, Plank 3×30s",
            "Cardio (2–3x/week)": "15–20 min brisk walking / cycling",
            "Cool-down": "5 min easy stretching (hamstrings, quads, calves, shoulders)",
        },
        "Weekly Split": {
            "Mon": "Full-body strength",
            "Tue": "Cardio + mobility",
            "Wed": "Rest / walk",
            "Thu": "Full-body strength",
            "Fri": "Cardio",
            "Sat": "Full-body strength (light)",
            "Sun": "Rest / stretching",
        },
    },
    "Intermediate": {
        "Daily Template": {
            "Warm-up": "8–10 min jog + mobility (hips, shoulders)",
            "Strength (4x/week)": "Pull-ups 3×6–8, Lunges 3×12/leg, Bench/Push-ups 3×10, Plank 3×60s",
            "Cardio (2–3x/week)": "20–30 min run/cycle or intervals (6×1 min fast/1 min easy)",
            "Cool-down": "8–10 min stretching or yoga flow",
        },
        "Weekly Split": {
            "Mon": "Upper Strength (push/pull)",
            "Tue": "Cardio (intervals)",
            "Wed": "Lower Strength",
            "Thu": "Active recovery / yoga",
            "Fri": "Full-body Strength",
            "Sat": "Cardio (steady)",
            "Sun": "Rest",
        },
    },
    "Advanced": {
        "Daily Template": {
            "Warm-up": "10 min HIIT warm-up + activation",
            "Strength (4–5x/week)": "Deadlift 4×6, Bench 4×6–8, Row 4×8, Bulgarian Split Squat 3×10/leg",
            "Cardio (3x/week)": "30–40 min run/cycle or swim; OR HIIT 10×1 min hard / 1 min easy",
            "Cool-down": "10–12 min deep stretching + breathing",
        },
        "Weekly Split": {
            "Mon": "Push (chest/shoulders/triceps)",
            "Tue": "Pull (back/biceps)",
            "Wed": "Legs",
            "Thu": "Cardio / conditioning",
            "Fri": "Full-body Strength",
            "Sat": "Endurance (long easy run/cycle)",
            "Sun": "Rest",
        },
    },
}

plan = PLANS[level]

c1, c2 = st.columns(2)
with c1:
    st.subheader("📘 Daily Template")
    for k, v in plan["Daily Template"].items():
        st.markdown(f"**{k}:** {v}")

with c2:
    st.subheader("🗓️ Weekly Split")
    for day, sess in plan["Weekly Split"].items():
        st.write(f"- **{day}:** {sess}")

st.divider()
st.subheader("✅ Simple workout checklist for today")
if "work_done" not in st.session_state:
    st.session_state["work_done"] = {"Warm-up": False, "Strength": False, "Cardio": False, "Cool-down": False}

for key in list(st.session_state["work_done"].keys()):
    st.session_state["work_done"][key] = st.checkbox(key, value=st.session_state["work_done"][key])

completed = sum(1 for v in st.session_state["work_done"].values() if v)
st.progress(completed / 4)
st.write(f"Completed {completed}/4 blocks today")
