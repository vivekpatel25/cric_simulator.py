import streamlit as st

# --- Custom Styling ---
st.markdown("""
<style>
body {
    background-color: #fdfbfb;
}
h1 {
    color: #D72638;
    font-family: 'Arial Black';
}
section.main > div {
    padding-top: 2rem;
}
div[data-testid="metric-container"] {
    background-color: #f5f5f5;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 15px;
    margin: 8px 0px;
}
div[data-testid="stMetricDelta"] {
    font-size: 1.1rem;
    font-weight: bold;
}
hr {
    border: 0;
    height: 2px;
    background: linear-gradient(to right, #D72638, #3F88C5);
    margin-top: 2rem;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- Streamlit Setup ---
st.set_page_config(page_title="Cric Simulator", page_icon="🏏")
st.title("🏏 **Cric Simulator**")
st.markdown("""
Simulate your chase like an analyst.  
_Adjusts for target pressure, wickets, and match momentum. Inspired by 🧠 tweet logic._
""")

# --- Chase Logic Function ---
def cric_par_score(current_over, current_wickets, target_score):
    average_target = 180
    difficulty_boost = min((target_score - average_target) / 10 * 0.02, 0.10) if target_score > average_target else 0

    # Phase-wise progression
    if current_over <= 6:
        progress_percent = (current_over / 6) * (0.293 + difficulty_boost)
    elif current_over <= 10:
        progress_percent = 0.293 + ((current_over - 6) / 4) * ((0.503 + difficulty_boost) - 0.293)
    elif current_over <= 15:
        progress_percent = 0.503 + ((current_over - 10) / 5) * ((0.706 + difficulty_boost) - 0.503)
    else:
        progress_percent = 0.706 + ((current_over - 15) / 5) * ((1.0 + difficulty_boost) - 0.706)

    base_score = target_score * progress_percent

    # Soft scaling wicket penalty
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
    return round(base_score + wicket_penalty)

# --- Inputs ---
target = st.number_input("🎯 Target Score", min_value=50, max_value=300, value=222)
current_over = st.slider("⏱️ Overs Completed", min_value=1, max_value=20, value=6)
wickets = st.slider("❌ Wickets Lost", min_value=0, max_value=10, value=2)
actual_score = st.number_input("📌 Your Current Score", min_value=0, max_value=target, value=54)

# --- Calculate Current Par ---
par = cric_par_score(current_over, wickets, target)
diff = actual_score - par
status = "✅ Ahead" if diff >= 0 else "❌ Behind"

# --- Output Section ---
st.subheader(f"📍 Required Par Score at {current_over} overs, {wickets} wickets: **{par}**")
st.metric(label="Your Progress", value=f"{actual_score} ({'+' if diff >= 0 else ''}{diff})", delta=status)

# --- Full Roadmap Option ---
st.markdown("___")
if st.checkbox("🔁 Show Full Chase Checkpoints"):
    st.markdown("### 🔄 Projected Par Score Milestones")
    for over in [6, 10, 15, 20]:
        if over >= current_over:
            proj_par = cric_par_score(over, wickets, target)
            st.markdown(f"- **Over {over}** ➤ {proj_par}")

# --- 10 Over Projection if Current < 10 ---
st.markdown("___")
if current_over < 10:
    st.markdown("### 🔮 Where Should They Be at 10 Overs?")
    for projected_wickets in range(wickets, wickets + 4):
        par_10 = cric_par_score(10, projected_wickets, target)
        runs_to_add = par_10 - actual_score
        req_rr = round((target - par_10) / 10, 2)
        st.markdown(f"""
        - If **{projected_wickets} wickets** down at 10 overs:
          - 📊 Par Score: **{par_10}**
          - ➕ Runs to Add: **{runs_to_add}**
          - 🔁 Required RR: **{req_rr}**
        """)
