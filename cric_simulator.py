import streamlit as st

# --- Chase Logic (Cric-style) ---
def cric_par_score(current_over, current_wickets, target_score):
    # --- Difficulty boost if target is high ---
    average_target = 180
    if target_score > average_target:
        difficulty_boost = (target_score - average_target) / 10 * 0.05
    else:
        difficulty_boost = 0

    # --- Phase-based progression (inspired by Prasanna tweets) ---
    if current_over <= 6:
        progress_percent = (current_over / 6) * (0.293 + difficulty_boost)
    elif current_over <= 10:
        progress_percent = 0.293 + ((current_over - 6) / 4) * ((0.503 + difficulty_boost) - 0.293)
    elif current_over <= 15:
        progress_percent = 0.503 + ((current_over - 10) / 5) * ((0.706 + difficulty_boost) - 0.503)
    else:
        progress_percent = 0.706 + ((current_over - 15) / 5) * ((1.0 + difficulty_boost) - 0.706)

    base_score = target_score * progress_percent

    # --- Wicket pressure penalty ---
    ideal_wickets = current_over / 5
    extra_wickets = max(0, current_wickets - ideal_wickets)
    wicket_penalty = extra_wickets * 6

    return round(base_score + wicket_penalty)

# --- UI ---
st.set_page_config(page_title="Cric Simulator", page_icon="🏏")
st.title("🏏 Cric Simulator")
st.markdown("**Simulate your chase phase-by-phase using match-style par logic**")

# --- User Inputs ---
target = st.number_input("🎯 Target Score", min_value=50, max_value=300, value=167)
current_over = st.slider("⏱️ Overs Completed", min_value=1, max_value=20, value=10)
wickets = st.slider("❌ Wickets Lost", min_value=0, max_value=10, value=2)
actual_score = st.number_input("📌 Your Current Score", min_value=0, max_value=target, value=81)

# --- Calculation ---
par = cric_par_score(current_over, wickets, target)
diff = actual_score - par
status = "✅ Ahead" if diff >= 0 else "❌ Behind"

# --- Output Display ---
st.subheader(f"📍 Required Par Score at {current_over} overs, {wickets} wickets: **{par}**")
st.metric(label="Your Progress", value=f"{actual_score} ({'+' if diff >= 0 else ''}{diff})", delta=status)

# --- Optional: Full roadmap
if st.checkbox("🔁 Show Full Chase Checkpoints"):
    st.markdown("### 🔄 Projected Par Score Milestones:")
    for over in [6, 10, 15, 20]:
        if over >= current_over:
            proj_par = cric_par_score(over, wickets, target)
            st.markdown(f"- Over {over}: **{proj_par}**")
