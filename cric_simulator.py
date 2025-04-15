import streamlit as st

# ✅ Set Streamlit Page Config
st.set_page_config(page_title="Cric Simulator", page_icon="🏏")

# --- Light Blue Theme Styling ---
st.markdown("""
<style>
body, .stApp {
    background-color: #e0f2fe;
}
h1 {
    color: #1D4ED8;
    font-family: 'Segoe UI Black', sans-serif;
}
label {
    color: #1E3A8A !important;
    font-weight: bold;
}
div[data-testid="metric-container"] {
    background-color: #ffffff;
    border: 2px solid #60A5FA;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    margin-top: 10px;
    margin-bottom: 10px;
}
div[data-testid="stMetricDelta"] {
    font-size: 1.1rem;
    font-weight: bold;
}
hr {
    border: none;
    height: 2px;
    background: linear-gradient(to right, #60A5FA, #3B82F6);
    margin-top: 2rem;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🏏 **Cric Simulator**")
st.markdown("""
Simulate your run chase with dynamic projections based on overs and wickets.  
No guesswork, just match-style logic 📊
""")

# --- Smart Par Score Logic ---
def cric_par_score(current_over, current_wickets, target_score):
    average_target = 180
    difficulty_boost = min((target_score - average_target) / 10 * 0.02, 0.10) if target_score > average_target else 0

    if current_over <= 6:
        progress_percent = (current_over / 6) * (0.293 + difficulty_boost)
    elif current_over <= 10:
        progress_percent = 0.293 + ((current_over - 6) / 4) * ((0.503 + difficulty_boost) - 0.293)
    elif current_over <= 15:
        progress_percent = 0.503 + ((current_over - 10) / 5) * ((0.706 + difficulty_boost) - 0.503)
    else:
        progress_percent = 0.706 + ((current_over - 15) / 5) * ((1.0 + difficulty_boost) - 0.706)

    base_score = target_score * progress_percent

    ideal_wickets = current_over / 5
    extra_wickets = max(0, current_wickets - ideal_wickets)

    if current_over <= 6:
        over_weight = 0.8
    elif current_over <= 10:
        over_weight = 1.0
    elif current_over <= 15:
        over_weight = 1.2
    else:
        over_weight = 1.5

    wicket_penalty = extra_wickets * over_weight * 4.5
    par = round(base_score + wicket_penalty)
    return min(par, target_score)

# --- User Inputs ---
st.markdown("### 🎯 Match Scenario")
target = st.number_input("Target Score", min_value=50, max_value=300, value=222)
current_over = st.slider("Overs Completed", min_value=1, max_value=20, value=5)
wickets = st.slider("Wickets Lost", min_value=0, max_value=10, value=3)
actual_score = st.number_input("Your Current Score", min_value=0, max_value=target, value=40)

# --- Current Status ---
par = cric_par_score(current_over, wickets, target)
diff = actual_score - par
status = "✅ Ahead" if diff >= 0 else "❌ Behind"

st.markdown("### 📍 Required Score")
st.subheader(f"Par Score at {current_over} overs, {wickets} wickets: **{par}**")
st.metric(label="Your Progress", value=f"{actual_score} ({'+' if diff >= 0 else ''}{diff})", delta=status)

# --- Dynamic Multi-Wicket Future Projections ---
st.markdown("___")
st.markdown("### 🔮 Future Par Score Projections")

for future_wickets in range(wickets, 11):
    st.markdown(f"#### If **{future_wickets} wickets** down:")
    lines = []
    for over in range(current_over + 1, 21):
        future_par = cric_par_score(over, future_wickets, target)
        lines.append(f"- Over {over}: **{future_par}**")
    st.markdown("\n".join(lines))
