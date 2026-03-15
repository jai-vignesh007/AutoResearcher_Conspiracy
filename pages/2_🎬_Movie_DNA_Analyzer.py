import streamlit as st
from movie_agents import analyze_genre, write_pitch, score_show

st.set_page_config(
    page_title="Movie DNA Analyzer",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Movie DNA Analyzer")
st.markdown(
    "Enter a genre or vibe. The AI will find the **secret DNA** "
    "of hit shows, write you an **original pitch**, "
    "and **score any existing show** against the formula."
)
st.divider()

# ── Input ────────────────────────────────────────────────────
genre = st.text_input(
    "🎭 Enter a genre or vibe",
    placeholder="e.g. dark psychological thrillers, feel-good romcoms, space operas"
)

run = st.button("🧬 Extract DNA", type="primary", use_container_width=True)

# ── Run pipeline ─────────────────────────────────────────────
if run and genre.strip():

    st.divider()
    status_box = st.empty()
    log_lines  = []

    def update_status(msg: str):
        log_lines.append(msg)
        status_box.info("\n\n".join(log_lines[-6:]))

    # ── Step 1: Extract DNA ───────────────────────────────────
    with st.spinner("Researching shows and extracting DNA..."):
        dna = analyze_genre(genre.strip(), status_callback=update_status)

    status_box.empty()

    # ── Shows analyzed ────────────────────────────────────────
    st.subheader("📺 Shows Analyzed")
    cols = st.columns(3)
    for i, title in enumerate(dna["titles"]):
        cols[i % 3].markdown(f"• {title}")

    st.divider()

    # ── DNA breakdown ─────────────────────────────────────────
    st.subheader("🧬 The Hidden DNA")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🎯 Core Theme**")
        st.info(dna["core_theme"])

        st.markdown("**👤 Character Archetype**")
        st.info(dna["character_archetype"])

        st.markdown("**📖 Story Structure**")
        st.info(dna["story_structure"])

    with col2:
        st.markdown("**💓 Emotional Hook**")
        st.info(dna["emotional_hook"])

        st.markdown("**🎨 Visual Style**")
        st.info(dna["visual_style"])

        st.markdown("**✨ Secret Ingredient**")
        st.success(dna["secret_ingredient"])

    if dna["patterns"]:
        st.markdown("**🔍 Hidden Patterns**")
        st.warning(dna["patterns"])

    st.divider()

    # ── Step 2: Generate pitch ────────────────────────────────
    st.subheader("✍️ Original Show Pitch")
    st.markdown("*Based on the DNA formula above*")

    with st.spinner("Writing original show pitch..."):
        log_lines.clear()
        pitch = write_pitch(dna, status_callback=update_status)
    status_box.empty()

    # Pitch header card
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                    border-radius: 14px; padding: 28px 32px; color: white;
                    margin-bottom: 16px;">
            <div style="font-size: 26px; font-weight: 700; margin-bottom: 6px;">
                {pitch["title"]}
            </div>
            <div style="font-size: 16px; opacity: 0.75; font-style: italic;">
                {pitch["tagline"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📝 Logline**")
        st.write(pitch["logline"])

        st.markdown("**🧑 Protagonist**")
        st.write(pitch["protagonist"])

        st.markdown("**📍 Setting**")
        st.write(pitch["setting"])

    with col2:
        st.markdown("**🎬 Season Arc**")
        st.write(pitch["episode_arc"])

        st.markdown("**💥 The Twist**")
        st.error(pitch["twist"])

        st.markdown("**🧬 Why It Works**")
        st.success(pitch["why_it_works"])

    st.divider()

    # ── Step 3: Show scorer ───────────────────────────────────
    st.subheader("🎯 Score an Existing Show")
    st.markdown("*See how well any show matches the DNA formula*")

    show_input = st.text_input(
        "Enter a show or movie name",
        placeholder="e.g. True Detective, Gone Girl, Hannibal"
    )

    score_btn = st.button("📊 Score It", type="secondary")

    if score_btn and show_input.strip():
        with st.spinner(f"Scoring {show_input}..."):
            log_lines.clear()
            score = score_show(show_input.strip(), dna, status_callback=update_status)
        status_box.empty()

        st.markdown(f"### 📊 {score['show_name']} — DNA Score")

        # Overall score with big progress bar
        overall = score["overall"]
        bar_color = "#1D9E75" if overall >= 75 else "#BA7517" if overall >= 50 else "#E85D24"
        st.markdown(f"**Overall Match: {overall}/100**")
        st.progress(overall / 100)

        # Four sub-scores
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("🎯 Theme",     f"{score['theme']}/100")
        with c2:
            st.metric("👤 Character", f"{score['character']}/100")
        with c3:
            st.metric("📖 Structure", f"{score['structure']}/100")
        with c4:
            st.metric("💓 Hook",      f"{score['hook']}/100")

        st.markdown("**Verdict**")
        st.info(score["verdict"])

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✅ Strengths**")
            st.success(score["strengths"])
        with col2:
            st.markdown("**⚠️ Weaknesses**")
            st.warning(score["weaknesses"])

elif run and not genre.strip():
    st.warning("Please enter a genre or vibe first!")