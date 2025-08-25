import streamlit as st

st.title("💧 Water Reminder")

weight = st.number_input("Enter your weight (kg)", 30, 200, 60)
water_need = round(weight * 0.05, 2)  # 0.05 L per kg
st.write(f"👉 You should drink about **{water_need:.2f} liters** of water daily.")

if "water" not in st.session_state:
    st.session_state["water"] = 0.0

add = st.number_input("Add water intake (liters)", 0.0, 1.0, 0.25, step=0.25)
if st.button("Log Water"):
    st.session_state["water"] += add

st.subheader("📊 Water Intake Summary")
st.write(f"Total water consumed today: **{st.session_state['water']:.2f} liters**")

progress = min(st.session_state["water"] / water_need, 1.0)
st.progress(progress)
