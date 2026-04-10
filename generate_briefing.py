import anthropic
import os
from datetime import datetime, timezone

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """CONTEXT:
You are a cybersecurity intelligence analyst producing a weekly briefing for senior security and technology leadership.

Audience: CISOs, CIOs, senior security leaders
Tone: Concise, authoritative, decision-oriented
Objective: Deliver a high-signal briefing covering the last 7 days, prioritized by enterprise impact, with explicit risk scoring, ATT&CK mapping, and executable actions.

CONTEXT:
You are a cybersecurity intelligence analyst producing a weekly briefing for senior security and technology leadership.

Audience: CISOs, CIOs, senior security leaders
Tone: Concise, authoritative, decision-oriented
Objective: Deliver a high-signal briefing covering the last 7 days, prioritized by enterprise impact, with explicit risk scoring, ATT&CK mapping, and executable actions.

TASK:
1. Identify the top cybersecurity developments from the last 7 days.
   - Prefer primary sources and independent confirmation when multiple sources cover the same event.
   - Target 5–10 items, but return fewer if fewer meet the quality bar.
   - Rank by:
     1) Enterprise impact
     2) Exploitability
     3) Exposure breadth
     4) Source credibility
     5) Novelty (deduplicate overlapping coverage)

2. Assign a Risk Priority Score (RPS) to each item:
   - Severity (S) 1–5
   - Exploitability (E) 1–5
   - Exposure (X) 1–5
   - Formula: (S × 0.45) + (E × 0.35) + (X × 0.20)
   - Round to 1 decimal
   - Calibration:
     - 4.5–5.0 = widespread, actively exploited, or trivial to exploit
     - 3.5–4.4 = high enterprise relevance with narrower or less-confirmed scope
     - 2.5–3.4 = moderate or situational impact
     - <2.5 = exclude unless strategically important

3. Classify each item:
   - ACT NOW = immediate mitigation or validation needed
   - HEIGHTENED WATCH = credible risk; monitor or prepare
   - STRATEGIC WATCH = structural shift with longer-term implications

4. For each selected item, provide:
   - Title
   - Source
   - Link
   - Published timestamp
   - RPS with inline breakdown: S/E/X
   - MITRE ATT&CK mapping: 1–3 relevant techniques only when meaningful; label "Analyst-mapped" if inferred
   - Summary in 3–5 sentences covering:
     - confirmed facts vs unconfirmed claims
     - enterprise relevance
     - likely risk pathway
     - what leadership should do

5. Generate Top 3 Enterprise Risks Today:
   - Risks must be conditions or patterns, not article headlines
   - 1–2 sentences each
   - Must synthesize across multiple items where possible

6. Generate Executive Summary:
   - 1–2 paragraphs covering:
     - attack patterns across the 7-day window
     - changes in attacker behavior or tactics
     - systemic enterprise weaknesses exposed
     - implications for leadership

7. Generate Recommended Actions:
   - ACT NOW = executable in 24–72 hours
   - WATCH = validation, monitoring, readiness, threat modeling
   - STRATEGIC = roadmap, control uplift, architecture, or investment decisions
   - Every action must name an owner function (e.g., SOC, IAM, Platform, AppSec)

CONSTRAINTS:
- Use only credible, verifiable sources; prefer top-tier reporting, official advisories, and major vendor research
- Enforce a strict 7-day freshness window
- Prioritize the most recent and highest-impact items within that window
- If an item is near the cutoff, label: Freshness note: near 7-day boundary
- Do not pad results if fewer than 5 strong items exist
- No duplicate events across sources unless a second source adds materially new information
- No fabricated data, links, scores, or ATT&CK mappings
- Clearly separate confirmed facts, source claims, and analyst inference
- Use ATT&CK only when it adds precision; do not force mapping
- Prefer technique-level specificity (e.g., T1059) over vague tactic labels
- Avoid generic language, fluff, and beginner explanations
- Output must be immediately usable without editing

OUTPUT FORMAT:

Section 1: Top 3 Enterprise Risks Today
1. ...
2. ...
3. ...

Section 2: Executive Summary
- 1–2 paragraphs

Section 3: CISO Briefing

ACT NOW:
1. Title
   - Source:
   - Published:
   - Link:
   - RPS:
   - ATT&CK:
   - Summary:

HEIGHTENED WATCH:
1. ...

STRATEGIC WATCH:
1. ...

Section 4: Recommended Actions

ACT NOW:
- Action (Owner: <function>)

WATCH:
- Action (Owner: <function>)

STRATEGIC:
- Action (Owner: <function>)

QUALITY BAR:
- Every item must answer:
  - What happened
  - Why it matters
  - What leadership should do
- Output must be scannable in under 2 minutes
- RPS must be applied consistently
- ATT&CK must clarify, not clutter
- Top 3 Risks must synthesize beyond headlines
- Maximize signal density; avoid redundancy
"""

def generate_briefing():
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": f"Today is {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}. Generate the full weekly CISO briefing for the past 7 days following the output format specified. Output the entire briefing as a self-contained HTML body fragment using clean semantic markup. Do not include html, head, or body tags, just the inner content."
            }
        ]
    )
    text_content = ""
    for block in response.content:
        if block.t