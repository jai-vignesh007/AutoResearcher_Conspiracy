import streamlit as st
from agents import auto_research_loop



# ── Header ───────────────────────────────────────────────────
st.title("🕵️ Conspiracy Debunker")
st.markdown(
    "Type any conspiracy theory. The AI will **autonomously research it**, "
    "run a **Pro vs Con debate**, and deliver a **verdict with confidence score**."
)
st.divider()

# ── Input form ───────────────────────────────────────────────
claim = st.text_input(
    "🔎 Enter a conspiracy theory",
    placeholder="e.g. NASA faked the moon landing"
)

col1, col2 = st.columns(2)
with col1:
    threshold = st.slider(
        "Confidence target %",
        min_value=50, max_value=95,
        value=75, step=5
    )
with col2:
    max_iter = st.slider(
        "Max research loops",
        min_value=1, max_value=4,
        value=3, step=1
    )

run = st.button("🔍 Investigate", type="primary", use_container_width=True)

# ── Run pipeline ─────────────────────────────────────────────
if run and claim.strip():

    st.divider()

    # Live status log using a Streamlit placeholder
    status_box  = st.empty()
    log_lines   = []

    def update_status(msg: str):
        log_lines.append(msg)
        # Show last 6 lines so it feels like a live feed
        status_box.info("\n\n".join(log_lines[-6:]))

    with st.spinner("AutoResearcher is running..."):
        result = auto_research_loop(
            claim,
            confidence_threshold=threshold,
            max_iterations=max_iter,
            status_callback=update_status
        )

    status_box.empty()  # clear the live log once done

    # ── Verdict color config ──────────────────────────────────
    config = {
        "TRUE":         {"color": "red",    "emoji": "🔴"},
        "FALSE":        {"color": "green",  "emoji": "🟢"},
        "UNVERIFIABLE": {"color": "orange", "emoji": "🟡"},
    }
    c = config.get(result["verdict"], config["UNVERIFIABLE"])

    # ── Verdict header ────────────────────────────────────────
    st.subheader(f"{c['emoji']} Verdict: {result['verdict']}")

    # ── Confidence bar ────────────────────────────────────────
    pct = result["confidence"]
    st.markdown(f"**Confidence Score: {pct}%**")
    st.progress(pct / 100)

    st.divider()

    # ── Reasoning ─────────────────────────────────────────────
    st.markdown("### 📋 Judge's Reasoning")
    st.write(result["reasoning"])

    # ── Fallacies ─────────────────────────────────────────────
    st.markdown("### ⚠️ Logical Fallacies Spotted")
    st.warning(result["fallacies"])

    # ── Stronger side ─────────────────────────────────────────
    st.markdown("### 🏆 Stronger Argument")
    st.success(result["stronger"])

    st.divider()

    # ── Pro vs Con side by side ───────────────────────────────
    st.markdown("### ⚔️ The Full Debate")
    pro_col, con_col = st.columns(2)

    with pro_col:
        st.markdown("#### 🔴 Pro — Conspiracy is TRUE")
        st.error(result.get("pro_case", ""))

    with con_col:
        st.markdown("#### 🔵 Con — Conspiracy is FALSE")
        st.success(result.get("con_case", ""))

elif run and not claim.strip():
    st.warning("Please enter a conspiracy theory first!")