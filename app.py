import streamlit as st

st.set_page_config(
    page_title="AutoResearcher",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AutoResearcher")
st.markdown(
    "An autonomous AI research platform. "
    "Pick a tool from the **sidebar** to get started."
)

st.divider()

# ── Tool cards ───────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🕵️ Conspiracy Debunker")
    st.markdown(
        "Feed it any conspiracy theory. Three AI agents "
        "research it, debate it, and deliver a verdict "
        "with a confidence score."
    )
    st.info("👈 Click **Conspiracy Debunker** in the sidebar")

with col2:
    st.markdown("### 🎬 Movie DNA Analyzer")
    st.markdown(
        "Give it a genre or vibe. It finds what makes "
        "hit shows work, extracts their secret DNA, "
        "and writes you an original show pitch."
    )
    st.info("👈 Click **Movie DNA Analyzer** in the sidebar")

with col3:
    st.markdown("### 🚀 Startup Evaluator")
    st.markdown(
        "Describe your startup idea. AI researches the "
        "market, finds competitors, scores it like a VC, "
        "and writes a full investor memo."
    )
    st.info("👈 Click **Startup Evaluator** in the sidebar")

st.divider()
st.caption("Built with OpenAI · Tavily · Streamlit")