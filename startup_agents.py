import os
from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_KEY"))


# ── Helper: web search (same pattern as before) ──────────────
def search_web(query: str, max_results: int = 5) -> str:
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


# ── 1. Market Research Agent ─────────────────────────────────
def market_agent(idea: str, status_callback=None) -> dict:
    """
    Researches the market for a startup idea.
    Finds market size, growth trends, target customers,
    and recent news in the space.
    """
    def log(msg):
        if status_callback:
            status_callback(msg)

    log("📈 Researching market size and trends...")

    # Two targeted searches for better coverage
    research  = search_web(f"{idea} market size growth 2024 2025", max_results=4)
    research += search_web(f"{idea} industry trends target customers", max_results=3)

    log("🤖 Analyzing market data...")

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1200,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a market research analyst at a top VC firm. "
                    "Analyze the market for a startup idea using the research provided.\n\n"
                    "You MUST respond in this exact format:\n\n"
                    "MARKET_SIZE: [Estimated total market size in dollars]\n"
                    "GROWTH_RATE: [Annual growth rate % if available]\n"
                    "TARGET_CUSTOMER: [Who exactly would pay for this]\n"
                    "KEY_TRENDS: [2-3 trends making this market interesting right now]\n"
                    "MARKET_TIMING: [Is now a good time to enter? Why?]\n"
                    "MARKET_SCORE: [0-100, how attractive is this market]\n\n"
                    "Be specific with numbers where available. No vague answers."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Startup idea: '{idea}'\n\n"
                    f"Market research:\n{research}\n\n"
                    "Analyze this market."
                )
            }
        ]
    )

    raw = response.choices[0].message.content
    market = {
        "market_size": "", "growth_rate": "", "target_customer": "",
        "key_trends": "", "market_timing": "", "market_score": 0,
        "raw": raw
    }

    for line in raw.split("\n"):
        if line.startswith("MARKET_SIZE:"):
            market["market_size"] = line.replace("MARKET_SIZE:", "").strip()
        elif line.startswith("GROWTH_RATE:"):
            market["growth_rate"] = line.replace("GROWTH_RATE:", "").strip()
        elif line.startswith("TARGET_CUSTOMER:"):
            market["target_customer"] = line.replace("TARGET_CUSTOMER:", "").strip()
        elif line.startswith("KEY_TRENDS:"):
            market["key_trends"] = line.replace("KEY_TRENDS:", "").strip()
        elif line.startswith("MARKET_TIMING:"):
            market["market_timing"] = line.replace("MARKET_TIMING:", "").strip()
        elif line.startswith("MARKET_SCORE:"):
            try:
                market["market_score"] = int(line.replace("MARKET_SCORE:", "").strip())
            except:
                market["market_score"] = 0

    log(f"✅ Market score: {market['market_score']}/100")
    return market


# ── 2. Competitor Research Agent ─────────────────────────────
def competitor_agent(idea: str, status_callback=None) -> dict:
    """
    Finds existing competitors for a startup idea.
    Analyzes who's already in the space, their weaknesses,
    and where the gaps are.
    """
    def log(msg):
        if status_callback:
            status_callback(msg)

    log("🔍 Hunting down competitors...")

    research  = search_web(f"{idea} competitors startups companies", max_results=4)
    research += search_web(f"{idea} alternatives existing apps", max_results=3)

    log("🤖 Analyzing competitive landscape...")

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1200,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a competitive intelligence analyst at a top VC firm. "
                    "Map out the competitive landscape for a startup idea.\n\n"
                    "You MUST respond in this exact format:\n\n"
                    "TOP_COMPETITORS: [List 3-5 real competitors with one line each]\n"
                    "MARKET_LEADER: [Who dominates this space right now]\n"
                    "COMPETITOR_WEAKNESS: [The biggest weakness across existing players]\n"
                    "GAP_IN_MARKET: [The clearest opportunity not yet captured]\n"
                    "DIFFERENTIATION: [How a new entrant could stand out]\n"
                    "COMPETITION_SCORE: [0-100, where 100 = no competition, 0 = impossible to compete]\n\n"
                    "Be specific with real company names. No vague answers."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Startup idea: '{idea}'\n\n"
                    f"Competitor research:\n{research}\n\n"
                    "Map the competitive landscape."
                )
            }
        ]
    )

    raw = response.choices[0].message.content
    competitors = {
        "top_competitors": "", "market_leader": "",
        "competitor_weakness": "", "gap_in_market": "",
        "differentiation": "", "competition_score": 0,
        "raw": raw
    }

    for line in raw.split("\n"):
        if line.startswith("TOP_COMPETITORS:"):
            competitors["top_competitors"] = line.replace("TOP_COMPETITORS:", "").strip()
        elif line.startswith("MARKET_LEADER:"):
            competitors["market_leader"] = line.replace("MARKET_LEADER:", "").strip()
        elif line.startswith("COMPETITOR_WEAKNESS:"):
            competitors["competitor_weakness"] = line.replace("COMPETITOR_WEAKNESS:", "").strip()
        elif line.startswith("GAP_IN_MARKET:"):
            competitors["gap_in_market"] = line.replace("GAP_IN_MARKET:", "").strip()
        elif line.startswith("DIFFERENTIATION:"):
            competitors["differentiation"] = line.replace("DIFFERENTIATION:", "").strip()
        elif line.startswith("COMPETITION_SCORE:"):
            try:
                competitors["competition_score"] = int(
                    line.replace("COMPETITION_SCORE:", "").strip()
                )
            except:
                competitors["competition_score"] = 0

    log(f"✅ Competition score: {competitors['competition_score']}/100")
    return competitors


# ── 3. Scorer Agent ─────────────────────────────────────────
def scorer_agent(idea: str, market: dict, competitors: dict,
                 status_callback=None) -> dict:
    """
    Reads market + competitor research and scores the idea
    across 5 investor dimensions. Returns an overall Go/No-Go.
    """
    def log(msg):
        if status_callback:
            status_callback(msg)

    log("🧮 Scoring your idea across 5 dimensions...")

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1500,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior partner at a top VC firm evaluating a startup. "
                    "Score the idea across 5 dimensions like a real investment committee.\n\n"
                    "You MUST respond in this exact format:\n\n"
                    "MARKET_SCORE: [0-100]\n"
                    "COMPETITION_SCORE: [0-100]\n"
                    "TIMING_SCORE: [0-100, is now the right moment?]\n"
                    "UNIQUENESS_SCORE: [0-100, how differentiated is the idea?]\n"
                    "EXECUTION_SCORE: [0-100, how feasible is it to build?]\n"
                    "OVERALL_SCORE: [0-100, weighted average]\n"
                    "DECISION: [GO / NO-GO / NEEDS-WORK]\n"
                    "ONE_LINE: [One punchy sentence verdict like a real investor would say]\n"
                    "BIGGEST_RISK: [The single biggest threat to this startup]\n"
                    "BIGGEST_OPPORTUNITY: [The single biggest upside if it works]\n\n"
                    "Be brutally honest. Investors respect tough love."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Startup idea: '{idea}'\n\n"
                    f"Market analysis:\n"
                    f"- Size: {market['market_size']}\n"
                    f"- Growth: {market['growth_rate']}\n"
                    f"- Timing: {market['market_timing']}\n"
                    f"- Trends: {market['key_trends']}\n\n"
                    f"Competitor analysis:\n"
                    f"- Top players: {competitors['top_competitors']}\n"
                    f"- Market gap: {competitors['gap_in_market']}\n"
                    f"- Differentiation: {competitors['differentiation']}\n\n"
                    "Score this startup idea."
                )
            }
        ]
    )

    raw = response.choices[0].message.content
    score = {
        "market": 0, "competition": 0, "timing": 0,
        "uniqueness": 0, "execution": 0, "overall": 0,
        "decision": "", "one_line": "",
        "biggest_risk": "", "biggest_opportunity": "",
        "raw": raw
    }

    for line in raw.split("\n"):
        try:
            if line.startswith("MARKET_SCORE:"):
                score["market"] = int(line.replace("MARKET_SCORE:", "").strip())
            elif line.startswith("COMPETITION_SCORE:"):
                score["competition"] = int(line.replace("COMPETITION_SCORE:", "").strip())
            elif line.startswith("TIMING_SCORE:"):
                score["timing"] = int(line.replace("TIMING_SCORE:", "").strip())
            elif line.startswith("UNIQUENESS_SCORE:"):
                score["uniqueness"] = int(line.replace("UNIQUENESS_SCORE:", "").strip())
            elif line.startswith("EXECUTION_SCORE:"):
                score["execution"] = int(line.replace("EXECUTION_SCORE:", "").strip())
            elif line.startswith("OVERALL_SCORE:"):
                score["overall"] = int(line.replace("OVERALL_SCORE:", "").strip())
            elif line.startswith("DECISION:"):
                score["decision"] = line.replace("DECISION:", "").strip()
            elif line.startswith("ONE_LINE:"):
                score["one_line"] = line.replace("ONE_LINE:", "").strip()
            elif line.startswith("BIGGEST_RISK:"):
                score["biggest_risk"] = line.replace("BIGGEST_RISK:", "").strip()
            elif line.startswith("BIGGEST_OPPORTUNITY:"):
                score["biggest_opportunity"] = line.replace("BIGGEST_OPPORTUNITY:", "").strip()
        except:
            pass

    log(f"✅ Overall score: {score['overall']}/100 — {score['decision']}")
    return score


# ── 4. Investor Memo Writer ──────────────────────────────────
def memo_writer(idea: str, market: dict, competitors: dict,
                score: dict, status_callback=None) -> dict:
    """
    Takes all research + scores and writes a full
    investor-style memo. The kind a VC would read
    before deciding to take a meeting.
    """
    def log(msg):
        if status_callback:
            status_callback(msg)

    log("📝 Writing investor memo...")

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2500,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a principal at a top VC firm writing an investment memo. "
                    "Write a concise, compelling one-page memo a partner would read "
                    "before deciding to take a meeting with this founder.\n\n"
                    "You MUST respond in this exact format:\n\n"
                    "PROBLEM: [What problem does this solve and for whom]\n"
                    "SOLUTION: [What the startup does in 2 sentences]\n"
                    "MARKET: [Market size and why now]\n"
                    "BUSINESS_MODEL: [How it makes money]\n"
                    "COMPETITION: [Competitive landscape and moat]\n"
                    "TRACTION_NEEDED: [What milestones would make this fundable]\n"
                    "RISKS: [Top 3 risks numbered]\n"
                    "THE_ASK: [Suggested seed round size and what it's used for]\n"
                    "VERDICT: [Final 2-sentence recommendation]\n\n"
                    "Write like a partner, not a consultant. Crisp and direct."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Startup idea: '{idea}'\n\n"
                    f"Market: {market['market_size']} | "
                    f"Growth: {market['growth_rate']} | "
                    f"Customer: {market['target_customer']}\n"
                    f"Trends: {market['key_trends']}\n\n"
                    f"Competitors: {competitors['top_competitors']}\n"
                    f"Gap: {competitors['gap_in_market']}\n"
                    f"Differentiation: {competitors['differentiation']}\n\n"
                    f"Scores: Market {score['market']} | "
                    f"Competition {score['competition']} | "
                    f"Timing {score['timing']} | "
                    f"Uniqueness {score['uniqueness']} | "
                    f"Execution {score['execution']}\n"
                    f"Decision: {score['decision']}\n\n"
                    "Write the investment memo."
                )
            }
        ]
    )

    raw = response.choices[0].message.content
    memo = {
        "problem": "", "solution": "", "market": "",
        "business_model": "", "competition": "",
        "traction_needed": "", "risks": "",
        "the_ask": "", "verdict": "",
        "raw": raw
    }

    for line in raw.split("\n"):
        if line.startswith("PROBLEM:"):
            memo["problem"] = line.replace("PROBLEM:", "").strip()
        elif line.startswith("SOLUTION:"):
            memo["solution"] = line.replace("SOLUTION:", "").strip()
        elif line.startswith("MARKET:"):
            memo["market"] = line.replace("MARKET:", "").strip()
        elif line.startswith("BUSINESS_MODEL:"):
            memo["business_model"] = line.replace("BUSINESS_MODEL:", "").strip()
        elif line.startswith("COMPETITION:"):
            memo["competition"] = line.replace("COMPETITION:", "").strip()
        elif line.startswith("TRACTION_NEEDED:"):
            memo["traction_needed"] = line.replace("TRACTION_NEEDED:", "").strip()
        elif line.startswith("RISKS:"):
            memo["risks"] = line.replace("RISKS:", "").strip()
        elif line.startswith("THE_ASK:"):
            memo["the_ask"] = line.replace("THE_ASK:", "").strip()
        elif line.startswith("VERDICT:"):
            memo["verdict"] = line.replace("VERDICT:", "").strip()

    log("✅ Memo written!")
    return memo


# ── 5. Full pipeline ─────────────────────────────────────────
def evaluate_startup(idea: str, status_callback=None) -> dict:
    """
    Runs the complete evaluation pipeline:
    Market → Competitors → Score → Memo
    """
    def log(msg):
        if status_callback:
            status_callback(msg)

    log(f"🚀 Evaluating: *{idea}*")

    market      = market_agent(idea, status_callback)
    competitors = competitor_agent(idea, status_callback)
    score       = scorer_agent(idea, market, competitors, status_callback)
    memo        = memo_writer(idea, market, competitors, score, status_callback)

    return {
        "idea":        idea,
        "market":      market,
        "competitors": competitors,
        "score":       score,
        "memo":        memo
    }


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    idea   = "Uber but for dog walking"
    result = evaluate_startup(idea, status_callback=print)

    s = result["score"]
    m = result["memo"]

    print("\n" + "="*55)
    print("📊 FINAL SCORES")
    print("="*55)
    print(f"Market      : {s['market']}/100")
    print(f"Competition : {s['competition']}/100")
    print(f"Timing      : {s['timing']}/100")
    print(f"Uniqueness  : {s['uniqueness']}/100")
    print(f"Execution   : {s['execution']}/100")
    print(f"OVERALL     : {s['overall']}/100  →  {s['decision']}")
    print(f"\n💬 {s['one_line']}")
    print(f"\n⚠️  Biggest risk        : {s['biggest_risk']}")
    print(f"🚀 Biggest opportunity : {s['biggest_opportunity']}")
    print("\n" + "="*55)
    print("📝 INVESTOR MEMO")
    print("="*55)
    print(f"Problem    : {m['problem']}")
    print(f"Solution   : {m['solution']}")
    print(f"Market     : {m['market']}")
    print(f"Biz model  : {m['business_model']}")
    print(f"Risks      : {m['risks']}")
    print(f"The ask    : {m['the_ask']}")
    print(f"Verdict    : {m['verdict']}")