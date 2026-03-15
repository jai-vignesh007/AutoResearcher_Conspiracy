import streamlit as st
from startup_agents import evaluate_startup

st.title("🚀 Startup Idea Evaluator")
st.markdown(
    "Type your startup idea. The AI will research the **market**, "
    "hunt down **competitors**, score it like a **VC**, "
    "and write a full **investor memo** — in under 2 minutes."
)
st.divider()

# ── Input ────────────────────────────────────────────────────
idea = st.text_input(
    "💡 Describe your startup idea",
    placeholder="e.g. Uber but for dog walking"
)

run = st.button("🔍 Evaluate My Idea", type="primary", use_container_width=True)

# ── Pipeline ─────────────────────────────────────────────────
if run and idea.strip():

    st.divider()
    status_box = st.empty()
    log_lines  = []

    def update_status(msg: str):
        log_lines.append(msg)
        status_box.info("\n\n".join(log_lines[-6:]))

    with st.spinner("Running full evaluation..."):
        result = evaluate_startup(idea.strip(), status_callback=update_status)

    status_box.empty()

    market = result["market"]
    comps  = result["competitors"]
    score  = result["score"]
    memo   = result["memo"]

    # ── Decision banner ───────────────────────────────────────
    decision_config = {
        "GO":         {"color": "#1D9E75", "bg": "#F0FDF8", "emoji": "🟢"},
        "NO-GO":      {"color": "#E85D24", "bg": "#FFF3EE", "emoji": "🔴"},
        "NEEDS-WORK": {"color": "#BA7517", "bg": "#FFFBF0", "emoji": "🟡"},
    }
    dc = decision_config.get(score["decision"], decision_config["NEEDS-WORK"])

    st.markdown(
        f"""
        <div style="background:{dc['bg']}; border-left: 5px solid {dc['color']};
                    border-radius: 10px; padding: 20px 24px; margin-bottom: 8px;">
            <div style="font-size:22px; font-weight:700; color:{dc['color']};">
                {dc['emoji']} {score['decision']} — {score['overall']}/100
            </div>
            <div style="font-size:15px; color:#444; margin-top:6px;">
                {score['one_line']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ── Score cards ───────────────────────────────────────────
    st.subheader("📊 Investor Scorecard")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📈 Market",      f"{score['market']}/100")
    c2.metric("🏢 Competition", f"{score['competition']}/100")
    c3.metric("⏰ Timing",      f"{score['timing']}/100")
    c4.metric("💡 Uniqueness",  f"{score['uniqueness']}/100")
    c5.metric("⚙️ Execution",   f"{score['execution']}/100")

    st.markdown("**Overall Score**")
    st.progress(score["overall"] / 100)

    st.divider()

    # ── Market + Competitors side by side ─────────────────────
    st.subheader("🔬 Research Breakdown")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📈 Market Analysis")
        st.markdown(f"**Market Size**\n\n{market['market_size']}")
        st.markdown(f"**Growth Rate**\n\n{market['growth_rate']}")
        st.markdown(f"**Target Customer**\n\n{market['target_customer']}")
        st.info(f"**Key Trends**\n\n{market['key_trends']}")
        st.success(f"**Timing**\n\n{market['market_timing']}")

    with col2:
        st.markdown("#### 🏢 Competitive Landscape")
        st.markdown(f"**Top Competitors**\n\n{comps['top_competitors']}")
        st.markdown(f"**Market Leader**\n\n{comps['market_leader']}")
        st.warning(f"**Their Weakness**\n\n{comps['competitor_weakness']}")
        st.success(f"**Gap in Market**\n\n{comps['gap_in_market']}")
        st.info(f"**How to Differentiate**\n\n{comps['differentiation']}")

    st.divider()

    # ── Risk + Opportunity ────────────────────────────────────
    st.subheader("⚖️ Risk vs Opportunity")
    r_col, o_col = st.columns(2)
    with r_col:
        st.error(f"⚠️ **Biggest Risk**\n\n{score['biggest_risk']}")
    with o_col:
        st.success(f"🚀 **Biggest Opportunity**\n\n{score['biggest_opportunity']}")

    st.divider()

    # ── Investor Memo ─────────────────────────────────────────
    st.subheader("📝 Investor Memo")
    st.markdown("*The one-pager a VC would read before deciding to take your meeting*")

    st.markdown(
        f"""
        <div style="background:#1a1a2e; color:white; border-radius:14px;
                    padding:28px 32px; margin-bottom:16px;">
            <div style="font-size:11px; opacity:0.5; text-transform:uppercase;
                        letter-spacing:2px; margin-bottom:8px;">
                Investment Memo
            </div>
            <div style="font-size:22px; font-weight:700;">{idea}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    sections = [
        ("🎯 Problem",          memo["problem"]),
        ("💡 Solution",         memo["solution"]),
        ("📈 Market",           memo["market"]),
        ("💰 Business Model",   memo["business_model"]),
        ("🏢 Competition",      memo["competition"]),
        ("📍 Traction Needed",  memo["traction_needed"]),
        ("⚠️ Risks",            memo["risks"]),
        ("💵 The Ask",          memo["the_ask"]),
    ]

    for label, content in sections:
        if content:
            with st.expander(label, expanded=True):
                st.write(content)

    # Final verdict highlighted
    if memo["verdict"]:
        st.markdown("### 🏁 Final Verdict")
        st.info(memo["verdict"])

elif run and not idea.strip():
    st.warning("Please enter a startup idea first!")