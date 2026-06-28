#!/usr/bin/env python3
"""
CrazyMail 项目进度看板自动更新脚本
从项目实际状态读取真实数据，更新 progress.html

更新频率策略：
- 每小时（本脚本）：站点状态、文章数、素材数、文章列表、风险监控
- 每日（cron 提醒用户）：工作计划状态
- 里程碑触发（手动）：项目进度阶段
"""

import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROGRESS_HTML = PROJECT_ROOT / "dashboard-v2" / "public" / "progress.html"


def get_git_log(n=5):
    """获取最近 n 条 Git 提交"""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{n}"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip().split("\n") if result.returncode == 0 else []
    except Exception:
        return []


def get_blog_articles():
    """从实际文件读取博客文章列表"""
    blog_dir = PROJECT_ROOT / "sites" / "site-01" / "frontend" / "src" / "routes"
    if not blog_dir.exists():
        return []

    articles = []
    for f in sorted(blog_dir.glob("blog.*.tsx")):
        content = f.read_text(encoding="utf-8", errors="ignore")
        # 从 frontmatter 或 meta 提取标题
        title_match = re.search(r"title:\s*[\"']([^\"']+)[\"']", content)
        title = title_match.group(1) if title_match else f.stem.replace("blog.", "").replace("-", " ").title()
        # 清理标题（去掉网站名后缀）
        title = re.sub(r"\s*[-–|]\s*TempMails?\.top\s*$", "", title)
        if len(title) > 55:
            title = title[:52] + "..."
        date = datetime.fromtimestamp(f.stat().st_mtime).strftime("%m-%d")
        articles.append({"title": title, "date": date})

    return articles


def count_hero_images():
    """统计已生成的角色素材"""
    hero_dir = PROJECT_ROOT / "pic" / "agnes_generated"
    return len(list(hero_dir.glob("*.png"))) if hero_dir.exists() else 0


def check_site_status(url, timeout=10):
    """检查站点运行状态"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=timeout
        )
        code = result.stdout.strip()
        return "运行中" if code == "200" else f"异常({code})"
    except Exception:
        return "未知"


def generate_articles_html(articles):
    """生成文章列表 HTML"""
    lines = []
    for i, a in enumerate(articles, 1):
        lines.append(f'''            <div class="article-item">
                <span class="num">{i:02d}</span>
                <span class="title">{a["title"]}</span>
                <span class="date">{a["date"]}</span>
            </div>''')
    return "\n".join(lines)


def update_progress_html():
    """更新 progress.html 中的真实数据"""
    if not PROGRESS_HTML.exists():
        print(f"❌ 找不到 {PROGRESS_HTML}")
        return False

    content = PROGRESS_HTML.read_text(encoding="utf-8")
    now = datetime.now()

    # ========== 1. 收集真实数据 ==========
    articles = get_blog_articles()
    article_count = len(articles)
    hero_count = count_hero_images()
    tempmails_status = check_site_status("https://tempmails.top/")
    git_log = get_git_log(3)

    # ========== 2. 更新关键指标 ==========
    content = re.sub(
        r'\{ label: "已发布文章", value: "\d+"',
        f'{{ label: "已发布文章", value: "{article_count}"',
        content
    )
    content = re.sub(
        r'\{ label: "角色素材", value: "\d+"',
        f'{{ label: "角色素材", value: "{hero_count}"',
        content
    )

    # ========== 3. 更新文章列表（tempmails 站点） ==========
    articles_html = generate_articles_html(articles)
    # 替换 tempmails 站点的 articles 数组
    pattern = r'(id: "tempmails".*?articles: \[).*?(\],\s*plans:)'
    replacement = f'\\1\n{articles_html}\n            \\2'
    # 由于 JS 数组格式不同，直接更新 HTML 中的文章列表
    # 找到 articleList div 并更新（使用贪婪匹配到最后一个 </div>）
    content = re.sub(
        r'(<div id="articleList">)(.*?)(</div>\s*</div>\s*</div>)',
        f'\\1\n{articles_html}\n        \\3',
        content,
        flags=re.DOTALL
    )

    # ========== 4. 更新站点文章数量 ==========
    content = re.sub(
        r'<td>\d+ 篇</td>\s*<td><span class="tech-tag tag-green">运行中',
        f'<td>{article_count} 篇</td>\n                <td><span class="tech-tag tag-green">运行中',
        content
    )

    # ========== 5. 更新时间戳 ==========
    time_str = now.strftime("%Y/%m/%d %H:%M:%S")
    content = re.sub(r'id="lastUpdate">.*?<', f'id="lastUpdate">{time_str}<', content)
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0)
    content = re.sub(r'id="nextUpdate">.*?<', f'id="nextUpdate">{next_hour.strftime("%Y/%m/%d %H:%M:%S")}<', content)

    # ========== 6. 写入文件 ==========
    PROGRESS_HTML.write_text(content, encoding="utf-8")

    # ========== 7. 打印报告 ==========
    print("=" * 50)
    print("📊 CrazyMail 项目进度看板已更新")
    print("=" * 50)
    print(f"⏰ 更新时间: {time_str}")
    print(f"📝 博客文章: {article_count} 篇")
    print(f"🎨 角色素材: {hero_count} 张")
    print(f"🌐 tempmails.top: {tempmails_status}")
    print()
    print("文章列表:")
    for i, a in enumerate(articles, 1):
        print(f"  {i:02d}. [{a['date']}] {a['title']}")
    print()
    print("最近 Git 提交:")
    for c in git_log[:3]:
        print(f"  - {c}")

    return True


if __name__ == "__main__":
    exit(0 if update_progress_html() else 1)
