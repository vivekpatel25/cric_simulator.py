import streamlit as st

# --- Streamlit Config ---
st.set_page_config(page_title="Cric Simulator", page_icon="🏏")

# --- Styling ---
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

# --- Title ---
st.title("🏏 **Cric Simulator**")
st.markdown("Match-aware par score simulator based on target, wickets, and batting depth.")

# --- Match Format Selector ---
match_format = st.selectbox("🕒 Select Match Format (Total Overs)", list(range(5, 21)), index=15)

# --- Smart Par Score Logic ---
def cric_par_score(current_over, current_wickets, target_score, total_overs, batters_left):
    average_target = 180
    difficulty_boost = min((target_score - average_target) / 10 * 0.02, 0.10) if target_score > average_target else 0

    # Progress by phase (based on match format)
    pp_end = 0.3 * total_overs
    mid_end = 0.75 * total_overs

    if current_over <= pp_end:
        progress_percent = (current_over / pp_end) * (0.293 + difficulty_boost)
    elif current_over <= mid_end:
        progress_percent = 0.293 + ((current_over - pp_end) / (mid_end - pp_end)) * ((0.706 + difficulty_boost) - 0.293)
    else:
        progress_percent = 0.706 + ((current_over - mid_end) / (total_overs - mid_end)) * ((1.0 + difficulty_boost) - 0.706)

    base_score = target_score * progress_percent

    # Wicket pressure
    ideal_wickets = current_over / 5
    extra_wickets = max(0, current_wickets - ideal_wickets)

    if current_over <= pp_end:
        over_weight = 0.8
    elif current_over <= mid_end:
        over_weight = 1.0
    else:
        over_weight = 1.3

    # Batter penalty logic
    if batters_left >= 3:
        batter_factor = 0.8
    elif batters_left == 2:
        batter_factor = 1.0
    elif batters_left == 1:
        batter_factor = 1.3
    else:
        batter_factor = 1.6

    pressure_boost = extra_wickets * over_weight * 4.5 * batter_factor
    par = round(base_score + pressure_boost)
    return max(0, min(par, target_score))

# --- User Inputs ---
st.markdown("### 📌 Match Situation")

target = st.number_input("🎯 Target Score", min_value=30, max_value=300, value=167)
overs_completed = st.slider("⏱️ Overs Completed", 1, match_format, 6)
wickets = st.slider("❌ Wickets Lost", 0, 10, 2)
actual_score = st.number_input("📌 Your Current Score", 0, target, 45)
batters_left = st.slider("🧠 Capable Batters or All-Rounders Left (excluding current 2)", 0, 6, 4)

# --- Calculate Current Par ---
current_par = cric_par_score(overs_completed, wickets, target, match_format, batters_left)
diff = actual_score - current_par
status = "✅ Ahead" if diff >= 0 else "❌ Behind"

st.markdown("### 📍 Current Par Score")
st.subheader(f"Par at {overs_completed} overs, {wickets} wickets: **{current_par}**")
st.metric("Your Progress", f"{actual_score} ({'+' if diff >= 0 else ''}{diff})", delta=status)

# --- Future Projections ---
st.markdown("---")
st.markdown("### 🔮 Future Overs — Par Score by Wickets Lost")

for future_over in range(overs_completed + 1, match_format + 1):
    st.markdown(f"#### Over {future_over}")
    rows = []
    for future_wkts in range(wickets, 11):
        additional_wkts = future_wkts - wickets
        future_batters_left = max(0, batters_left - additional_wkts)

        future_par = cric_par_score(
            current_over=future_over,
            current_wickets=future_wkts,
            target_score=target,
            total_overs=match_format,
            batters_left=future_batters_left
        )

        rows.append(f"- If **{future_wkts} wickets** down: **{future_par}**")

    st.markdown("\n".join(rows))
