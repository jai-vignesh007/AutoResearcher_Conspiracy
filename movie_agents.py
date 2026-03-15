import os
from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_KEY"))


# ── 1. Find top shows in a genre ─────────────────────────────
def find_top_shows(genre: str) -> list[str]:
    """
    Asks GPT to list the 6 most iconic hit shows/movies
    for a given genre or vibe. Returns a plain list of titles.

    Why GPT and not search here?
    GPT already knows pop culture extremely well.
    We use search for facts — we use GPT for cultural knowledge.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=300,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a film and TV expert. "
                    "When given a genre or vibe, return ONLY a plain list "
                    "of exactly 6 iconic hit shows or movies in that genre. "
                    "One title per line. No numbers, no explanations, no extra text."
                )
            },
            {
                "role": "user",
                "content": f"Genre/vibe: '{genre}'"
            }
        ]
    )

    raw = response.choices[0].message.content
    titles = [t.strip() for t in raw.strip().split("\n") if t.strip()]
    return titles[:6]


# ── 2. Research a single show ────────────────────────────────
def research_show(title: str) -> str:
    """
    Searches the web for what critics and audiences say
    about a specific show — what made it work, themes,
    storytelling techniques, why it was a hit.
    """
    results = tavily_client.search(
        query=f"{title} TV show what makes it great storytelling analysis",
        max_results=3,
        search_depth="advanced"
    )

    formatted = f"=== {title} ===\n"
    for r in results["results"]:
        formatted += f"- {r['content'][:300]}\n"
    return formatted


# ── 3. Research ALL shows in the genre ───────────────────────
def research_all_shows(titles: list[str],
                       status_callback=None) -> str:
    """
    Loops through every show title and gathers research.
    Combines everything into one big context block.
    """
    def log(msg):
        if status_callback:
            status_callback(msg)

    all_research = ""
    for title in titles:
        log(f"🔍 Researching: *{title}*...")
        all_research += research_show(title) + "\n"

    return all_research


# ── 4. DNA Extractor agent ───────────────────────────────────
def extract_dna(genre: str, research: str) -> dict:
    """
    The core agent. Reads research across all shows and
    extracts the hidden DNA — what patterns they ALL share.

    Returns a structured dict with DNA components.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert story analyst and showrunner. "
                    "You will be given research about multiple hit shows in a genre. "
                    "Your job is to find the HIDDEN DNA — the patterns they all share "
                    "that explain why they succeeded.\n\n"
                    "You MUST respond in this exact format:\n\n"
                    "CORE_THEME: [The central theme all these shows share in 1 sentence]\n"
                    "CHARACTER_ARCHETYPE: [The type of protagonist that always appears]\n"
                    "STORY_STRUCTURE: [The plot structure they follow]\n"
                    "EMOTIONAL_HOOK: [The core emotion that keeps audiences hooked]\n"
                    "VISUAL_STYLE: [Common visual/aesthetic patterns]\n"
                    "SECRET_INGREDIENT: [The one surprising thing they all have that people miss]\n"
                    "PATTERNS: [3 bullet points of hidden patterns found across all shows]\n\n"
                    "Be specific and insightful. No generic answers."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Genre/vibe: '{genre}'\n\n"
                    f"Research on hit shows:\n{research}\n\n"
                    "Extract the hidden DNA."
                )
            }
        ]
    )

    raw = response.choices[0].message.content

    # ── Parse into a dict (same technique as judge agent) ────
    dna = {
        "core_theme": "",
        "character_archetype": "",
        "story_structure": "",
        "emotional_hook": "",
        "visual_style": "",
        "secret_ingredient": "",
        "patterns": "",
        "raw": raw
    }

    for line in raw.split("\n"):
        if line.startswith("CORE_THEME:"):
            dna["core_theme"] = line.replace("CORE_THEME:", "").strip()
        elif line.startswith("CHARACTER_ARCHETYPE:"):
            dna["character_archetype"] = line.replace("CHARACTER_ARCHETYPE:", "").strip()
        elif line.startswith("STORY_STRUCTURE:"):
            dna["story_structure"] = line.replace("STORY_STRUCTURE:", "").strip()
        elif line.startswith("EMOTIONAL_HOOK:"):
            dna["emotional_hook"] = line.replace("EMOTIONAL_HOOK:", "").strip()
        elif line.startswith("VISUAL_STYLE:"):
            dna["visual_style"] = line.replace("VISUAL_STYLE:", "").strip()
        elif line.startswith("SECRET_INGREDIENT:"):
            dna["secret_ingredient"] = line.replace("SECRET_INGREDIENT:", "").strip()
        elif line.startswith("PATTERNS:"):
            dna["patterns"] = line.replace("PATTERNS:", "").strip()

    return dna


# ── 5. Full DNA pipeline (Search + Research + Extract) ───────
def analyze_genre(genre: str, status_callback=None) -> dict:
    """
    The main pipeline:
    1. Find top shows in genre
    2. Research each show on the web
    3. Extract the DNA across all of them
    """
    def log(msg):
        if status_callback:
            status_callback(msg)

    log(f"🎬 Finding top shows for: *{genre}*...")
    titles = find_top_shows(genre)
    log(f"✅ Found: {', '.join(titles)}")

    log("🔍 Researching each show on the web...")
    research = research_all_shows(titles, status_callback)

    log("🧬 Extracting the hidden DNA...")
    dna = extract_dna(genre, research)

    # attach the show titles so we can display them
    dna["titles"] = titles
    dna["genre"]  = genre

    log("✅ DNA extracted!")
    return dna


# ── 6. Pitch Writer agent ────────────────────────────────────
def write_pitch(dna: dict, status_callback=None) -> dict:
    """
    Takes the extracted DNA and writes a full original
    show pitch that follows the formula.
    """
    def log(msg):
        if status_callback:
            status_callback(msg)

    log("✍️ Writing original show pitch from DNA...")

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Hollywood showrunner and pitch writer. "
                    "Given the DNA of a successful genre, write a compelling "
                    "original show pitch that uses this DNA formula.\n\n"
                    "You MUST respond in this exact format:\n\n"
                    "TITLE: [Catchy show title]\n"
                    "TAGLINE: [One punchy sentence]\n"
                    "LOGLINE: [2-3 sentence premise]\n"
                    "PROTAGONIST: [Who is the main character and what's their flaw]\n"
                    "SETTING: [Where and when]\n"
                    "EPISODE_ARC: [How the first season unfolds across 3 acts]\n"
                    "TWIST: [The shocking mid-season or finale twist]\n"
                    "WHY_IT_WORKS: [One sentence explaining how it uses the DNA formula]\n\n"
                    "Be bold, specific, and original. No generic ideas."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Genre: '{dna['genre']}'\n\n"
                    f"DNA Formula:\n"
                    f"- Core theme: {dna['core_theme']}\n"
                    f"- Character archetype: {dna['character_archetype']}\n"
                    f"- Story structure: {dna['story_structure']}\n"
                    f"- Emotional hook: {dna['emotional_hook']}\n"
                    f"- Visual style: {dna['visual_style']}\n"
                    f"- Secret ingredient: {dna['secret_ingredient']}\n\n"
                    "Write a full original show pitch using this DNA."
                )
            }
        ]
    )

    raw = response.choices[0].message.content

    pitch = {
        "title": "", "tagline": "", "logline": "",
        "protagonist": "", "setting": "",
        "episode_arc": "", "twist": "",
        "why_it_works": "", "raw": raw
    }

    for line in raw.split("\n"):
        if line.startswith("TITLE:"):
            pitch["title"] = line.replace("TITLE:", "").strip()
        elif line.startswith("TAGLINE:"):
            pitch["tagline"] = line.replace("TAGLINE:", "").strip()
        elif line.startswith("LOGLINE:"):
            pitch["logline"] = line.replace("LOGLINE:", "").strip()
        elif line.startswith("PROTAGONIST:"):
            pitch["protagonist"] = line.replace("PROTAGONIST:", "").strip()
        elif line.startswith("SETTING:"):
            pitch["setting"] = line.replace("SETTING:", "").strip()
        elif line.startswith("EPISODE_ARC:"):
            pitch["episode_arc"] = line.replace("EPISODE_ARC:", "").strip()
        elif line.startswith("TWIST:"):
            pitch["twist"] = line.replace("TWIST:", "").strip()
        elif line.startswith("WHY_IT_WORKS:"):
            pitch["why_it_works"] = line.replace("WHY_IT_WORKS:", "").strip()

    log(f"✅ Pitch written: *{pitch['title']}*")
    return pitch


# ── 7. Show Scorer agent ─────────────────────────────────────
def score_show(show_name: str, dna: dict, status_callback=None) -> dict:
    """
    Scores an existing show against the extracted DNA formula.
    Tells you WHY it succeeded or failed based on the patterns.
    """
    def log(msg):
        if status_callback:
            status_callback(msg)

    log(f"🎯 Scoring *{show_name}* against the DNA formula...")

    # First search for info about this specific show
    results = tavily_client.search(
        query=f"{show_name} TV show analysis storytelling review",
        max_results=3,
        search_depth="advanced"
    )
    show_research = "\n".join([r["content"][:300] for r in results["results"]])

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1500,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a film critic and story analyst. "
                    "Score a show against a genre DNA formula. "
                    "Be honest — a low score is fine if the show doesn't fit.\n\n"
                    "You MUST respond in this exact format:\n\n"
                    "OVERALL_SCORE: [0-100]\n"
                    "THEME_SCORE: [0-100]\n"
                    "CHARACTER_SCORE: [0-100]\n"
                    "STRUCTURE_SCORE: [0-100]\n"
                    "HOOK_SCORE: [0-100]\n"
                    "VERDICT: [One sentence — does this show nail the DNA formula?]\n"
                    "STRENGTHS: [What it does right according to the formula]\n"
                    "WEAKNESSES: [Where it diverges from the formula]\n\n"
                    "Base scores on evidence, not personal taste."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Show to score: '{show_name}'\n\n"
                    f"Show research:\n{show_research}\n\n"
                    f"DNA Formula to score against:\n"
                    f"- Core theme: {dna['core_theme']}\n"
                    f"- Character archetype: {dna['character_archetype']}\n"
                    f"- Story structure: {dna['story_structure']}\n"
                    f"- Emotional hook: {dna['emotional_hook']}\n"
                    f"- Secret ingredient: {dna['secret_ingredient']}\n\n"
                    f"Score this show against the DNA formula."
                )
            }
        ]
    )

    raw = response.choices[0].message.content

    score = {
        "show_name": show_name,
        "overall": 0, "theme": 0, "character": 0,
        "structure": 0, "hook": 0,
        "verdict": "", "strengths": "", "weaknesses": "",
        "raw": raw
    }

    for line in raw.split("\n"):
        try:
            if line.startswith("OVERALL_SCORE:"):
                score["overall"] = int(line.replace("OVERALL_SCORE:", "").strip())
            elif line.startswith("THEME_SCORE:"):
                score["theme"] = int(line.replace("THEME_SCORE:", "").strip())
            elif line.startswith("CHARACTER_SCORE:"):
                score["character"] = int(line.replace("CHARACTER_SCORE:", "").strip())
            elif line.startswith("STRUCTURE_SCORE:"):
                score["structure"] = int(line.replace("STRUCTURE_SCORE:", "").strip())
            elif line.startswith("HOOK_SCORE:"):
                score["hook"] = int(line.replace("HOOK_SCORE:", "").strip())
            elif line.startswith("VERDICT:"):
                score["verdict"] = line.replace("VERDICT:", "").strip()
            elif line.startswith("STRENGTHS:"):
                score["strengths"] = line.replace("STRENGTHS:", "").strip()
            elif line.startswith("WEAKNESSES:"):
                score["weaknesses"] = line.replace("WEAKNESSES:", "").strip()
        except:
            pass

    log(f"✅ Score: {score['overall']}/100")
    return score


# ── Quick test — run directly with: streamlit run movie_agents.py ──
if __name__ == "__main__":
    genre = "dark psychological thrillers"

    # Test 1: DNA extraction
    print("🎬 Step 1 — Extracting DNA...\n")
    dna = analyze_genre(genre, status_callback=print)
    print(f"\n✅ Core theme: {dna['core_theme']}")

    # Test 2: Pitch writer
    print("\n✍️  Step 2 — Writing pitch...\n")
    pitch = write_pitch(dna, status_callback=print)
    print(f"\n✅ Show title : {pitch['title']}")
    print(f"   Tagline    : {pitch['tagline']}")
    print(f"   Logline    : {pitch['logline']}")

    # Test 3: Show scorer
    print("\n🎯 Step 3 — Scoring a show...\n")
    score = score_show("True Detective", dna, status_callback=print)
    print(f"\n✅ Score      : {score['overall']}/100")
    print(f"   Verdict    : {score['verdict']}")