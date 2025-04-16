import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Cric Simulator", page_icon="🏏")

# --- Theme Toggle ---
theme = st.radio("🌓 Choose Theme", ["Light", "Dark"], horizontal=True)

# --- Theme Styling ---
if theme == "Dark":
    st.markdown("""
    <style>
    body, .stApp { background-color: #0f172a; color: #f1f5f9; }
    label { color: #f8fafc !important; }
    div[data-testid="metric-container"] {
        background-color: #1e293b;
        border: 2px solid #38bdf8;
        border-radius: 12px;
        padding: 16px;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    body, .stApp { background-color: #ffffff; color: #1e293b; }
    label { color: #1e293b !important; }
    div[data-testid="metric-container"] {
        background-color: #f8fafc;
        border: 2px solid #60a5fa;
        border-radius: 12px;
        padding: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- App Title ---
st.title("🏏 Cric Simulator")
st.markdown("Match-aware par score simulator with RRR, pressure logic, milestones & future projections.")

# --- Match Format Selector ---
match_format = st.selectbox("🕒 Match Format (Overs)", list(range(5, 21)), index=15)

# --- Par Score Function ---
def cric_par_score(current_over, current_wickets, target_score, total_overs, batters_left):
    avg_target = 180
    diff_boost = min((target_score - avg_target) / 10 * 0.02, 0.10) if target_score > avg_target else 0
    pp_end, mid_end = 0.3 * total_overs, 0.75 * total_overs

    if current_over <= pp_end:
        progress = (current_over / pp_end) * (0.293 + diff_boost)
    elif current_over <= mid_end:
        progress = 0.293 + ((current_over - pp_end) / (mid_end - pp_end)) * ((0.706 + diff_boost) - 0.293)
    else:
        progress = 0.706 + ((current_over - mid_end) / (total_overs - mid_end)) * ((1.0 + diff_boost) - 0.706)

    base_score = target_score * progress
    ideal_wickets = current_over / 5
    extra_wickets = max(0, current_wickets - ideal_wickets)

    over_weight = 0.8 if current_over <= pp_end else 1.0 if current_over <= mid_end else 1.3
    batter_factor = 0.8 if batters_left >= 3 else 1.0 if batters_left == 2 else 1.3 if batters_left == 1 else 1.6

    pressure = extra_wickets * over_weight * 4.5 * batter_factor
    return max(0, min(round(base_score + pressure), target_score))

# --- User Inputs ---
st.markdown("### 📌 Match Situation")
target = st.number_input("🎯 Target Score", 30, 300, 167)
overs = st.slider("⏱️ Overs Completed", 1, match_format, 6)
wickets = st.slider("❌ Wickets Lost", 0, 10, 2)
score = st.number_input("📌 Current Score", 0, target, 45)
batters_left = st.slider("🧠 Batters/All-Rounders Left", 0, 6, 4)

# --- Current Par Score ---
par = cric_par_score(overs, wickets, target, match_format, batters_left)
diff = score - par
status = "✅ Ahead" if diff >= 0 else "❌ Behind"

st.markdown(f"### 📍 Par Score at {overs} Overs, {wickets} Wickets: **{par}**")
st.metric("Your Score", f"{score} ({'+' if diff >= 0 else ''}{diff})", delta=status)

# --- Required Run Rate (RRR) ---
st.markdown("### 📈 Required Run Rate (RRR)")
remaining_overs = match_format - overs
rrr = round((target - score) / remaining_overs, 2) if remaining_overs > 0 else 0

if batters_left >= 3:
    rrr_comment = "👍 RRR is manageable with strong depth"
elif batters_left == 2:
    rrr_comment = "⚠️ RRR rising — stay alert"
else:
    rrr_comment = "🚨 High RRR & shallow depth — high risk"

st.markdown(f"**RRR:** `{rrr}` → {rrr_comment}")

# --- Milestone Par Targets ---
st.markdown("### 🧭 Phase-Based Milestone Targets")
for milestone in [6, 10, 15, 20]:
    if milestone <= match_format:
        phase_par = cric_par_score(milestone, wickets, target, match_format, batters_left)
        st.markdown(f"- Over **{milestone}**: Par Score = `{phase_par}`")

# --- 🔮 Future Projections by Over & Wickets ---
st.markdown("### 🔮 Future Par Score Projections by Wickets Lost")

for future_over in range(overs + 1, match_format + 1):
    st.markdown(f"#### Over {future_over}")
    lines = []
    for w in range(wickets, 11):
        added = w - wickets
        future_batters = max(0, batters_left - added)
        future_par = cric_par_score(future_over, w, target, match_format, future_batters)
        lines.append(f"- If **{w} wickets** down: **{future_par}**")
    st.markdown("\n".join(lines))
