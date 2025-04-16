import streamlit as st

# ✅ Config
st.set_page_config(page_title="Cric Simulator", page_icon="🏏")

# --- Light Blue Styling ---
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
st.markdown("Smart par score calculator for dynamic matches. Built for analysts. Adjusts to overs, wickets, and batting strength.")

# --- Par Score Logic ---
def cric_par_score(current_over, current_wickets, target_score, total_overs, batters_left):
    average_target = 180
    difficulty_boost = min((target_score - average_target) / 10 * 0.02, 0.10) if target_score > average_target else 0

    # Phase-based progression using total_overs
    pp_end = 0.3 * total_overs
    mid_end = 0.75 * total_overs

    if current_over <= pp_end:
        progress_percent = (current_over / pp_end) * (0.293 + difficulty_boost)
    elif current_over <= mid_end:
        progress_percent = 0.293 + ((current_over - pp_end) / (mid_end - pp_end)) * ((0.706 + difficulty_boost) - 0.293)
    else:
        progress_percent = 0.706 + ((current_over - mid_end) / (total_overs - mid_end)) * ((1.0 + difficulty_boost) - 0.706)

    base_score = target_score * progress_percent

    # Smart Wicket Penalty
    ideal_wickets = current_over / 5
    extra_wickets = max(0, current_wickets - ideal_wickets)

    if current_over <= pp_end:
        over_weight = 0.8
    elif current_over <= mid_end:
        over_weight = 1.0
    else:
        over_weight = 1.3

    # Batting strength scaling
    if batters_left >= 3:
        batter_factor = 0.8
    elif batters_left == 2:
        batter_factor = 1.0
    elif batters_left == 1:
        batter_factor = 1.2
    else:
        batter_factor = 1.5

    wicket_penalty = extra_wickets * over_weight * 4.5 * batter_factor

    par = round(base_score - wicket_penalty)
    return max(0, min(par, target_score))

# --- Inputs ---
st.markdown("### 🎯 Match Setup")

total_overs = st.slider("🕒 Total Overs in Match", 5, 20, 20)
target = st.number_input("🏹 Target Score", min_value=30, max_value=300, value=180)
current_over = st.slider("⏱️ Overs Completed", 1, total_overs, 6)
wickets = st.slider("❌ Wickets Lost", 0, 10, 2)
actual_score = st.number_input("📌 Current Score", 0, target, 52)
batters_left = st.slider("🧠 Capable Batters/All-Rounders Left (excluding current 2)", 0, 5, 2)

# --- Par Score Now ---
par = cric_par_score(current_over, wickets, target, total_overs, batters_left)
diff = actual_score - par
status = "✅ Ahead" if diff >= 0 else "❌ Behind"

st.markdown("### 📍 Required Par Score")
st.subheader(f"Par Score at {current_over} overs, {wickets} wickets: **{par}**")
st.metric(label="Your Progress", value=f"{actual_score} ({'+' if diff >= 0 else ''}{diff})", delta=status)

# --- Future Projections ---
st.markdown("___")
st.markdown(f"### 🔮 Future Par Score Projections (Overs {current_over+1} to {total_overs})")

for wkts in range(wickets, 11):
    st.markdown(f"#### If **{wkts} wickets** down:")
    lines = []
    for over in range(current_over + 1, total_overs + 1):
        par_score = cric_par_score(over, wkts, target, total_overs, batters_left)
        lines.append(f"- Over {over}: **{par_score}**")
    st.markdown("\n".join(lines))
