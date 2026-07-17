#!/usr/bin/env python3
"""
Grok Build 内容审计修复工具 — CrazyMail 内容工厂质量门禁

审计维度（来自 docs/grok-audit-report.md / docs/FULL_REPAIR_PLAN.md）:
1. MD残留：未转换的 Markdown 语法
2. 事实一致性：产品信息（品牌、域名、保留时长）是否一致
3. 内链缺失：是否有合适位置添加内部链接
4. 重复内容：与其他文章高度重复的段落
5. E-E-A-T风险：虚假人设或误导性内容
6. CTA一致性：行动号召是否指向正确位置

用法:
    # 审计并修复单个 TSX 文章
    python tools/grok_audit.py sites/site-01/frontend/src/routes/blog.xxx.tsx

    # 批量审计目录下所有 blog.*.tsx
    python tools/grok_audit.py --batch sites/site-01/frontend/src/routes

    # 仅报告不写入（干跑）
    python tools/grok_audit.py --batch sites/site-01/frontend/src/routes --dry-run

    # 审计 Markdown（流水线 Stage 4 使用）
    python tools/grok_audit.py --md docs/humanized-xxx.md --slug xxx

    # 可选：调用 Grok CLI 做深度修复（默认仅规则引擎，可离线稳定运行）
    python tools/grok_audit.py blog.xxx.tsx --use-grok

流水线集成:
    from grok_audit import audit_and_fix_markdown
    result = audit_and_fix_markdown(humanized_md, keyword=kw, slug=slug)
    fixed_md = result["fixed"]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ── 路径 ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE_ROUTES = ROOT / "sites" / "site-01" / "frontend" / "src" / "routes"
BLOG_INDEX = SITE_ROUTES / "blog.tsx"

# ── 产品事实（规范源，与 FAQ / 优秀文章对齐）──────────────────────────────
PRODUCT = {
    "brand": "TempMails.top",
    "brand_alt": "TempMails",
    "author": "TempMails Team",
    "domain": "tempmails.top",
    "site_url": "https://tempmails.top",
    "home_path": "/",
    "cta_anchor": "/",  # 统一 CTA 指向首页工具
    "retention_default": "10 minutes",
    "retention_note": "10 minutes by default",
    "no_ads": True,
    "registration": False,
}

# 禁止的虚假人设 / 误导表述
BANNED_PERSONAS = [
    r"Alex\s+Chen",
    r"independent\s+(reviewer|tester|analyst)",
    r"as\s+an\s+independent\s+",
    r"I\s+am\s+an\s+independent\s+",
]

# 错误品牌名（应统一为 TempMails.top）
WRONG_BRANDS = [
    (r"TempMail\s+Pro", "TempMails.top"),
    (r"Temp\s*Mail\s+Pro", "TempMails.top"),
    (r"tempmailpro\.com", "tempmails.top"),
]

# 错误保留时长（描述「我们自己产品」时的常见错误；竞品对比语境保留）
# 仅在明确指代我们服务时修正，见 fix_fact_consistency
OWN_PRODUCT_MARKERS = [
    r"tempmails\.top",
    r"TempMails\.top",
    r"TempMails Team",
    r"our\s+(service|tool|platform|temp\s*mail)",
    r"we\s+(offer|provide|give\s+you)",
]


# ── 工具函数 ──────────────────────────────────────────────────────────────
def load_blog_posts() -> list[dict]:
    """从 blog.tsx 解析已发布文章列表，供内链推荐。"""
    if not BLOG_INDEX.exists():
        return []

    text = BLOG_INDEX.read_text(encoding="utf-8")
    posts = []
    # 匹配 { slug: "...", title: "...", ... category: "..." }
    pattern = re.compile(
        r'\{\s*slug:\s*"([^"]+)"\s*,\s*title:\s*"([^"]+)"'
        r'(?:[\s\S]*?category:\s*"([^"]+)")?',
        re.MULTILINE,
    )
    for m in pattern.finditer(text):
        posts.append({
            "slug": m.group(1),
            "title": m.group(2),
            "category": m.group(3) or "Guide",
        })
    return posts


def _is_tsx(content: str) -> bool:
    """粗略判断是否为 TSX 路由文件。"""
    return "createFileRoute" in content or "className=" in content


def _slug_from_path(path: Path) -> str:
    """从 blog.{slug}.tsx 或 humanized-{slug}.md 提取 slug。"""
    name = path.stem
    if name.startswith("blog."):
        return name[5:]
    for prefix in ("humanized-", "draft-", "outline-", "qc-", "audit-"):
        if name.startswith(prefix):
            return name[len(prefix):]
    return name


# ── 维度 1：MD 残留 ───────────────────────────────────────────────────────
def detect_md_residue(content: str) -> list[dict]:
    """检测未转换的 Markdown 语法残留。

    - Markdown 正文中的 ## 标题是合法的，不报错
    - TSX 中的 <p># Title</p>、段落内 **bold** 等算残留
    - Markdown 中若误粘贴 <p># ...</p> 也算残留
    """
    issues = []

    # 无论 MD/TSX：HTML 段落内残留 # 标题
    for m in re.finditer(r"<p>\s*(#{1,6})\s+([^<]+)</p>", content):
        issues.append({
            "dimension": "md_residue",
            "severity": "high",
            "message": f"段落内残留 Markdown 标题: {m.group(0)[:80]}",
            "span": m.group(0),
        })

    # 仅 TSX：裸 # 标题、段落内 **bold** / [link](url) / - list
    if _is_tsx(content):
        for m in re.finditer(r"(?m)^(#{1,6})\s+(.+)$", content):
            line = m.group(0)
            if "className" in line or "http" in line:
                continue
            issues.append({
                "dimension": "md_residue",
                "severity": "high",
                "message": f"TSX 中裸 Markdown 标题: {line[:80]}",
                "span": line,
            })

        for m in re.finditer(r"<p>[^<]*\*\*[^*]+\*\*[^<]*</p>", content):
            issues.append({
                "dimension": "md_residue",
                "severity": "medium",
                "message": f"段落内残留 **粗体** Markdown: {m.group(0)[:80]}",
                "span": m.group(0),
            })
        for m in re.finditer(r"<p>[^<]*\[[^\]]+\]\([^)]+\)[^<]*</p>", content):
            issues.append({
                "dimension": "md_residue",
                "severity": "medium",
                "message": f"段落内残留 [链接](url) Markdown: {m.group(0)[:80]}",
                "span": m.group(0),
            })
        for m in re.finditer(r"<p>\s*[-*]\s+[^<]+</p>", content):
            issues.append({
                "dimension": "md_residue",
                "severity": "medium",
                "message": f"段落内残留列表标记: {m.group(0)[:80]}",
                "span": m.group(0),
            })

    return issues


def fix_md_residue(content: str) -> tuple[str, list[str]]:
    """自动修复可确定性处理的 MD 残留。"""
    changes = []
    result = content

    def replace_md_heading_p(match: re.Match) -> str:
        hashes = match.group(1)
        text = match.group(2).strip()
        level = len(hashes)
        # 文章页已有 H1，# / ## 一律落到 h2，###+ 落到 h3，避免双 H1
        if level <= 2:
            tag = "h2"
            jsx = f'<h2 className="mt-12 text-2xl font-bold">{text}</h2>'
        else:
            tag = "h3"
            jsx = f'<h3 className="mt-8 text-xl font-semibold">{text}</h3>'
        changes.append(f"MD标题段落 → <{tag}>: {text[:60]}")
        return jsx

    if _is_tsx(result):
        new = re.sub(
            r"<p>\s*(#{1,6})\s+([^<]+)</p>",
            replace_md_heading_p,
            result,
        )
        result = new

        # **bold** → <strong>
        def bold_in_p(m: re.Match) -> str:
            inner = m.group(0)
            fixed = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", inner)
            if fixed != inner:
                changes.append(f"段落内 **粗体** → <strong>: {inner[:50]}")
            return fixed

        result = re.sub(r"<p>[^<]*\*\*[^*]+\*\*[^<]*</p>", bold_in_p, result)

        # [text](url) → <a>
        def link_in_p(m: re.Match) -> str:
            inner = m.group(0)

            def repl(lm: re.Match) -> str:
                changes.append(f"段落内 Markdown 链接 → <a>: {lm.group(1)[:40]}")
                return (
                    f'<a href="{lm.group(2)}" target="_blank" '
                    f'rel="noopener noreferrer" className="text-primary underline">'
                    f"{lm.group(1)}</a>"
                )

            return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, inner)

        result = re.sub(r"<p>[^<]*\[[^\]]+\]\([^)]+\)[^<]*</p>", link_in_p, result)

        # <p>- item</p> → <li>
        def list_p(m: re.Match) -> str:
            item = re.sub(r"^<p>\s*[-*]\s+", "", m.group(0))
            item = re.sub(r"</p>$", "", item)
            changes.append(f"段落列表标记 → <li>: {item[:50]}")
            return f"          <li>{item}</li>"

        result = re.sub(r"<p>\s*[-*]\s+[^<]+</p>", list_p, result)
    else:
        # Markdown：去掉误粘贴的 HTML 包裹的 # 标题
        def md_heading_fix(m: re.Match) -> str:
            level = len(m.group(1))
            text = m.group(2).strip()
            changes.append(f"清理 HTML 包裹的 MD 标题: {text[:60]}")
            return f"{'#' * level} {text}"

        result = re.sub(
            r"<p>\s*(#{1,6})\s+([^<]+)</p>",
            md_heading_fix,
            result,
        )

    return result, changes


# ── 维度 2：事实一致性 ───────────────────────────────────────────────────
def detect_fact_consistency(content: str) -> list[dict]:
    """检测产品事实不一致。"""
    issues = []
    plain = content

    for pattern, _correct in WRONG_BRANDS:
        for m in re.finditer(pattern, plain, re.IGNORECASE):
            issues.append({
                "dimension": "fact_consistency",
                "severity": "high",
                "message": f"错误品牌名: {m.group(0)}（应为 {PRODUCT['brand']}）",
                "span": m.group(0),
            })

    # 示例邮箱使用错误域名（我们产品示例应 @tempmails.top）
    for m in re.finditer(
        r"@(?!tempmails\.top)(tempmailpro\.com|temp-mail\.org|guerrillamail\.com)\b",
        plain,
        re.IGNORECASE,
    ):
        # 若上下文是竞品对比可忽略；简单启发：前后 80 字含 competitor 类词则跳过
        start = max(0, m.start() - 80)
        ctx = plain[start:m.end() + 80].lower()
        if any(w in ctx for w in ("competitor", "vs ", "versus", "compared to", "temp-mail.org", "guerrilla")):
            continue
        issues.append({
            "dimension": "fact_consistency",
            "severity": "medium",
            "message": f"示例邮箱域名可能不一致: {m.group(0)}",
            "span": m.group(0),
        })

    # 自身产品被写成 24-hour retention 等（FAQ 默认 10 minutes）
    for m in re.finditer(
        r"(?i)(tempmails\.top|our (?:service|emails?|temp(?:orary)? emails?))"
        r"[^.]{0,80}?(24[- ]hour|7[- ]day|1[- ]hour)\s+retention",
        plain,
    ):
        issues.append({
            "dimension": "fact_consistency",
            "severity": "high",
            "message": f"自身产品保留时长与 FAQ 不一致: {m.group(0)[:80]}",
            "span": m.group(0),
        })

    return issues


def fix_fact_consistency(content: str) -> tuple[str, list[str]]:
    """统一品牌名与明显错误事实。"""
    changes = []
    result = content

    for pattern, correct in WRONG_BRANDS:
        def repl(m: re.Match, c=correct) -> str:
            if m.group(0) != c:
                changes.append(f"品牌名 {m.group(0)} → {c}")
            return c

        result = re.sub(pattern, repl, result, flags=re.IGNORECASE)

    # 自身产品 24-hour retention → 10 minutes（保守：仅匹配明确 tempmails 主语）
    def fix_retention(m: re.Match) -> str:
        changes.append(f"保留时长修正: {m.group(0)[:60]} → 10 minutes")
        return re.sub(
            r"(?i)24[- ]hour|7[- ]day|1[- ]hour",
            "10-minute",
            m.group(0),
        )

    result = re.sub(
        r"(?i)(tempmails\.top|TempMails\.top)([^.]{0,80}?)(24[- ]hour|7[- ]day)\s+retention",
        fix_retention,
        result,
    )

    return result, changes


# ── 维度 3：内链缺失 ─────────────────────────────────────────────────────
def detect_internal_links(
    content: str,
    slug: str = "",
    posts: list[dict] | None = None,
) -> list[dict]:
    """检测站内内链是否不足。"""
    issues = []
    posts = posts if posts is not None else load_blog_posts()

    # 首页 / 品牌链
    home_links = re.findall(
        r"tempmails\.top|href=[\"']/(?:[\"'#]|blog)|to=[\"']/",
        content,
        re.IGNORECASE,
    )
    if len(home_links) < 1:
        issues.append({
            "dimension": "internal_links",
            "severity": "high",
            "message": "缺少指向首页/品牌的内链",
            "span": "",
        })

    # 相关文章链接 /blog/xxx
    blog_links = re.findall(r"/blog/([a-z0-9-]+)", content, re.IGNORECASE)
    # 排除自身
    other_links = [s for s in blog_links if s != slug]
    if len(set(other_links)) < 1 and len(posts) > 3:
        issues.append({
            "dimension": "internal_links",
            "severity": "medium",
            "message": "缺少指向其他博客文章的内链（建议至少 1–3 条相关文）",
            "span": "",
        })

    return issues


def _pick_related_posts(slug: str, posts: list[dict], n: int = 3) -> list[dict]:
    """简单相关文推荐：同 category 优先，否则取最新非自身。"""
    others = [p for p in posts if p["slug"] != slug]
    if not others:
        return []

    current_cat = None
    for p in posts:
        if p["slug"] == slug:
            current_cat = p.get("category")
            break

    same = [p for p in others if current_cat and p.get("category") == current_cat]
    rest = [p for p in others if p not in same]
    ordered = same + rest
    return ordered[:n]


def fix_internal_links(
    content: str,
    slug: str = "",
    posts: list[dict] | None = None,
) -> tuple[str, list[str]]:
    """在合适位置补充相关文章内链（不重复插入）。"""
    changes = []
    posts = posts if posts is not None else load_blog_posts()
    related = _pick_related_posts(slug, posts, n=3)
    if not related:
        return content, changes

    # 已有足够 /blog/ 链接则跳过
    existing = set(re.findall(r"/blog/([a-z0-9-]+)", content, re.IGNORECASE))
    existing.discard(slug)
    if len(existing) >= 2:
        return content, changes

    # 若已有 Related 区块则跳过
    if re.search(r"(?i)related\s+(posts|articles|guides)|you\s+may\s+also\s+like", content):
        return content, changes

    if _is_tsx(content):
        block_lines = [
            '        <h2 className="mt-12 text-2xl font-bold">Related Guides</h2>',
            '        <ul className="my-4 space-y-1">',
        ]
        for p in related:
            block_lines.append(
                f'          <li><Link to="/blog/{p["slug"]}" className="text-primary underline">'
                f'{p["title"]}</Link></li>'
            )
        block_lines.append("        </ul>")
        block = "\n".join(block_lines)

        # 插在 CTA 区块前，或 author bio 前，或 prose 结尾前
        insert_markers = [
            r'(\s*<div className="mt-12 rounded-lg bg-primary/5)',
            r'(\s*<div className="mt-12 flex items-start gap-4 rounded-lg border)',
            r'(\s*</div>\s*</article>)',
        ]
        inserted = False
        for marker in insert_markers:
            if re.search(marker, content):
                content = re.sub(marker, "\n" + block + "\n\\1", content, count=1)
                inserted = True
                break
        if inserted:
            changes.append(
                f"补充相关内链 {len(related)} 条: "
                + ", ".join(p["slug"] for p in related)
            )
            # 确保 from @tanstack/react-router 已导入 Link
            imp = re.search(
                r'import\s*\{([^}]+)\}\s*from\s*["\']@tanstack/react-router["\']',
                content,
            )
            if imp and "Link" not in imp.group(1):
                old_imp = imp.group(0)
                names = imp.group(1).strip().rstrip(",")
                new_names = f"{names}, Link" if names else "Link"
                content = content.replace(
                    old_imp,
                    old_imp.replace(imp.group(1), f" {new_names} "),
                    1,
                )
            elif not imp:
                content = (
                    'import { createFileRoute, Link } from "@tanstack/react-router";\n'
                    + content
                )
    else:
        # Markdown 相关链接
        lines = ["\n## Related Guides\n"]
        for p in related:
            lines.append(f'- [{p["title"]}](https://tempmails.top/blog/{p["slug"]})')
        block = "\n".join(lines) + "\n"
        # 插在文末或 FAQ 前
        if re.search(r"(?m)^##\s+FAQ", content):
            content = re.sub(r"(?m)^##\s+FAQ", block + "\n## FAQ", content, count=1)
        else:
            content = content.rstrip() + "\n" + block
        changes.append(
            f"补充相关内链 {len(related)} 条: "
            + ", ".join(p["slug"] for p in related)
        )

    return content, changes


# ── 维度 4：重复内容 ─────────────────────────────────────────────────────
def _extract_paragraphs(content: str) -> list[str]:
    """提取较长段落用于重复检测。"""
    if _is_tsx(content):
        paras = re.findall(r"<p[^>]*>(.*?)</p>", content, re.DOTALL)
        texts = []
        for p in paras:
            t = re.sub(r"<[^>]+>", "", p)
            t = re.sub(r"\s+", " ", t).strip()
            if len(t.split()) >= 40:
                texts.append(t)
        return texts

    paras = re.split(r"\n\s*\n", content)
    return [p.strip() for p in paras if len(p.split()) >= 40]


def _jaccard(a: str, b: str) -> float:
    """词级 Jaccard 相似度。"""
    sa = set(a.lower().split())
    sb = set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def detect_duplicate_content(
    content: str,
    slug: str = "",
    corpus: list[tuple[str, str]] | None = None,
    threshold: float = 0.75,
) -> list[dict]:
    """
    检测与其他文章高度重复的段落。
    corpus: list of (other_slug, other_content)
    """
    issues = []
    my_paras = _extract_paragraphs(content)
    if not my_paras:
        return issues

    if corpus is None:
        corpus = []
        if SITE_ROUTES.exists():
            for path in SITE_ROUTES.glob("blog.*.tsx"):
                other_slug = path.stem[5:]
                if other_slug == slug:
                    continue
                try:
                    corpus.append((other_slug, path.read_text(encoding="utf-8")))
                except OSError:
                    continue

    for other_slug, other_content in corpus:
        other_paras = _extract_paragraphs(other_content)
        for i, para in enumerate(my_paras):
            for other in other_paras:
                score = _jaccard(para, other)
                if score >= threshold:
                    issues.append({
                        "dimension": "duplicate_content",
                        "severity": "medium",
                        "message": (
                            f"与文章 {other_slug} 高度重复 "
                            f"(相似度 {score:.0%}): {para[:80]}..."
                        ),
                        "span": para[:120],
                        "other_slug": other_slug,
                        "score": round(score, 3),
                    })
                    break  # 同一段落只报一次

    # 去重：同一 span 只保留最高分
    seen = {}
    for iss in issues:
        key = iss["span"][:80]
        if key not in seen or iss.get("score", 0) > seen[key].get("score", 0):
            seen[key] = iss
    return list(seen.values())


def fix_duplicate_content(content: str, issues: list[dict]) -> tuple[str, list[str]]:
    """
    重复内容难以自动改写（需语义重写）。
    规则引擎仅标记；深度模式可交给 Grok CLI。
    此处不自动删段，避免误伤。
    """
    changes = []
    if issues:
        changes.append(
            f"发现 {len(issues)} 处疑似重复段落（需人工或 --use-grok 重写，未自动删除）"
        )
    return content, changes


# ── 维度 5：E-E-A-T 风险 ─────────────────────────────────────────────────
def detect_eeat_risk(content: str) -> list[dict]:
    """检测虚假人设、误导性独立评测等。"""
    issues = []

    for pattern in BANNED_PERSONAS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            issues.append({
                "dimension": "eeat_risk",
                "severity": "high",
                "message": f"E-E-A-T 风险（虚假/误导人设）: {m.group(0)}",
                "span": m.group(0),
            })

    # 自评第一且伪装第三方
    for m in re.finditer(
        r"(?i)(independent|unbiased|third[- ]party).{0,40}(top\s*pick|best\s*overall|#1|number\s*one)",
        content,
    ):
        issues.append({
            "dimension": "eeat_risk",
            "severity": "high",
            "message": f"可能伪装第三方测评: {m.group(0)[:80]}",
            "span": m.group(0),
        })

    # 作者字段异常
    if _is_tsx(content):
        if re.search(r'author["\']?\s*,\s*content:\s*["\'](?!TempMails)', content):
            # 非 TempMails 作者需人工确认，仅提示 Alex 类
            pass
        if re.search(r"Alex\s+Chen", content, re.IGNORECASE):
            issues.append({
                "dimension": "eeat_risk",
                "severity": "high",
                "message": "作者/正文含虚构人设 Alex Chen",
                "span": "Alex Chen",
            })

    return issues


def fix_eeat_risk(content: str) -> tuple[str, list[str]]:
    """将虚假人设替换为诚实的 TempMails Team 身份。"""
    changes = []
    result = content

    if re.search(r"Alex\s+Chen", result, re.IGNORECASE):
        result = re.sub(r"Alex\s+Chen", PRODUCT["author"], result, flags=re.IGNORECASE)
        changes.append(f"虚假人设 Alex Chen → {PRODUCT['author']}")

    # independent reviewer 等 → we (TempMails Team)
    def fix_indep(m: re.Match) -> str:
        changes.append(f"误导独立身份 → 团队身份: {m.group(0)[:50]}")
        return "we (the TempMails Team)"

    result = re.sub(
        r"(?i)as an independent (reviewer|tester|analyst)",
        fix_indep,
        result,
    )
    result = re.sub(
        r"(?i)I am an independent (reviewer|tester|analyst)",
        "We are the TempMails Team",
        result,
    )

    return result, changes


# ── 维度 6：CTA 一致性 ───────────────────────────────────────────────────
def detect_cta_consistency(content: str) -> list[dict]:
    """检测 CTA 是否指向正确位置（首页工具）。"""
    issues = []

    # 错误 CTA 目标
    bad_cta_patterns = [
        (r'href=["\']/coming-soon["\']', "指向 /coming-soon"),
        (r'href=["\']/pricing["\']', "指向尚未上线的 /pricing"),
        (r'to=["\']/coming-soon["\']', "Link 指向 /coming-soon"),
        (r'href=["\']https?://tempmailpro\.com', "指向旧域名 tempmailpro.com"),
    ]
    for pattern, desc in bad_cta_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append({
                "dimension": "cta_consistency",
                "severity": "high",
                "message": f"CTA 目标错误: {desc}",
                "span": desc,
            })

    # 是否存在至少一个指向首页的 CTA / 行动号召
    # TSX: to="/" / href="https://tempmails.top"
    # Markdown: https://tempmails.top 或裸域名 tempmails.top
    good_cta = re.search(
        r'(to=["\']/["\']'
        r'|href=["\']https://tempmails\.top/?["\']'
        r'|href=["\']/?#?["\']'
        r'|https?://tempmails\.top/?'
        r'|tempmails\.top)',
        content,
        re.IGNORECASE,
    )
    cta_text = re.search(
        r"(?i)(get\s+(your\s+)?(free\s+)?temp|try\s+(it\s+)?free|protect\s+your\s+real\s+email|create\s+(a\s+)?temporary)",
        content,
    )
    if cta_text and not good_cta:
        issues.append({
            "dimension": "cta_consistency",
            "severity": "medium",
            "message": "存在 CTA 文案但未发现指向首页 / 的有效链接",
            "span": cta_text.group(0),
        })

    return issues


def fix_cta_consistency(content: str) -> tuple[str, list[str]]:
    """将错误 CTA 目标修正为首页。"""
    changes = []
    result = content

    replacements = [
        (r'href=["\']/coming-soon["\']', 'href="/"'),
        (r'to=["\']/coming-soon["\']', 'to="/"'),
        (r'href=["\']https?://tempmailpro\.com/?["\']', 'href="https://tempmails.top/"'),
        (r'href=["\']/pricing["\']', 'href="/"'),
        (r'to=["\']/pricing["\']', 'to="/"'),
    ]
    for pattern, repl in replacements:
        if re.search(pattern, result, re.IGNORECASE):
            result = re.sub(pattern, repl, result, flags=re.IGNORECASE)
            changes.append(f"CTA 目标修正: {pattern} → {repl}")

    return result, changes


# ── 汇总：规则引擎审计 + 修复 ─────────────────────────────────────────────
def run_rule_audit(
    content: str,
    slug: str = "",
    posts: list[dict] | None = None,
    check_duplicates: bool = True,
    corpus: list[tuple[str, str]] | None = None,
) -> dict:
    """
    运行全部六个维度的检测（只读）。

    Returns:
        {
            "issues": [...],
            "by_dimension": {dim: [issues]},
            "counts": {...},
        }
    """
    posts = posts if posts is not None else load_blog_posts()
    issues: list[dict] = []
    issues.extend(detect_md_residue(content))
    issues.extend(detect_fact_consistency(content))
    issues.extend(detect_internal_links(content, slug=slug, posts=posts))
    if check_duplicates:
        issues.extend(detect_duplicate_content(content, slug=slug, corpus=corpus))
    issues.extend(detect_eeat_risk(content))
    issues.extend(detect_cta_consistency(content))

    by_dim: dict[str, list] = {}
    for iss in issues:
        by_dim.setdefault(iss["dimension"], []).append(iss)

    high = sum(1 for i in issues if i.get("severity") == "high")
    medium = sum(1 for i in issues if i.get("severity") == "medium")

    return {
        "issues": issues,
        "by_dimension": by_dim,
        "counts": {
            "total": len(issues),
            "high": high,
            "medium": medium,
            "dimensions_hit": list(by_dim.keys()),
        },
    }


def run_rule_fix(
    content: str,
    slug: str = "",
    posts: list[dict] | None = None,
    audit_issues: list[dict] | None = None,
) -> tuple[str, list[str]]:
    """按固定顺序应用自动修复，返回 (fixed_content, changes)。"""
    posts = posts if posts is not None else load_blog_posts()
    all_changes: list[str] = []
    result = content

    result, ch = fix_md_residue(result)
    all_changes.extend(ch)

    result, ch = fix_fact_consistency(result)
    all_changes.extend(ch)

    result, ch = fix_eeat_risk(result)
    all_changes.extend(ch)

    result, ch = fix_cta_consistency(result)
    all_changes.extend(ch)

    result, ch = fix_internal_links(result, slug=slug, posts=posts)
    all_changes.extend(ch)

    dup_issues = [
        i for i in (audit_issues or [])
        if i.get("dimension") == "duplicate_content"
    ]
    result, ch = fix_duplicate_content(result, dup_issues)
    all_changes.extend(ch)

    return result, all_changes


def audit_and_fix(
    content: str,
    slug: str = "",
    *,
    check_duplicates: bool = True,
    corpus: list[tuple[str, str]] | None = None,
    posts: list[dict] | None = None,
) -> dict:
    """
    完整规则引擎：先审计、再修复、再复检。

    Returns:
        {
            "success": bool,
            "original": str,
            "fixed": str,
            "has_changes": bool,
            "issues_before": list,
            "issues_after": list,
            "changes": list[str],
            "report": dict,
            "overall": "PASS" | "WARN" | "FAIL",
        }
    """
    posts = posts if posts is not None else load_blog_posts()
    before = run_rule_audit(
        content,
        slug=slug,
        posts=posts,
        check_duplicates=check_duplicates,
        corpus=corpus,
    )
    fixed, changes = run_rule_fix(
        content,
        slug=slug,
        posts=posts,
        audit_issues=before["issues"],
    )
    after = run_rule_audit(
        fixed,
        slug=slug,
        posts=posts,
        check_duplicates=check_duplicates,
        corpus=corpus,
    )

    high_after = after["counts"]["high"]
    # high 问题修不掉 → FAIL；仅 medium（如重复）→ WARN；全清 → PASS
    if high_after > 0:
        overall = "FAIL"
    elif after["counts"]["total"] > 0:
        overall = "WARN"
    else:
        overall = "PASS"

    report = {
        "slug": slug,
        "timestamp": datetime.now().isoformat(),
        "overall": overall,
        "before": before["counts"],
        "after": after["counts"],
        "changes_count": len(changes),
        "issues_before": before["issues"],
        "issues_after": after["issues"],
        "changes": changes,
    }

    return {
        "success": True,
        "original": content,
        "fixed": fixed,
        "has_changes": fixed != content,
        "issues_before": before["issues"],
        "issues_after": after["issues"],
        "changes": changes,
        "report": report,
        "overall": overall,
    }


def audit_and_fix_markdown(
    content: str,
    keyword: str = "",
    slug: str = "",
    *,
    check_duplicates: bool = True,
) -> dict:
    """
    流水线 Stage 4 入口：审计并修复 Markdown 正文。

    keyword 预留用于后续关键词一致性扩展。
    """
    _ = keyword  # 预留
    return audit_and_fix(
        content,
        slug=slug,
        check_duplicates=check_duplicates,
    )


def audit_and_fix_tsx(
    content: str,
    slug: str = "",
    *,
    check_duplicates: bool = True,
) -> dict:
    """TSX 文章审计修复入口（与 Markdown 共用规则引擎）。"""
    return audit_and_fix(
        content,
        slug=slug,
        check_duplicates=check_duplicates,
    )


# ── 可选：Grok CLI 深度修复 ───────────────────────────────────────────────
def run_grok_cli_fix(
    article_content: str,
    article_name: str = "article.tsx",
    timeout: int = 300,
) -> dict:
    """
    调用本机 Grok Build CLI 做深度审计修复（可选）。

    需要 ~/.grok/bin/grok.exe 可用；失败时返回 success=False，调用方应回退规则引擎结果。
    """
    grok_bin = Path.home() / ".grok" / "bin" / "grok.exe"
    if not grok_bin.exists():
        # 非 Windows 尝试 grok
        grok_bin = Path.home() / ".grok" / "bin" / "grok"
    if not grok_bin.exists():
        return {
            "success": False,
            "error": "未找到 Grok CLI（~/.grok/bin/grok.exe）",
            "original": article_content,
            "fixed": article_content,
        }

    with tempfile.TemporaryDirectory() as tmpdir:
        article_file = Path(tmpdir) / article_name
        article_file.write_text(article_content, encoding="utf-8")

        # 附带产品事实，避免模型编造
        facts = json.dumps(PRODUCT, ensure_ascii=False, indent=2)
        audit_prompt = f"""请审计并修复以下博客文章文件: {article_name}

产品事实（必须遵守）:
{facts}

审计维度：
1. MD残留：未转换的 Markdown（如 <p># Title</p>、**粗体**、[链接](url)）
2. 事实一致性：品牌 TempMails.top、默认保留 10 minutes、无广告
3. 内链缺失：补充指向 / 与相关 /blog/ 文章的链接
4. 重复内容：改写高度模板化/重复段落，保留信息
5. E-E-A-T风险：禁止 Alex Chen 等虚假人设；身份为 TempMails Team，可诚实披露利益关系
6. CTA一致性：行动号召指向 https://tempmails.top/ 或 to="/"

修复要求：
1. 直接修改文件 {article_name}，不要只列问题
2. 保持文章结构与文风
3. 只修复问题，不添加无关营销段落
4. 修复后在终端简要列出修改清单
"""

        cmd = [
            str(grok_bin),
            "--always-approve",
            "--max-turns",
            "15",
            "--cwd",
            tmpdir,
            audit_prompt,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
            )
            fixed_content = article_file.read_text(encoding="utf-8")
            return {
                "success": True,
                "original": article_content,
                "fixed": fixed_content,
                "has_changes": fixed_content != article_content,
                "grok_output": (result.stdout or "")[-2000:],
                "grok_errors": (result.stderr or "")[-1000:],
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Grok Build 超时（{timeout}s）",
                "original": article_content,
                "fixed": article_content,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original": article_content,
                "fixed": article_content,
            }


# ── 文件级操作 ────────────────────────────────────────────────────────────
def backup_file(path: Path) -> Path:
    """备份原文件为 .bak（同目录，带时间戳避免覆盖）。"""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = path.with_suffix(path.suffix + f".{ts}.bak")
    shutil.copy2(path, backup_path)
    return backup_path


def audit_article_file(
    file_path: str | Path,
    *,
    dry_run: bool = False,
    no_backup: bool = False,
    use_grok: bool = False,
    check_duplicates: bool = True,
    write_report: bool = True,
) -> dict:
    """
    审计单个文章文件（TSX 或 MD），可选写回与备份。
    """
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": f"文件不存在: {file_path}", "file_path": str(file_path)}

    content = path.read_text(encoding="utf-8")
    slug = _slug_from_path(path)

    # 1) 规则引擎
    result = audit_and_fix(
        content,
        slug=slug,
        check_duplicates=check_duplicates,
    )

    # 2) 可选 Grok 深度修复（在规则结果之上）
    if use_grok:
        print("  → 调用 Grok CLI 深度修复...")
        grok = run_grok_cli_fix(result["fixed"], path.name)
        if grok.get("success") and grok.get("has_changes"):
            # 对 Grok 输出再跑一遍规则，保证事实门禁
            second = audit_and_fix(
                grok["fixed"],
                slug=slug,
                check_duplicates=check_duplicates,
            )
            result["fixed"] = second["fixed"]
            result["has_changes"] = result["fixed"] != content
            result["changes"] = result["changes"] + ["[grok-cli] 深度修复已应用"] + second["changes"]
            result["issues_after"] = second["issues_after"]
            result["overall"] = second["overall"]
            result["report"] = second["report"]
            result["grok_used"] = True
        else:
            result["grok_used"] = False
            result["grok_error"] = grok.get("error", "无额外修改")

    result["file_path"] = str(path)
    result["slug"] = slug

    # 3) 写回
    if result["has_changes"] and not dry_run:
        if not no_backup:
            bak = backup_file(path)
            result["backup_path"] = str(bak)
        path.write_text(result["fixed"], encoding="utf-8")
        result["written"] = True
    else:
        result["written"] = False

    # 4) 审计报告 JSON
    if write_report:
        DOCS.mkdir(exist_ok=True)
        report_path = DOCS / f"audit-{slug}.json"
        report_path.write_text(
            json.dumps(result.get("report", result), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        result["report_path"] = str(report_path)

    return result


def audit_batch(
    directory: str | Path,
    *,
    dry_run: bool = False,
    no_backup: bool = False,
    use_grok: bool = False,
    check_duplicates: bool = True,
    pattern: str = "blog.*.tsx",
) -> list[dict]:
    """批量审计目录中的文章文件。"""
    dir_path = Path(directory)
    if not dir_path.exists():
        return [{"success": False, "error": f"目录不存在: {directory}"}]

    files = sorted(dir_path.glob(pattern))
    if not files:
        print(f"未找到匹配 {pattern} 的文件")
        return []

    print(f"找到 {len(files)} 个文章文件")
    results = []

    # 预加载语料，避免重复读盘
    corpus = []
    for f in files:
        try:
            corpus.append((_slug_from_path(f), f.read_text(encoding="utf-8")))
        except OSError:
            pass

    for i, fpath in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] 审计: {fpath.name}")
        slug = _slug_from_path(fpath)
        content = fpath.read_text(encoding="utf-8")
        # 批量时 corpus 排除自身
        other_corpus = [(s, c) for s, c in corpus if s != slug]

        result = audit_and_fix(
            content,
            slug=slug,
            check_duplicates=check_duplicates,
            corpus=other_corpus if check_duplicates else [],
        )

        if use_grok:
            print("  → 调用 Grok CLI...")
            grok = run_grok_cli_fix(result["fixed"], fpath.name)
            if grok.get("success") and grok.get("has_changes"):
                second = audit_and_fix(
                    grok["fixed"],
                    slug=slug,
                    check_duplicates=False,
                )
                result["fixed"] = second["fixed"]
                result["has_changes"] = result["fixed"] != content
                result["changes"] = result["changes"] + ["[grok-cli]"] + second["changes"]
                result["overall"] = second["overall"]
                result["report"] = second["report"]

        result["file_path"] = str(fpath)
        result["slug"] = slug

        if result["has_changes"] and not dry_run:
            if not no_backup:
                bak = backup_file(fpath)
                result["backup_path"] = str(bak)
            fpath.write_text(result["fixed"], encoding="utf-8")
            result["written"] = True
            print(f"  ✅ 已修复 ({len(result['changes'])} 处) overall={result['overall']}")
        elif result["has_changes"] and dry_run:
            result["written"] = False
            print(f"  🔍 干跑：将修复 {len(result['changes'])} 处 overall={result['overall']}")
        else:
            result["written"] = False
            print(f"  ⏭️ 无自动修复项 overall={result['overall']}")

        if result.get("issues_after"):
            for iss in result["issues_after"][:5]:
                print(f"     · [{iss['severity']}] {iss['dimension']}: {iss['message'][:70]}")

        DOCS.mkdir(exist_ok=True)
        report_path = DOCS / f"audit-{slug}.json"
        report_path.write_text(
            json.dumps(result.get("report", {}), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        result["report_path"] = str(report_path)
        results.append(result)

    return results


# ── CLI ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Grok Build 内容审计修复工具 — 六维度质量门禁",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python tools/grok_audit.py sites/site-01/frontend/src/routes/blog.xxx.tsx
  python tools/grok_audit.py --batch sites/site-01/frontend/src/routes --dry-run
  python tools/grok_audit.py --md docs/humanized-xxx.md --slug xxx
  python tools/grok_audit.py blog.xxx.tsx --use-grok
        """,
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="文章文件路径（.tsx 或 .md）",
    )
    parser.add_argument(
        "--batch",
        metavar="DIR",
        help="批量审计目录下的 blog.*.tsx",
    )
    parser.add_argument(
        "--md",
        metavar="FILE",
        help="审计 Markdown 文件（流水线用）",
    )
    parser.add_argument(
        "--slug",
        default="",
        help="文章 slug（配合 --md 或无法从文件名推断时）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只报告不写回文件",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="写回时不创建 .bak 备份",
    )
    parser.add_argument(
        "--use-grok",
        action="store_true",
        help="在规则修复后调用 Grok CLI 深度修复",
    )
    parser.add_argument(
        "--no-duplicate-check",
        action="store_true",
        help="跳过与其他文章的重复内容检测（加快批量）",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="将结果摘要写入 JSON 文件",
    )

    args = parser.parse_args()
    check_dup = not args.no_duplicate_check

    # 批量
    if args.batch:
        results = audit_batch(
            args.batch,
            dry_run=args.dry_run,
            no_backup=args.no_backup,
            use_grok=args.use_grok,
            check_duplicates=check_dup,
        )
        total = len(results)
        changed = sum(1 for r in results if r.get("has_changes"))
        failed = sum(1 for r in results if r.get("overall") == "FAIL")
        warned = sum(1 for r in results if r.get("overall") == "WARN")
        passed = sum(1 for r in results if r.get("overall") == "PASS")

        print(f"\n{'=' * 60}")
        print("批量审计完成")
        print(f"  总计:   {total}")
        print(f"  PASS:   {passed}")
        print(f"  WARN:   {warned}")
        print(f"  FAIL:   {failed}")
        print(f"  已修复: {changed}" + (" (干跑未写入)" if args.dry_run else ""))
        print(f"{'=' * 60}")

        if args.output:
            summary = [
                {
                    "file": r.get("file_path"),
                    "slug": r.get("slug"),
                    "overall": r.get("overall"),
                    "has_changes": r.get("has_changes"),
                    "changes": r.get("changes"),
                    "issues_after_count": len(r.get("issues_after") or []),
                }
                for r in results
            ]
            Path(args.output).write_text(
                json.dumps(summary, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"摘要已保存: {args.output}")

        sys.exit(0 if failed == 0 else 1)

    # Markdown 单文件
    if args.md:
        path = Path(args.md)
        if not path.exists():
            parser.error(f"文件不存在: {args.md}")
        content = path.read_text(encoding="utf-8")
        slug = args.slug or _slug_from_path(path)
        result = audit_and_fix_markdown(content, slug=slug, check_duplicates=check_dup)

        if args.use_grok:
            grok = run_grok_cli_fix(result["fixed"], path.name)
            if grok.get("success") and grok.get("has_changes"):
                result = audit_and_fix_markdown(grok["fixed"], slug=slug, check_duplicates=check_dup)
                result["grok_used"] = True

        print(f"审计: {path.name}  overall={result['overall']}")
        print(f"  修复前问题: {len(result['issues_before'])}")
        print(f"  修复后问题: {len(result['issues_after'])}")
        for c in result["changes"]:
            print(f"  · {c}")

        if result["has_changes"] and not args.dry_run:
            if not args.no_backup:
                bak = backup_file(path)
                print(f"  备份: {bak}")
            path.write_text(result["fixed"], encoding="utf-8")
            print(f"  已写入: {path}")
        elif args.dry_run and result["has_changes"]:
            print("  （干跑，未写入）")

        DOCS.mkdir(exist_ok=True)
        report_path = DOCS / f"audit-{slug}.json"
        report_path.write_text(
            json.dumps(result.get("report", {}), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  报告: {report_path}")

        if args.output:
            Path(args.output).write_text(
                json.dumps(result.get("report", {}), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        sys.exit(0 if result["overall"] != "FAIL" else 1)

    # 单文件 TSX/MD
    if args.file:
        result = audit_article_file(
            args.file,
            dry_run=args.dry_run,
            no_backup=args.no_backup,
            use_grok=args.use_grok,
            check_duplicates=check_dup,
        )
        if not result.get("success") and result.get("error"):
            print(f"❌ {result['error']}")
            sys.exit(1)

        print(f"审计: {args.file}  overall={result.get('overall')}")
        print(f"  修复前问题: {len(result.get('issues_before') or [])}")
        print(f"  修复后问题: {len(result.get('issues_after') or [])}")
        for c in result.get("changes") or []:
            print(f"  · {c}")
        if result.get("written"):
            print(f"  ✅ 已写回" + (f"  备份: {result.get('backup_path')}" if result.get("backup_path") else ""))
        elif result.get("has_changes") and args.dry_run:
            print("  🔍 干跑：有修复但未写入")
        else:
            print("  ⏭️ 无自动修复写入")
        if result.get("report_path"):
            print(f"  报告: {result['report_path']}")

        if args.output:
            Path(args.output).write_text(
                json.dumps(result.get("report", {}), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        sys.exit(0 if result.get("overall") != "FAIL" else 1)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
