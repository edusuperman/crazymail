#!/usr/bin/env python3
from pathlib import Path
import re

routes = Path("sites/site-01/frontend/src/routes")
files = sorted([f for f in routes.glob("blog.*.tsx") if not f.name.endswith(".bak")])
bad = []
for f in files:
    c = f.read_text(encoding="utf-8")
    m = re.search(
        r'Related Guides</h2>\s*<ul className="my-4 space-y-1">(.*?)</ul>',
        c,
        re.S,
    )
    if not m:
        bad.append((f.name, "no related"))
        continue
    links = re.findall(r'to="/blog/([^"]+)"', m.group(1))
    if len(links) != 3:
        bad.append((f.name, f"count={len(links)} {links}"))
    cta = re.search(
        r'bg-primary/5 p-8 text-center">.*?to="([^"]+)".*?>(.*?)</Link>',
        c,
        re.S,
    )
    if not cta or cta.group(1) != "/" or "Get a Free Temporary Email" not in cta.group(2):
        bad.append(
            (
                f.name,
                f"cta={cta.group(1) if cta else None} text={(cta.group(2).strip()[:50] if cta else None)}",
            )
        )

print("files", len(files))
print("bad", len(bad))
for b in bad:
    print(b)

abs_home = 0
pricing = 0
for f in files:
    c = f.read_text(encoding="utf-8")
    abs_home += len(re.findall(r'href="https?://(?:www\.)?tempmails\.top/?"', c))
    pricing += len(re.findall(r'tempmails\.top/pricing|tempmails\.top/faq', c))
print("remaining abs homepage hrefs", abs_home)
print("paths like pricing/faq still present", pricing)

# sample related uniqueness
from collections import Counter
targets = Counter()
for f in files:
    c = f.read_text(encoding="utf-8")
    m = re.search(
        r'Related Guides</h2>\s*<ul className="my-4 space-y-1">(.*?)</ul>',
        c,
        re.S,
    )
    if m:
        for slug in re.findall(r'to="/blog/([^"]+)"', m.group(1)):
            targets[slug] += 1
print("top related targets:")
for k, v in targets.most_common(10):
    print(v, k)
