import streamlit as st

st.title("💡 Health Tips")

tips = [
    "Eat more vegetables and fruits daily 🍎🥦",
    "Drink at least 2-3 liters of water 💧",
    "Avoid junk food & sugary drinks ❌",
    "Sleep 7-8 hours daily 😴",
    "Exercise at least 30 minutes daily 🏃‍♂️",
    "Take short breaks when sitting long hours 💻",
    "Practice meditation or breathing exercises 🧘"
    "Complete your protien-intake daily without fail"
]

st.subheader("✅ Daily Health Tips")
for t in tips:
    st.write("- ", t)
