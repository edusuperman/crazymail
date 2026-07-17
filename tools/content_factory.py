#!/usr/bin/env python3
"""
Content Factory MVP — 5-stage content pipeline for CrazyMail blogs.

流水线阶段:
    Stage 1: 关键词 → 大纲（MiMo）
    Stage 2: 大纲 → 初稿（MiMo）
    Stage 3: 初稿 → 润色/人味化（MiMo）
    Stage 4: Grok Build 审计修复 + QC 门禁（规则引擎 / 可选 Grok CLI）
    Stage 5: 生成 TSX 路由文件（本地转换）

Usage:
    python tools/content_factory.py "temporary email for verification"
    python tools/content_factory.py -k "temp mail privacy" --lang zh
    python tools/content_factory.py --batch "keyword1" "keyword2" "keyword3"
    python tools/content_factory.py --batch-file keywords.txt
    python tools/content_factory.py "keyword" --use-grok   # Stage 4 启用 Grok CLI 深度修复
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from openai import OpenAI

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
TOOLS = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE_ROUTES = ROOT / "sites" / "site-01" / "frontend" / "src" / "routes"
BLOG_INDEX = SITE_ROUTES / "blog.tsx"

# 导入同目录 grok_audit（Stage 4）
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from grok_audit import (  # noqa: E402
    audit_and_fix_markdown,
    run_grok_cli_fix,
)


# ── API Client ─────────────────────────────────────────────────────────────
def get_client() -> OpenAI:
    """Create MiMo API client using key from OpenCode config."""
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
    """Call MiMo API and return assistant message content."""
    resp = client.chat.completions.create(
        model="mimo-v2.5-pro",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=0.95,
        stream=False,
        extra_body={"enable_thinking": False},
    )
    content = resp.choices[0].message.content
    if not content:
        # MiMo may put output in reasoning_content for some models
        content = getattr(resp.choices[0].message, "reasoning_content", "") or ""
    if not content:
        print("Warning: API returned empty content")
        print(f"  Finish reason: {resp.choices[0].finish_reason}")
    return content or ""


# ── Stage 1: Keyword → Outline ─────────────────────────────────────────────
def stage1_outline(client: OpenAI, keyword: str) -> dict:
    """生成文章大纲（JSON）。"""
    print("[Stage 1/5] Generating outline (MiMo)...")

    system = """You are an SEO content strategist. Return ONLY a valid JSON object. No explanations, no markdown fences, no thinking out loud. Just the JSON.

The JSON must have these fields:
- title: article title with keyword, 50-60 chars
- subtitle: subtitle
- slug: url-friendly-slug (lowercase, hyphens)
- category: one of Guide, Data, Privacy, Industry, AI Tools, Social Media
- primary_keyword: the main keyword
- secondary_keywords: array of 2-3 related keywords
- meta_description: SEO description 150-160 chars
- sections: array of {heading, key_points, data_needed} with 4-6 H2 sections
- faq: array of {q, a} with 3-5 FAQ items
- cta: call to action text

IMPORTANT: Output ONLY the JSON object. Start with { and end with }."""

    user = f"""Create an outline for a blog post about: "{keyword}"

The blog is for tempmails.top, a temporary email service. Include internal links to tempmails.top in the outline."""

    content = call_mimo(client, system, user, max_tokens=8192)

    if not content:
        print("Error: Empty response from API")
        sys.exit(1)

    # Try to extract JSON from response
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        print("Error: Could not parse outline JSON")
        print("Raw response:", content[:500])
        sys.exit(1)


# ── Stage 2: Outline → Draft ───────────────────────────────────────────────
def stage2_draft(client: OpenAI, keyword: str, outline: dict) -> str:
    """根据大纲生成初稿（Markdown）。"""
    print("[Stage 2/5] Writing first draft (MiMo)...")

    system = """You are a privacy protection blogger with 5 years of experience. Write like you're talking to a friend.

Style rules:
- Conversational tone: "Look," / "Here's the thing" / "I've tested this"
- Short paragraphs: 3-5 sentences
- Include at least 1 personal opinion per article
- You MUST write at least 1500 words. Short articles are unacceptable.
- Include at least 2 personal experiences or opinions using phrases like: honestly, in my testing, I have found, here is the thing, let me break this down
- Use lists and tables for clarity
- Identity: TempMails Team (builders of tempmails.top)
- Honest attitude: can recommend own product but disclose it's yours

BANNED phrases (never use these):
- Furthermore, Moreover, In conclusion, It's important to note
- First, Second, Third (as paragraph starters)
- Delve, Tapestry, Leverage, Embark"""

    outline_str = json.dumps(outline, indent=2, ensure_ascii=False)
    user = f"""Write a full blog post based on this outline.

Keyword: "{keyword}"
Outline:
{outline_str}

Requirements:
- 1500-2500 words
- Include internal links to tempmails.top or /
- Include FAQ section
- End with CTA and author bio
- Write in Markdown format"""

    return call_mimo(client, system, user, max_tokens=8192)


# ── Stage 3: Humanize ──────────────────────────────────────────────────────
def stage3_humanize(client: OpenAI, draft: str) -> str:
    """润色初稿，去除 AI 腔。"""
    print("[Stage 3/5] Humanizing (MiMo)...")

    system = """You are an editor who makes AI-written content sound human.

Rules:
- Remove ALL AI-sounding phrases: Furthermore, Moreover, In conclusion, It's important to note, Delve, Tapestry
- You MUST include at least 3 DIFFERENT human markers scattered naturally throughout the article. Use markers like: honestly, I have tested this, here is the thing, let me break this down, in my experience, the bottom line, I have seen this happen, that said, the truth is
- These markers must appear in DIFFERENT sections of the article, not clustered together.
- Vary sentence length — mix short punchy sentences with longer ones
- Use contractions naturally (don't, won't, it's)
- Add occasional em dashes — like this
- Keep the structure and information intact
- Don't add new information, just polish the tone
- Return the polished Markdown only, no commentary"""

    user = f"""Polish this blog post to sound more human and less AI-generated:

{draft}"""

    result = call_mimo(client, system, user, max_tokens=8192)

    # Fallback: if humanized output is too short, use original draft
    if len(result.split()) < 100:
        print(f"  ⚠ Warning: Humanized output only has {len(result.split())} words (< 100). Falling back to original draft.")
        return draft

    return result


# ── Stage 4: Grok Build 审计修复 + QC 门禁 ────────────────────────────────
def stage4_grok_audit(
    article: str,
    keyword: str,
    slug: str = "",
    *,
    use_grok: bool = False,
) -> tuple[str, dict]:
    """
    Stage 4：Grok Build 六维度审计修复（规则引擎，可选 Grok CLI）。

    维度：MD残留 / 事实一致性 / 内链 / 重复内容 / E-E-A-T / CTA

    Returns:
        (fixed_article, audit_result)
    """
    print("[Stage 4/5] Grok Build 审计修复...")

    result = audit_and_fix_markdown(
        article,
        keyword=keyword,
        slug=slug,
        check_duplicates=True,
    )

    if use_grok:
        print("  → 调用 Grok CLI 深度修复...")
        grok = run_grok_cli_fix(result["fixed"], f"humanized-{slug or 'article'}.md")
        if grok.get("success") and grok.get("has_changes"):
            result = audit_and_fix_markdown(
                grok["fixed"],
                keyword=keyword,
                slug=slug,
                check_duplicates=True,
            )
            result["grok_used"] = True
            print("  → Grok CLI 修复已应用并复检")
        else:
            print(f"  → Grok CLI 跳过/失败: {grok.get('error', '无额外修改')}")
            result["grok_used"] = False

    fixed = result["fixed"]
    print(f"  审计结果: {result['overall']}")
    print(f"  修复前问题: {len(result.get('issues_before') or [])}")
    print(f"  修复后问题: {len(result.get('issues_after') or [])}")
    for ch in result.get("changes") or []:
        print(f"    · {ch}")
    if result.get("issues_after"):
        for iss in result["issues_after"][:5]:
            print(f"    ! [{iss.get('severity')}] {iss.get('dimension')}: {iss.get('message', '')[:70]}")

    return fixed, result


def stage4_qc(article: str, keyword: str) -> dict:
    """
    QC 质量门禁（Stage 4 末尾执行）。
    ≤2 项 FAIL 算 PASS，>2 项 FAIL 算 FAIL（与 STRATEGY 一致）。
    """
    print("  [QC] Running quality check...")

    word_count = len(article.split())

    # AI 腔套话
    ai_phrases = [
        "Furthermore", "Moreover", "In conclusion",
        "It's important to note", "It is worth noting",
        "Delve", "Tapestry", "Leverage", "Embark",
    ]
    ai_found = [p for p in ai_phrases if p.lower() in article.lower()]

    # 人味标记
    human_markers = [
        "here's the thing", "honestly", "i've tested",
        "i've found", "in my testing", "look,", "that's it",
        "who cares", "the thing is", "let me break",
        "the bottom line", "i have seen", "that said", "the truth is",
        "i have found", "in my testing", "let me break this down",
        "here is the thing", "i have tested", "who cares",
    ]
    human_found = [m for m in human_markers if m.lower() in article.lower()]

    # H2 数量
    h2_count = len(re.findall(r"^##\s", article, re.MULTILINE))

    # 内链
    internal_links = re.findall(
        r"tempmails\.top|href=['\"]/", article, re.IGNORECASE
    )

    # 关键词出现次数
    kw_count = article.lower().count(keyword.lower())

    checks = {
        "word_count": {"value": word_count, "pass": 1200 <= word_count <= 3500},
        "ai_phrases": {"value": len(ai_found), "found": ai_found, "pass": len(ai_found) == 0},
        "human_markers": {"value": len(human_found), "found": human_found, "pass": len(human_found) >= 2},
        "h2_count": {"value": h2_count, "pass": h2_count >= 3},
        "internal_links": {"value": len(internal_links), "pass": len(internal_links) >= 1},
        "keyword_occurrences": {"value": kw_count, "pass": kw_count >= 2},
    }

    fail_count = sum(1 for c in checks.values() if not c["pass"])
    all_pass = fail_count <= 2

    return {
        "keyword": keyword,
        "timestamp": datetime.now().isoformat(),
        "overall": "PASS" if all_pass else "FAIL",
        "fail_count": fail_count,
        "checks": checks,
    }


# ── Stage 5: Generate TSX Route File ───────────────────────────────────────
def md_to_jsx(md: str) -> str:
    """Convert Markdown to JSX for the blog post body."""
    lines = md.split("\n")
    jsx_lines = []
    in_list = False
    in_table = False
    table_rows = []

    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            if in_list:
                jsx_lines.append("        </ul>")
                in_list = False
            if in_table:
                jsx_lines.extend(_render_table(table_rows))
                table_rows = []
                in_table = False
            jsx_lines.append("")
            continue

        # H2
        if stripped.startswith("## ") and not stripped.startswith("### "):
            if in_list:
                jsx_lines.append("        </ul>")
                in_list = False
            heading = _inline_format(stripped[3:])
            jsx_lines.append(f'        <h2 className="mt-12 text-2xl font-bold">{heading}</h2>')
            continue

        # H3
        if stripped.startswith("### "):
            if in_list:
                jsx_lines.append("        </ul>")
                in_list = False
            heading = _inline_format(stripped[4:])
            jsx_lines.append(f'        <h3 className="mt-8 text-xl font-semibold">{heading}</h3>')
            continue

        # Unordered list
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                jsx_lines.append('        <ul className="my-4 space-y-1">')
                in_list = True
            item = _inline_format(stripped[2:])
            jsx_lines.append(f"          <li>{item}</li>")
            continue

        # Ordered list (treat as ul for simplicity)
        if re.match(r"^\d+\.\s", stripped):
            if not in_list:
                jsx_lines.append('        <ul className="my-4 space-y-1 list-decimal list-inside">')
                in_list = True
            item = _inline_format(re.sub(r"^\d+\.\s", "", stripped))
            jsx_lines.append(f"          <li>{item}</li>")
            continue

        # Table row
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
            # Skip separator rows
            if re.match(r"^\|[\s\-:|]+\|$", stripped):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            table_rows.append(cells)
            continue

        # Close list if we hit non-list content
        if in_list:
            jsx_lines.append("        </ul>")
            in_list = False

        # Regular paragraph
        formatted = _inline_format(stripped)
        jsx_lines.append(f"        <p>{formatted}</p>")

    # Close any open list
    if in_list:
        jsx_lines.append("        </ul>")

    return "\n".join(jsx_lines)


def _inline_format(text: str) -> str:
    """Convert inline Markdown to JSX."""
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Links
    text = re.sub(
        r"\[(.+?)\]\((.+?)\)",
        r'<a href="\2" target="_blank" rel="noopener noreferrer" className="text-primary underline">\1</a>',
        text,
    )
    # Inline code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def _render_table(rows: list[list[str]]) -> list[str]:
    """Render table rows as JSX."""
    if not rows:
        return []

    result = [
        '        <div className="my-6 overflow-x-auto">',
        '          <table className="w-full border-collapse text-sm">',
    ]

    # First row as header
    header = rows[0]
    result.append("            <thead>")
    result.append("              <tr>")
    for cell in header:
        result.append(f'                <th className="border border-border px-4 py-2 text-left font-semibold">{_inline_format(cell)}</th>')
    result.append("              </tr>")
    result.append("            </thead>")

    # Body rows
    if len(rows) > 1:
        result.append("            <tbody>")
        for row in rows[1:]:
            result.append("              <tr>")
            for cell in row:
                result.append(f'                <td className="border border-border px-4 py-2">{_inline_format(cell)}</td>')
            result.append("              </tr>")
        result.append("            </tbody>")

    result.append("          </table>")
    result.append("        </div>")
    return result


def stage5_tsx(outline: dict, article_md: str) -> str:
    """根据大纲与审计后正文生成 TanStack 路由 TSX。"""
    print("[Stage 5/5] Generating TSX route file...")

    slug = outline["slug"]
    title = outline["title"]
    subtitle = outline.get("subtitle", "")
    meta_desc = outline["meta_description"]
    keywords = ", ".join(
        [outline["primary_keyword"]] + outline.get("secondary_keywords", [])
    )
    category = outline.get("category", "Guide")
    today = datetime.now().strftime("%Y-%m-%d")
    read_time = f"{max(1, len(article_md.split()) // 200)} min read"

    # Extract CTA from outline
    cta = outline.get("cta", "Get Your Temporary Email →")

    # Extract FAQ from outline
    faq_items = outline.get("faq", [])

    # Build JSX body
    body_jsx = md_to_jsx(article_md)

    # Build FAQ JSX
    faq_jsx = ""
    if faq_items:
        faq_jsx = '\n        <h2 className="mt-12 text-2xl font-bold">FAQ</h2>\n'
        for item in faq_items:
            q = item.get("q", "").replace('"', '\\"')
            a = item.get("a", "").replace('"', '\\"')
            faq_jsx += f"""        <h3 className="mt-8 text-xl font-semibold">{q}</h3>
        <p>{a}</p>
"""

    tsx = f'''import {{ createFileRoute, Link }} from "@tanstack/react-router";

export const Route = createFileRoute("/blog/{slug}")({{
  head: () => ({{
    meta: [
      {{ title: "{title} - TempMails.top" }},
      {{ name: "description", content: "{meta_desc}" }},
      {{ name: "keywords", content: "{keywords}" }},
      {{ name: "author", content: "TempMails Team" }},
      {{ name: "robots", content: "index, follow" }},
      {{ property: "og:type", content: "article" }},
      {{ property: "og:title", content: "{title}" }},
      {{ property: "og:description", content: "{meta_desc}" }},
      {{ property: "og:url", content: "https://tempmails.top/blog/{slug}" }},
    ],
    links: [
      {{ rel: "canonical", href: "https://tempmails.top/blog/{slug}" }},
    ],
    scripts: [
      {{
        type: "application/ld+json",
        children: JSON.stringify({{
          "@context": "https://schema.org",
          "@type": "Article",
          "headline": "{title}",
          "description": "{meta_desc}",
          "author": {{ "@type": "Organization", "name": "TempMails Team" }},
          "datePublished": "{today}",
          "dateModified": "{today}",
          "publisher": {{ "@type": "Organization", "name": "TempMails.top" }},
        }}),
      }},
    ],
  }}),
  component: BlogPostPage,
}});

function BlogPostPage() {{
  return (
    <article className="mx-auto max-w-3xl px-4 py-16">
      <Link to="/blog" className="mb-8 inline-flex items-center text-sm text-primary hover:underline">
        ← Back to Blog
      </Link>

      <header className="mb-10">
        <span className="mb-4 inline-block rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
          {category}
        </span>
        <h1 className="text-3xl font-bold leading-tight tracking-tight md:text-4xl">
          {title}
          <span className="mt-2 block text-xl font-normal text-muted-foreground">
            {subtitle}
          </span>
        </h1>
        <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
          <span>By TempMails Team</span>
          <span>·</span>
          <time>{today}</time>
          <span>·</span>
          <span>{read_time}</span>
        </div>
      </header>

      <div className="prose prose-gray prose-lg max-w-none">
{body_jsx}
{faq_jsx}
        <div className="mt-12 rounded-lg bg-primary/5 p-8 text-center">
          <h3 className="text-xl font-semibold">Protect Your Real Email Today</h3>
          <p className="mt-2 text-muted-foreground">
            Get a free temporary email address in seconds. No registration, no tracking.
          </p>
          <Link
            to="/"
            className="mt-4 inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            {cta}
          </Link>
        </div>

        <div className="mt-12 flex items-start gap-4 rounded-lg border border-border p-6">
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xl font-bold text-primary">
            TM
          </div>
          <div>
            <p className="font-semibold">TempMails Team</p>
            <p className="text-sm text-muted-foreground">
              We build TempMails.top — a free, ad-free, privacy-first temporary email service.
              We write about email privacy and online security.
            </p>
          </div>
        </div>
      </div>
    </article>
  );
}}
'''
    return tsx


# ── Update blog.tsx index ──────────────────────────────────────────────────
def update_blog_index(outline: dict):
    """Add new post entry to blog.tsx blogPosts array."""
    print("  Updating blog.tsx index...")

    slug = outline["slug"]
    title = outline["title"]
    meta_desc = outline["meta_description"]
    category = outline.get("category", "Guide")
    today = datetime.now().strftime("%Y-%m-%d")
    word_count = 1800  # approximate
    read_time = f"{max(1, word_count // 200)} min read"

    content = BLOG_INDEX.read_text(encoding="utf-8")

    # Check if slug already exists
    if f'slug: "{slug}"' in content:
        print(f"  Slug '{slug}' already exists in blog.tsx, skipping.")
        return

    # Build new entry
    new_entry = f"""  {{
    slug: "{slug}",
    title: "{title}",
    excerpt: "{meta_desc[:120]}...",
    date: "{today}",
    readTime: "{read_time}",
    category: "{category}",
  }},"""

    # Insert before the closing ];
    content = content.replace(
        "];",
        f"{new_entry}\n];",
        1,
    )

    BLOG_INDEX.write_text(content, encoding="utf-8")
    print("  blog.tsx updated.")


# ── Main Pipeline ──────────────────────────────────────────────────────────
def run_pipeline(keyword: str, *, use_grok: bool = False):
    """运行完整 5 阶段内容流水线。"""
    print(f"\n{'='*60}")
    print(f"Content Factory MVP")
    print(f"Keyword: {keyword}")
    if use_grok:
        print("Stage 4: Grok CLI 深度修复 = ON")
    print(f"{'='*60}\n")

    # Ensure output dirs exist
    DOCS.mkdir(exist_ok=True)

    client = get_client()

    # Stage 1: Outline（MiMo）
    outline = stage1_outline(client, keyword)
    slug = outline["slug"]
    outline_path = DOCS / f"outline-{slug}.json"
    outline_path.write_text(json.dumps(outline, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  → {outline_path}")

    # Stage 2: Draft（MiMo）
    draft = stage2_draft(client, keyword, outline)
    draft_path = DOCS / f"draft-{slug}.md"
    draft_path.write_text(draft, encoding="utf-8")
    print(f"  → {draft_path}")

    # Stage 3: Humanize（MiMo）
    humanized = stage3_humanize(client, draft)
    humanized_path = DOCS / f"humanized-{slug}.md"
    humanized_path.write_text(humanized, encoding="utf-8")
    print(f"  → {humanized_path}")

    # Stage 4a: Grok Build 审计修复
    audited, audit_result = stage4_grok_audit(
        humanized,
        keyword,
        slug=slug,
        use_grok=use_grok,
    )
    audited_path = DOCS / f"audited-{slug}.md"
    audited_path.write_text(audited, encoding="utf-8")
    print(f"  → {audited_path}")

    audit_report_path = DOCS / f"audit-{slug}.json"
    audit_report_path.write_text(
        json.dumps(audit_result.get("report", audit_result), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  → {audit_report_path}")

    # Stage 4b: QC 门禁（对审计后正文）
    qc_report = stage4_qc(audited, keyword)
    # 若审计仍有 high 级问题未修掉，强制 QC FAIL
    if audit_result.get("overall") == "FAIL":
        qc_report["overall"] = "FAIL"
        qc_report["fail_count"] = qc_report.get("fail_count", 0) + 1
        qc_report["audit_gate"] = "FAIL"
        print("  ⚠ 审计仍有 high 级问题 → QC 门禁 FAIL")
    else:
        qc_report["audit_gate"] = audit_result.get("overall", "PASS")

    qc_path = DOCS / f"qc-{slug}.json"
    qc_path.write_text(json.dumps(qc_report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  → {qc_path}")
    print(f"  QC Result: {qc_report['overall']}")
    for name, check in qc_report["checks"].items():
        status = "PASS" if check["pass"] else "FAIL"
        print(f"    {name}: {check['value']} [{status}]")

    # Stage 5: TSX（QC 通过才输出）
    tsx_path = None
    if qc_report["overall"] == "FAIL":
        print("\n  ✖ QC FAILED — 跳过 TSX 生成。请修复问题后重试。")
        print(f"    Run: python tools/content_factory.py \"{keyword}\"")
    else:
        tsx_content = stage5_tsx(outline, audited)
        tsx_path = SITE_ROUTES / f"blog.{slug}.tsx"
        tsx_path.write_text(tsx_content, encoding="utf-8")
        print(f"  → {tsx_path}")

        # 更新博客列表
        update_blog_index(outline)

    print(f"\n{'='*60}")
    print("Pipeline complete!")
    print(f"  Outline:    {outline_path}")
    print(f"  Draft:      {draft_path}")
    print(f"  Humanized:  {humanized_path}")
    print(f"  Audited:    {audited_path} ({audit_result.get('overall')})")
    print(f"  Audit:      {audit_report_path}")
    print(f"  QC:         {qc_path} ({qc_report['overall']})")
    if qc_report["overall"] == "PASS":
        print(f"  TSX:        {tsx_path}")
    else:
        print(f"  TSX:        SKIPPED (QC FAIL)")
    print(f"{'='*60}\n")

    return qc_report["overall"]


# ── Batch Mode ──────────────────────────────────────────────────────────────
def run_batch(
    keywords: list[str],
    lang: str = "en",
    *,
    use_grok: bool = False,
) -> list[dict]:
    """按关键词顺序跑完整流水线。

    Returns a list of result dicts with keys: keyword, status, error.
    """
    results = []
    total = len(keywords)

    print(f"\n{'='*60}")
    print(f"Content Factory — Batch Mode")
    print(f"Keywords to process: {total}")
    print(f"Language: {lang}")
    if use_grok:
        print("Stage 4: Grok CLI = ON")
    print(f"{'='*60}\n")

    for i, kw in enumerate(keywords, 1):
        print(f"\n[{i}/{total}] Processing: {kw}")
        print(f"{'─'*60}")
        try:
            status = run_pipeline(kw, use_grok=use_grok)
            results.append({"keyword": kw, "status": status, "error": None})
        except Exception as e:
            print(f"  ✖ ERROR: {e}")
            results.append({"keyword": kw, "status": "ERROR", "error": str(e)})

    # Summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    print(f"\n{'='*60}")
    print(f"Batch Summary")
    print(f"{'='*60}")
    print(f"  Attempted: {total}")
    print(f"  PASS:      {passed}")
    print(f"  FAIL:      {failed}")
    if errors:
        print(f"  ERROR:     {errors}")
    print()
    for r in results:
        marker = "✔" if r["status"] == "PASS" else "✖"
        extra = f" ({r['error']})" if r["error"] else ""
        print(f"  {marker} [{r['status']}] {r['keyword']}{extra}")
    print(f"{'='*60}\n")

    return results


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Content Factory MVP — 5-stage blog content pipeline "
                    "(含 Stage 4 Grok Build 审计修复)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python tools/content_factory.py "temporary email for verification"
  python tools/content_factory.py -k "temp mail privacy" --lang zh
  python tools/content_factory.py --batch "keyword1" "keyword2" "keyword3"
  python tools/content_factory.py --batch-file keywords.txt
  python tools/content_factory.py "keyword" --use-grok
        """,
    )
    parser.add_argument(
        "keyword",
        nargs="?",
        help="Target keyword for the blog post",
    )
    parser.add_argument(
        "-k", "--keyword-alt",
        help="Alternative way to specify keyword",
    )
    parser.add_argument(
        "--lang",
        default="en",
        help="Language (default: en)",
    )
    parser.add_argument(
        "--batch",
        nargs="+",
        metavar="KEYWORD",
        help="Run pipeline for multiple keywords sequentially",
    )
    parser.add_argument(
        "--batch-file",
        metavar="FILE",
        help="Read keywords from a text file (one per line)",
    )
    parser.add_argument(
        "--use-grok",
        action="store_true",
        help="Stage 4 在规则修复后调用 Grok CLI 深度修复（较慢）",
    )

    args = parser.parse_args()

    # Batch file mode
    if args.batch_file:
        batch_path = Path(args.batch_file)
        if not batch_path.exists():
            parser.error(f"Batch file not found: {args.batch_file}")
        keywords = [
            line.strip()
            for line in batch_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        if not keywords:
            parser.error(f"No keywords found in {args.batch_file}")
        results = run_batch(keywords, lang=args.lang, use_grok=args.use_grok)
        sys.exit(0 if all(r["status"] == "PASS" for r in results) else 1)

    # Batch inline mode
    if args.batch:
        results = run_batch(args.batch, lang=args.lang, use_grok=args.use_grok)
        sys.exit(0 if all(r["status"] == "PASS" for r in results) else 1)

    # Single keyword mode
    keyword = args.keyword or args.keyword_alt
    if not keyword:
        parser.error("Please provide a keyword, e.g.: python tools/content_factory.py \"temporary email\"")

    result = run_pipeline(keyword, use_grok=args.use_grok)
    sys.exit(0 if result == "PASS" else 1)


if __name__ == "__main__":
    main()
