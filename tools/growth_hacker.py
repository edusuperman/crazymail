#!/usr/bin/env python3
"""
Growth Hacker Tool — Generate platform-specific promotional content for CrazyMail.

Usage:
    python tools/growth_hacker.py --article "temporary email for verification"
    python tools/growth_hacker.py --keyword "is temporary email safe"
    python tools/growth_hacker.py --directories
    python tools/growth_hacker.py --calendar 14
    python tools/growth_hacker.py --all
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


# ── API Client ──────────────────────────────────────────────────────────────
def get_client() -> OpenAI:
    config_path = Path.home() / ".config" / "opencode" / "opencode.json"
    if not config_path.exists():
        print(f"Error: OpenCode config not found at {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    api_key = (
        config.get("provider", {}).get("mimo", {}).get("options", {}).get("apiKey")
    )
    if not api_key:
        print("Error: provider.mimo.options.apiKey not found in opencode.json")
        sys.exit(1)

    return OpenAI(
        api_key=api_key,
        base_url="https://api.xiaomimimo.com/v1",
        default_headers={"api-key": api_key},
    )


def call_mimo(client: OpenAI, system: str, user: str, max_tokens: int = 4096) -> str:
    resp = client.chat.completions.create(
        model="mimo-v2.5-pro",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_completion_tokens=max_tokens,
        temperature=0.7,
        top_p=0.95,
        stream=False,
    )
    content = resp.choices[0].message.content
    if not content:
        content = getattr(resp.choices[0].message, "reasoning_content", "") or ""
    if not content:
        print("Warning: API returned empty content")
        print(f"  Finish reason: {resp.choices[0].finish_reason}")
    return content or ""


# ── Context Loader ──────────────────────────────────────────────────────────
def load_blog_context(keyword: str) -> str:
    site_routes = ROOT / "sites" / "site-01" / "frontend" / "src" / "routes"
    blog_files = list(site_routes.glob("blog.*.tsx"))
    if not blog_files:
        return ""

    relevant = []
    kw_lower = keyword.lower()
    for f in blog_files:
        content = f.read_text(encoding="utf-8")
        if kw_lower in content.lower() or f.stem.replace("blog.", "") in kw_lower.replace(" ", "-"):
            relevant.append((f.stem, content[:2000]))

    if not relevant:
        for f in blog_files[:3]:
            content = f.read_text(encoding="utf-8")
            relevant.append((f.stem, content[:1500]))

    parts = []
    for name, excerpt in relevant[:5]:
        parts.append(f"### {name}\n{excerpt}\n")
    return "\n".join(parts)


# ── Reddit Post ─────────────────────────────────────────────────────────────
def generate_reddit(client: OpenAI, keyword: str, context: str) -> str:
    print("[Reddit] Generating post...")

    system = """You are a privacy-conscious Reddit user who contributes genuinely to communities like r/privacy, r/cybersecurity, r/privacytoolsIO, and r/onlinSecurity.

Rules:
- Write like a real Reddit user, NOT a marketer
- Title: question-based or data-driven, no sales pitch
- Body: share genuine experience, data, or tips; mention tempmails.top naturally at the end as one option among several
- Include 2-3 actionable tips that stand on their own
- End with a soft mention: "I've been using tempmails.top for this, but there are other options too"
- Use Reddit markdown formatting
- Keep it under 500 words
- Sound like you're genuinely trying to help, not sell

BANNED:
- "Furthermore", "Moreover", "In conclusion"
- Overly promotional language
- Fake statistics"""

    user = f"""Generate a Reddit post about: "{keyword}"

Available blog context for reference:
{context if context else "No specific blog context available. Write based on general knowledge about temporary email."}

Output format:
1. Post title (one line)
2. Subreddit recommendation
3. Full post body in Reddit markdown

Make it sound like a real person sharing their experience."""

    return call_mimo(client, system, user, max_tokens=2048)


# ── Hacker News Post ────────────────────────────────────────────────────────
def generate_hackernews(client: OpenAI, keyword: str, context: str) -> str:
    print("[Hacker News] Generating post...")

    system = """You are a technical founder presenting on Hacker News. Write a Show HN post.

Rules:
- Title: concise, technical, data-driven (e.g., "Show HN: TempMails – Disposable email with zero tracking")
- Body: explain the technical approach, what problem it solves, what makes it different
- Include technical details: architecture choices, privacy guarantees, performance
- Be honest about limitations
- Keep it under 400 words
- Sound like a builder, not a marketer
- Use plain text, no markdown formatting (HN uses plain text)

BANNED:
- Marketing speak: "revolutionary", "game-changing", "cutting-edge"
- "Furthermore", "Moreover", "In conclusion"
- Vague claims without specifics"""

    user = f"""Generate a Show HN post about: "{keyword}"

Available blog context:
{context if context else "No specific blog context. Write based on general knowledge about temporary email services."}

Output format:
1. Show HN title
2. Post body (plain text, technical)
3. First comment (self-reply with additional technical details or FAQ)"""

    return call_mimo(client, system, user, max_tokens=2048)


# ── Twitter/X Thread ────────────────────────────────────────────────────────
def generate_twitter(client: OpenAI, keyword: str, context: str) -> str:
    print("[Twitter/X] Generating thread...")

    system = """You are a privacy advocate on Twitter/X. Write a thread about temporary email.

Rules:
- Tweet 1 (hook): under 280 chars, attention-grabbing, include a stat or surprising fact
- Tweets 2-6: one tip or insight per tweet, under 280 chars each
- Tweet 7 (final): CTA mentioning tempmails.top
- Use thread numbering (1/, 2/, etc.)
- Include 1-2 relevant hashtags in the final tweet only
- Use line breaks between tweets
- Sound conversational, not corporate

BANNED:
- "Thread 🧵" opener (overused)
- "Furthermore", "Moreover"
- Excessive emojis
- Generic advice like "stay safe online" """

    user = f"""Generate a Twitter/X thread about: "{keyword}"

Blog context:
{context if context else "No specific blog context available."}

Create a 7-tweet thread. Each tweet must be under 280 characters."""

    return call_mimo(client, system, user, max_tokens=2048)


# ── LinkedIn Post ───────────────────────────────────────────────────────────
def generate_linkedin(client: OpenAI, keyword: str, context: str) -> str:
    print("[LinkedIn] Generating post...")

    system = """You are a cybersecurity professional on LinkedIn sharing insights about email privacy.

Rules:
- Professional tone but not boring
- Start with a hook: a question, stat, or bold statement
- Share a professional insight or observation
- Include 3-5 bullet points with actionable advice
- End with a question to drive engagement
- Mention tempmails.top as one resource among several
- Use LinkedIn formatting: short paragraphs, line breaks, bullet points
- 300-500 words

BANNED:
- "I'm thrilled to announce"
- "Furthermore", "Moreover", "In conclusion"
- Generic inspirational quotes
- Overly corporate language"""

    user = f"""Generate a LinkedIn post about: "{keyword}"

Blog context:
{context if context else "No specific blog context available."}

Make it professional but engaging. Include a hook, insights, and end with a discussion question."""

    return call_mimo(client, system, user, max_tokens=2048)


# ── Directory Submissions ───────────────────────────────────────────────────
def generate_directories(client: OpenAI, keyword: str) -> str:
    print("[Directories] Generating submission templates...")

    system = """You are preparing directory submission templates for tempmails.top, a temporary email service.

Generate submission content for each directory below. Each submission should be tailored to that platform's style and requirements.

Rules:
- Be factual and specific
- Highlight different aspects for different directories
- Include all required fields
- Keep descriptions within typical character limits
- No marketing fluff, just clear value propositions"""

    user = f"""Generate directory submission templates for tempmails.top.

Primary keyword: "{keyword}"

Create submissions for these directories:

1. **Product Hunt**
   - Tagline (60 chars max)
   - Description (260 chars max)
   - First maker comment
   - Topics/tags

2. **AlternativeTo**
   - Name
   - Short description
   - Full description
   - Category
   - Platforms
   - Tags

3. **SaaSHub**
   - Name
   - Tagline
   - Description
   - Category
   - Features list (5-8 items)
   - Pricing

4. **ToolFinder**
   - Name
   - Description
   - Category
   - Key features

5. **Other relevant directories** (list 3-5 more temp email directories with submission guidance)

Format each as a clear, copy-paste-ready template."""

    return call_mimo(client, system, user, max_tokens=4096)


# ── Content Calendar ────────────────────────────────────────────────────────
def generate_calendar(client: OpenAI, keyword: str, days: int = 14) -> str:
    print(f"[Calendar] Generating {days}-day content calendar...")

    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d (%A)") for i in range(days)]

    system = """You are a growth hacker creating a content calendar for a temporary email service (tempmails.top).

Rules:
- 1-2 actions per day
- Rotate platforms: Reddit, Hacker News, Twitter/X, LinkedIn, directories, blog comments, forums
- Rotate content types: new posts, comments on existing threads, directory submissions, engagement activities
- Include specific subreddits, forums, and communities to target
- Each action should have: platform, action type, content description, estimated time
- Weekend actions should be lighter
- Week 2 should include follow-up actions from Week 1"""

    user = f"""Generate a {days}-day content calendar starting from {dates[0]}.

Primary keyword: "{keyword}"

Dates to plan for:
{chr(10).join(dates)}

Format as a markdown table with columns:
| Date | Platform | Action | Content/Topic | Time Est. |

Include notes at the bottom about:
- Which posts to revisit for engagement
- Best times to post per platform
- Key metrics to track"""

    return call_mimo(client, system, user, max_tokens=4096)


# ── Output Writer ───────────────────────────────────────────────────────────
def get_output_dir() -> Path:
    date_str = datetime.now().strftime("%Y%m%d")
    output_dir = DOCS / f"growth-content-{date_str}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_output(output_dir: Path, filename: str, content: str):
    filepath = output_dir / filename
    filepath.write_text(content, encoding="utf-8")
    print(f"  → {filepath}")


# ── Main Pipeline ───────────────────────────────────────────────────────────
def run_all(client: OpenAI, keyword: str, days: int = 14):
    print(f"\n{'='*60}")
    print(f"Growth Hacker Tool")
    print(f"Keyword: {keyword}")
    print(f"{'='*60}\n")

    output_dir = get_output_dir()
    context = load_blog_context(keyword)

    reddit = generate_reddit(client, keyword, context)
    write_output(output_dir, "reddit-post.md", reddit)

    hn = generate_hackernews(client, keyword, context)
    write_output(output_dir, "hackernews-post.md", hn)

    twitter = generate_twitter(client, keyword, context)
    write_output(output_dir, "twitter-thread.md", twitter)

    linkedin = generate_linkedin(client, keyword, context)
    write_output(output_dir, "linkedin-post.md", linkedin)

    dirs = generate_directories(client, keyword)
    write_output(output_dir, "directory-submissions.md", dirs)

    calendar = generate_calendar(client, keyword, days)
    write_output(output_dir, "content-calendar.md", calendar)

    print(f"\n{'='*60}")
    print(f"All content generated in: {output_dir}")
    print(f"{'='*60}\n")
    return output_dir


def run_article(client: OpenAI, keyword: str):
    print(f"\n{'='*60}")
    print(f"Growth Hacker — Article Mode")
    print(f"Keyword: {keyword}")
    print(f"{'='*60}\n")

    output_dir = get_output_dir()
    context = load_blog_context(keyword)

    reddit = generate_reddit(client, keyword, context)
    write_output(output_dir, "reddit-post.md", reddit)

    hn = generate_hackernews(client, keyword, context)
    write_output(output_dir, "hackernews-post.md", hn)

    twitter = generate_twitter(client, keyword, context)
    write_output(output_dir, "twitter-thread.md", twitter)

    linkedin = generate_linkedin(client, keyword, context)
    write_output(output_dir, "linkedin-post.md", linkedin)

    print(f"\n{'='*60}")
    print(f"Social posts generated in: {output_dir}")
    print(f"{'='*60}\n")
    return output_dir


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Growth Hacker Tool — Generate platform-specific promotional content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python tools/growth_hacker.py --article "temporary email for verification"
  python tools/growth_hacker.py --keyword "is temporary email safe"
  python tools/growth_hacker.py --directories
  python tools/growth_hacker.py --calendar 14
  python tools/growth_hacker.py --all
        """,
    )
    parser.add_argument(
        "--article",
        help="Blog article keyword to generate social posts for",
    )
    parser.add_argument(
        "--keyword",
        help="Keyword/topic to generate content around",
    )
    parser.add_argument(
        "--directories",
        action="store_true",
        help="Generate directory submission templates",
    )
    parser.add_argument(
        "--calendar",
        type=int,
        nargs="?",
        const=14,
        help="Generate content calendar (default: 14 days)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all content (social posts + directories + calendar)",
    )

    args = parser.parse_args()

    if not any([args.article, args.keyword, args.directories, args.calendar, args.all]):
        parser.error("Provide at least one option. Use --help for usage.")

    client = get_client()

    keyword = args.keyword or args.article or "temporary email"

    if args.all:
        run_all(client, keyword, days=args.calendar or 14)
    else:
        if args.article:
            run_article(client, keyword)
        elif args.keyword:
            run_article(client, keyword)

        if args.directories:
            output_dir = get_output_dir()
            dirs = generate_directories(client, keyword)
            write_output(output_dir, "directory-submissions.md", dirs)

        if args.calendar is not None:
            output_dir = get_output_dir()
            days = args.calendar if args.calendar > 0 else 14
            cal = generate_calendar(client, keyword, days)
            write_output(output_dir, "content-calendar.md", cal)


if __name__ == "__main__":
    main()
