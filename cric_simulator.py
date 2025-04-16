import streamlit as st

# --- Config ---
st.set_page_config(page_title="Cric Simulator", page_icon="🏏")

# --- Theme Toggle ---
theme = st.radio("🌓 Select Theme", ["Light", "Dark"], horizontal=True)

# --- Dynamic Styling ---
if theme == "Dark":
    st.markdown("""
    <style>
    body, .stApp { background-color: #0f172a; color: #f1f5f9; }
    label { color: #f8fafc !important; }
    div[data-testid="metric-container"] {
        background-color: #1e293b; border: 2px solid #38bdf8; border-radius: 12px; padding: 16px;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    body, .stApp { background-color: #ffffff; color: #1e293b; }
    label { color: #1e293b !important; }
    div[data-testid="metric-container"] {
        background-color: #f8fafc; border: 2px solid #60a5fa; border-radius: 12px; padding: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Title ---
st.title("🏏 Cric Simulator")
st.markdown("Smart chase simulator with real-time par, pressure, RRR, and phase goals.")

# --- Match Format ---
match_format = st.selectbox("🕒 Match Format (Total Overs)", list(range(5, 21)), index=15)

# --- Par Score Logic ---
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

    if batters_left >= 3:
        batter_factor = 0.8
    elif batters_left == 2:
        batter_factor = 1.0
    elif batters_left == 1:
        batter_factor = 1.3
    else:
        batter_factor = 1.6

    pressure_boost = extra_wickets * over_weight * 4.5 * batter_factor
    return max(0, min(round(base_score + pressure_boost), target_score))

# --- User Inputs ---
st.markdown("### 📌 Match Situation")
target = st.number_input("🎯 Target Score", 30, 300, 167)
overs = st.slider("⏱️ Overs Completed", 1, match_format, 6)
wickets = st.slider("❌ Wickets Lost", 0, 10, 2)
score = st.number_input("📌 Current Score", 0, target, 45)
batters_left = st.slider("🧠 Batters/All-Rounders Left", 0, 6, 4)

# --- Par + RRR + Commentary ---
par = cric_par_score(overs, wickets, target, match_format, batters_left)
diff = score - par
status = "✅ Ahead" if diff >= 0 else "❌ Behind"

remaining_overs = match_format - overs
rrr = round((target - score) / remaining_overs, 2) if remaining_overs > 0 else 0

if batters_left >= 3:
    rrr_comment = "👍 RRR is manageable with strong depth"
elif batters_left == 2:
    rrr_comment = "⚠️ RRR rising — need to watch wickets"
else:
    rrr_comment = "🚨 RRR is high and depth is thin"

# --- Output Display ---
st.markdown("### 📍 Current Par & Pressure Check")
st.subheader(f"Par at {overs} overs, {wickets} wickets: **{par}**")
st.metric("Your Progress", f"{score} ({'+' if diff >= 0 else ''}{diff})", delta=status)
st.markdown(f"**Required Run Rate:** {rrr} → {rrr_comment}")

# --- Phase Milestones ---
st.markdown("### 🧭 Milestone Targets")
phase_milestones = [6, 10, 15, 20]
for milestone in phase_milestones:
    if milestone <= match_format:
        phase_par = cric_par_score(milestone, wickets, target, match_format, batters_left)
        st.markdown(f"- Over {milestone}: **{phase_par}** if still {wickets} down")

# --- Future Projections ---
st.markdown("---")
st.markdown("### 🔮 Future Overs – Wicket-Based Projections")

for future_over in range(overs + 1, match_format + 1):
    st.markdown(f"#### Over {future_over}")
    rows = []
    for future_wkts in range(wickets, 11):
        added = future_wkts - wickets
        future_batters = max(0, batters_left - added)
        par_future = cric_par_score(future_over, future_wkts, target, match_format, future_batters)
        rows.append(f"- If **{future_wkts} wickets** down: **{par_future}**")
    st.markdown("\n".join(rows))
