# Home.py
import streamlit as st
import pandas as pd
import requests
from math import isfinite

st.set_page_config(page_title="Smart Diet Planner", layout="wide", page_icon="🥗")

# ------------------------- Helpers -------------------------
MEAL_SPLIT = {
    "Breakfast": 0.25,
    "Lunch": 0.35,
    "Snack": 0.15,
    "Dinner": 0.25,
}

SUGGESTIONS_VEG = {
    "Breakfast": "Oats with milk & fruits",
    "Lunch": "2 Chapati + Dal + Veg Curry + Salad",
    "Snack": "Sprouts / Fruit Salad",
    "Dinner": "Rice + Paneer Curry + Veg Sabji",
}

SUGGESTIONS_NONVEG = {
    "Breakfast": "Egg omelette + Bread + Milk",
    "Lunch": "Chicken Curry + Rice/Chapati + Salad",
    "Snack": "Boiled Eggs / Fruit Salad",
    "Dinner": "Fish Curry/Chicken + Rice + Veg Sabji",
}

def calculate_bmi(weight, height_cm):
    try:
        return round(weight / ((height_cm / 100) ** 2), 2)
    except ZeroDivisionError:
        return 0.0

def calorie_needs(weight, height, age, gender, activity):
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
    }
    return int(bmr * activity_multipliers[activity])

# ---------- Nutritionix API ----------
def get_nutrition(food_item: str):
    """
    Returns dict: Food, Calories, Protein (g), Carbs (g), Fat (g)
    Uses Nutritionix natural language endpoint (quantity supported, e.g. '100g paneer').
    """
    app_id = "95de49aa"
    api_key = "ff4c0256db383c287c19f7c0bcc8e798"
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {"x-app-id": app_id, "x-app-key": api_key}
    body = {"query": food_item}

    try:
        response = requests.post(url, headers=headers, json=body, timeout=15)
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None

    if response.status_code != 200:
        st.error(f"API Error: {response.status_code} — {response.text[:200]}")
        return None

    try:
        # You can log multiple items at once; we’ll sum them into a single entry
        foods = response.json().get("foods", [])
        if not foods:
            return None
        total = {"Food": [], "Calories": 0, "Protein (g)": 0.0, "Carbs (g)": 0.0, "Fat (g)": 0.0}
        for f in foods:
            total["Food"].append(f.get("food_name", "").title())
            total["Calories"] += round(float(f.get("nf_calories", 0)))
            total["Protein (g)"] += float(f.get("nf_protein", 0) or 0)
            total["Carbs (g)"] += float(f.get("nf_total_carbohydrate", 0) or 0)
            total["Fat (g)"] += float(f.get("nf_total_fat", 0) or 0)
        total["Protein (g)"] = round(total["Protein (g)"], 1)
        total["Carbs (g)"] = round(total["Carbs (g)"], 1)
        total["Fat (g)"] = round(total["Fat (g)"], 1)
        total["Food"] = ", ".join([x for x in total["Food"] if x])
        return total
    except Exception as e:
        st.error(f"Parsing error: {e}")
        return None

def init_plan(daily_calories: int, diet_type: str):
    """Create a fresh plan with targets and suggestions; consumed totals start at 0."""
    suggestions = SUGGESTIONS_VEG if diet_type == "Veg" else SUGGESTIONS_NONVEG
    plan = []
    for meal, share in MEAL_SPLIT.items():
        plan.append({
            "Meal": meal,
            "Suggested": suggestions[meal],
            "Foods": [],  # list of dict items (each with macros)
            "Chosen Foods": "",  # joined names for UI
            "Calories": 0,
            "Protein (g)": 0.0,
            "Carbs (g)": 0.0,
            "Fat (g)": 0.0,
            "Target (kcal)": int(round(daily_calories * share)),
        })
    return plan

def add_food_to_meal(plan: list, meal_name: str, food_entry: dict):
    """Append a food entry to selected meal and recompute totals."""
    for row in plan:
        if row["Meal"] == meal_name:
            row["Foods"].append(food_entry)
            # recompute totals
            row["Chosen Foods"] = ", ".join([f["Food"] for f in row["Foods"]])
            row["Calories"] = int(sum(f["Calories"] for f in row["Foods"]))
            row["Protein (g)"] = round(sum(f["Protein (g)"] for f in row["Foods"]), 1)
            row["Carbs (g)"] = round(sum(f["Carbs (g)"] for f in row["Foods"]), 1)
            row["Fat (g)"] = round(sum(f["Fat (g)"] for f in row["Foods"]), 1)
            return

def reset_today():
    for key in ("diet_plan", "daily_target", "diet_generated", "diet_done"):
        if key in st.session_state:
            del st.session_state[key]

# ------------------------- UI -------------------------
st.title("🥗 Smart Diet Planner — multi-item meals + live progress")

with st.sidebar:
    st.header("Your Details")
    name = st.text_input("Name", "User")
    age = st.number_input("Age", min_value=12, max_value=100, value=25)
    weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
    height = st.number_input("Height (cm)", min_value=120, max_value=220, value=170)
    gender = st.selectbox("Gender", ["Male", "Female"])
    activity = st.selectbox("Activity Level",
                            ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
    diet_type = st.radio("Diet Preference", ["Veg", "Non-Veg"], horizontal=True)

    colB1, colB2 = st.columns(2)
    with colB1:
        gen = st.button("Generate Plan", type="primary")
    with colB2:
        clr = st.button("Reset Today's Log")

if clr:
    reset_today()
    st.success("Cleared today's diet data.")

if gen:
    bmi = calculate_bmi(weight, height)
    calories = calorie_needs(weight, height, age, gender, activity)
    st.session_state["daily_target"] = calories
    st.session_state["diet_plan"] = init_plan(calories, diet_type)
    st.session_state["diet_generated"] = True

# -------- Health Summary --------
st.subheader("📊 Health Summary")
if "daily_target" in st.session_state:
    bmi_val = calculate_bmi(weight, height)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Name", name)
    c2.metric("BMI", bmi_val)
    c3.metric("Daily Target (kcal)", st.session_state["daily_target"])
    water_goal_l = round(weight * 0.05, 2)  # 0.05 L per kg
    c4.metric("Water Goal (L/day)", water_goal_l)

# -------- Plan Table + Progress --------
if "diet_plan" in st.session_state:
    st.subheader("🍽 Your Diet Plan (Live & Interactive)")
    # Display table
    df = pd.DataFrame([{
        "Meal": r["Meal"],
        "Suggested": r["Suggested"],
        "Chosen Foods": r["Chosen Foods"] if r["Chosen Foods"] else "—",
        "Calories": r["Calories"],
        "Protein (g)": r["Protein (g)"],
        "Carbs (g)": r["Carbs (g)"],
        "Fat (g)": r["Fat (g)"],
        "Target (kcal)": r["Target (kcal)"],
    } for r in st.session_state["diet_plan"]])
    st.dataframe(df, use_container_width=True)

    st.markdown("**Per-meal progress** (current kcal vs target kcal):")
    for row in st.session_state["diet_plan"]:
        current = row["Calories"]
        target = max(row["Target (kcal)"], 1)
        pct = max(0.0, min(current / target, 1.0))
        st.write(f"**{row['Meal']}** — {current} / {target} kcal")
        st.progress(pct)

    # Daily progress
    total_current = int(sum(r["Calories"] for r in st.session_state["diet_plan"]))
    total_target = int(st.session_state.get("daily_target", 1))
    st.subheader("📈 Daily Progress")
    st.write(f"Total consumed: **{total_current} / {total_target} kcal**")
    st.progress(max(0.0, min(total_current / max(total_target, 1), 1.0)))

# -------- Add Foods --------
st.subheader("📝 Add foods (supports multiple items & quantities)")
st.caption("Tip: You can enter multiple foods at once, e.g. `100g paneer and 1 banana and 40g oats`.")

cadd1, cadd2 = st.columns([2, 1])
with cadd1:
    food_input = st.text_input("What did you eat?", placeholder="e.g., 150g paneer and 1 apple and 40g oats")
with cadd2:
    meal_choice = st.selectbox("For which meal?", list(MEAL_SPLIT.keys()))

add_clicked = st.button("Add to Diet Plan", type="primary")

if add_clicked:
    if "diet_plan" not in st.session_state:
        st.warning("Generate your diet plan first from the sidebar.")
    else:
        result = get_nutrition(food_input.strip())
        if result:
            add_food_to_meal(st.session_state["diet_plan"], meal_choice, result)
            st.success(f"Added to **{meal_choice}**: {result['Food']} ({result['Calories']} kcal)")
        else:
            st.warning("Couldn't recognize that food. Please try a simpler description.")

# -------- Remove last item (per meal) --------
st.divider()
st.subheader("🧹 Undo / Remove last food (optional)")
rc1, rc2 = st.columns([1, 1])
with rc1:
    rem_meal = st.selectbox("Select meal", list(MEAL_SPLIT.keys()), key="rem_meal")
with rc2:
    rem = st.button("Remove last food from selected meal")
if rem and "diet_plan" in st.session_state:
    for row in st.session_state["diet_plan"]:
        if row["Meal"] == st.session_state["rem_meal"] and row["Foods"]:
            removed = row["Foods"].pop()
            # recompute
            row["Chosen Foods"] = ", ".join([f["Food"] for f in row["Foods"]]) if row["Foods"] else ""
            row["Calories"] = int(sum(f["Calories"] for f in row["Foods"])) if row["Foods"] else 0
            row["Protein (g)"] = round(sum(f["Protein (g)"] for f in row["Foods"]), 1) if row["Foods"] else 0.0
            row["Carbs (g)"] = round(sum(f["Carbs (g)"] for f in row["Foods"]), 1) if row["Foods"] else 0.0
            row["Fat (g)"] = round(sum(f["Fat (g)"] for f in row["Foods"]), 1) if row["Foods"] else 0.0
            st.info(f"Removed **{removed['Food']}** from **{row['Meal']}**")
            break

# Footer
st.caption("Built with ♥ Streamlit · Nutrition data by Nutritionix")
    