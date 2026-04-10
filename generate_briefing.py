import anthropic
import os
from datetime import datetime, timezone

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You are a cybersecurity intelligence analyst producing a weekly briefing for senior security and technology leadership. Audience: CISOs, CIOs, senior security leaders. Tone: Concise, authoritative, decision-oriented. Identify the top cybersecurity developments from the last 7 days. Assign a Risk Priority Score (RPS) using formula (S x 0.45) + (E x 0.35) + (X x 0.20). Classify each item as ACT NOW, HEIGHTENED WATCH, or STRATEGIC WATCH. For each item provide title, source, link, published timestamp, RPS, MITRE ATT&CK mapping, and a 3-5 sentence summary. Generate Top 3 Enterprise Risks, an Executive Summary, and Recommended Actions with owners. Output the entire briefing as a self-contained HTML body fragment using clean semantic markup. Do not include html, head, or body tags, just the inner content."""


def generate_briefing():
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": f"Today is {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}. Generate the full weekly CISO briefing for the past 7 days."
            }
        ]
    )
    text_content = ""
    for block in response.content:
        if block.type == "text":
            text_content += block.text
    return text_content


def write_html(content):
    now = datetime.now(timezone.utc)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CISO Weekly Briefing</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 0 auto; padding: 2rem 1rem; color: #1a1a1a; line-height: 1.6; }}
    h1 {{ font-size: 1.5rem; font-weight: 600; border-bottom: 2px solid #e5e5e5; padding-bottom: 0.5rem; }}
    h2 {{ font-size: 1rem; text-transform: uppercase; letter-spacing: 0.05em; color: #666; margin-top: 2rem; }}
    h3 {{ font-size: 1rem; font-weight: 600; margin-bottom: 0.25rem; }}
    .updated {{ font-size: 0.8rem; color: #9ca3af; margin-bottom: 2rem; }}
  </style>
</head>
<body>
  <p class="updated">Last updated: {now.strftime('%B %d, %Y at %H:%M UTC')}</p>
  {content}
</body>
</html>"""
    with open("docs/index.html", "w") as f:
        f.write(html)
    print("Written to docs/index.html")


def main():
    print("Generating briefing...")
    try:
        content = generate_briefing()
        write_html(content)
        print("Done.")
    except Exception as e:
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    main()