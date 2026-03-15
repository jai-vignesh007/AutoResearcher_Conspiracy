import os
from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_KEY"))


# ── 1. Web Search ────────────────────────────────────────────
def search_web(query: str, max_results: int = 6) -> str:
    results = tavily_client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced"
    )
    formatted = ""
    for i, r in enumerate(results["results"]):
        formatted += f"[Source {i+1}] {r['title']}\n"
        formatted += f"URL: {r['url']}\n"
        formatted += f"Content: {r['content'][:400]}\n\n"
    return formatted


# ── 2. Pro Agent ─────────────────────────────────────────────
def pro_agent(claim: str, research: str) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a sharp debate lawyer arguing that a conspiracy theory is TRUE. "
                    "Build the strongest possible case SUPPORTING the claim using ONLY "
                    "the research provided. Pick the most suspicious facts, highlight "
                    "inconsistencies, and question official explanations. "
                    "Structure your argument with 3 clear points. Be persuasive and bold."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Conspiracy claim: '{claim}'\n\n"
                    f"Research:\n{research}\n\n"
                    "Build the strongest case that this claim is TRUE."
                )
            }
        ]
    )
    return response.choices[0].message.content


# ── 3. Con Agent ─────────────────────────────────────────────
def con_agent(claim: str, research: str) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a sharp debate lawyer arguing that a conspiracy theory is FALSE. "
                    "Build the strongest possible case DEBUNKING the claim using ONLY "
                    "the research provided. Cite credible sources, explain away suspicious "
                    "claims logically, and highlight the overwhelming evidence against it. "
                    "Structure your argument with 3 clear points. Be persuasive and precise."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Conspiracy claim: '{claim}'\n\n"
                    f"Research:\n{research}\n\n"
                    "Build the strongest case that this claim is FALSE."
                )
            }
        ]
    )
    return response.choices[0].message.content


# ── 4. Judge Agent ───────────────────────────────────────────
def judge_agent(claim: str, pro_case: str, con_case: str) -> dict:
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1500,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert fact-checker and impartial judge. "
                    "Evaluate both arguments fairly and deliver a verdict.\n\n"
                    "You MUST respond in this exact format:\n\n"
                    "VERDICT: [TRUE / FALSE / UNVERIFIABLE]\n"
                    "CONFIDENCE: [0-100]\n"
                    "REASONING: [2-3 sentences]\n"
                    "FALLACIES: [logical fallacies spotted]\n"
                    "STRONGER_SIDE: [PRO or CON and one sentence why]\n\n"
                    "Base your verdict on evidence quality, not persuasiveness."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Conspiracy claim: '{claim}'\n\n"
                    f"--- PRO ARGUMENT ---\n{pro_case}\n\n"
                    f"--- CON ARGUMENT ---\n{con_case}\n\n"
                    "Deliver your verdict now."
                )
            }
        ]
    )

    raw = response.choices[0].message.content
    verdict, confidence, reasoning, fallacies, stronger = "", 0, "", "", ""

    for line in raw.split("\n"):
        if line.startswith("VERDICT:"):
            verdict = line.replace("VERDICT:", "").strip()
        elif line.startswith("CONFIDENCE:"):
            try:
                confidence = int(line.replace("CONFIDENCE:", "").strip())
            except:
                confidence = 0
        elif line.startswith("REASONING:"):
            reasoning = line.replace("REASONING:", "").strip()
        elif line.startswith("FALLACIES:"):
            fallacies = line.replace("FALLACIES:", "").strip()
        elif line.startswith("STRONGER_SIDE:"):
            stronger = line.replace("STRONGER_SIDE:", "").strip()

    return {
        "verdict": verdict, "confidence": confidence,
        "reasoning": reasoning, "fallacies": fallacies,
        "stronger": stronger, "raw": raw
    }


# ── 5. Smart Query Generator ─────────────────────────────────
def generate_search_queries(claim: str, previous_verdict: dict) -> list:
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=300,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a research strategist. Generate 2 NEW search queries "
                    "to find better evidence for an uncertain conspiracy verdict. "
                    "Return ONLY 2 queries, one per line, nothing else."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Claim: '{claim}'\n"
                    f"Current verdict: {previous_verdict['verdict']} "
                    f"(confidence: {previous_verdict['confidence']}%)\n"
                    f"Reasoning: {previous_verdict['reasoning']}\n\n"
                    "Generate 2 new search queries."
                )
            }
        ]
    )
    raw = response.choices[0].message.content
    return [q.strip() for q in raw.strip().split("\n") if q.strip()][:2]


# ── 6. Full AutoResearch Loop ────────────────────────────────
def auto_research_loop(claim: str,
                       confidence_threshold: int = 75,
                       max_iterations: int = 3,
                       status_callback=None) -> dict:
    """
    status_callback: optional function(message) to stream
    progress updates to the UI in real time.
    """

    def log(msg):
        if status_callback:
            status_callback(msg)

    all_research = ""
    verdict      = None
    pro_case     = ""
    con_case     = ""

    for iteration in range(1, max_iterations + 1):

        log(f"🔄 Iteration {iteration}/{max_iterations}")

        if iteration == 1:
            queries = [claim, f"{claim} evidence debunked"]
        else:
            log("🧠 Generating smarter search queries...")
            queries = generate_search_queries(claim, verdict)

        for q in queries:
            log(f"🔍 Searching: *{q}*")
            all_research += search_web(q, max_results=4)

        log("⚔️ Running Pro vs Con debate...")
        pro_case = pro_agent(claim, all_research)
        con_case = con_agent(claim, all_research)

        log("🧑‍⚖️ Judge is evaluating both sides...")
        verdict = judge_agent(claim, pro_case, con_case)

        log(f"📊 Confidence after iteration {iteration}: **{verdict['confidence']}%**")

        if verdict["confidence"] >= confidence_threshold:
            log(f"✅ Reached {confidence_threshold}% threshold — stopping!")
            break
        elif iteration < max_iterations:
            log(f"⚠️ Not confident enough yet. Searching deeper...")

    verdict["pro_case"] = pro_case
    verdict["con_case"] = con_case
    return verdict