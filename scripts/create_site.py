#!/usr/bin/env python3
"""
CrazyMail 多站点生成器 — 一键创建新站点

Usage:
    python scripts/create_site.py --name "TempMail.io" --domain "tempmail.io"
    python scripts/create_site.py --name "DisposableMail.cc" --domain "disposablemail.cc" --theme dark
"""

import argparse
import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SITES_DIR = PROJECT_ROOT / "sites"
TEMPLATE_DIR = SITES_DIR / "site-01"  # 使用 site-01 作为模板


def get_next_site_id() -> str:
    """获取下一个站点 ID"""
    existing = [d.name for d in SITES_DIR.iterdir() if d.is_dir() and d.name.startswith("site-")]
    if not existing:
        return "site-02"
    nums = [int(s.split("-")[1]) for s in existing]
    return f"site-{max(nums) + 1:02d}"


def create_site(name: str, domain: str, theme: str = "light") -> Path:
    """创建新站点"""
    site_id = get_next_site_id()
    site_dir = SITES_DIR / site_id

    print(f"🚀 创建新站点: {name}")
    print(f"   ID: {site_id}")
    print(f"   域名: {domain}")
    print(f"   主题: {theme}")
    print()

    # 复制模板
    if site_dir.exists():
        print(f"❌ 站点目录已存在: {site_dir}")
        return site_dir

    shutil.copytree(TEMPLATE_DIR / "frontend", site_dir / "frontend")

    # 更新配置
    update_site_config(site_dir, name, domain, theme)

    # 创建站点配置文件
    create_site_config(site_dir, site_id, name, domain)

    print(f"✅ 站点创建成功: {site_dir}")
    print()
    print("下一步:")
    print(f"  1. cd {site_dir}/frontend")
    print(f"  2. npm install")
    print(f"  3. npm run dev")
    print(f"  4. 购买域名 {domain}")
    print(f"  5. 部署到 Vercel")

    return site_dir


def update_site_config(site_dir: Path, name: str, domain: str, theme: str):
    """更新站点配置"""
    # 更新 package.json
    pkg_file = site_dir / "frontend" / "package.json"
    if pkg_file.exists():
        content = pkg_file.read_text(encoding="utf-8")
        content = content.replace('"name": "tempmails-frontend"', f'"name": "{domain}-frontend"')
        pkg_file.write_text(content, encoding="utf-8")

    # 更新 vite.config.ts
    vite_file = site_dir / "frontend" / "vite.config.ts"
    if vite_file.exists():
        content = vite_file.read_text(encoding="utf-8")
        # 可以在这里添加域名特定的配置
        vite_file.write_text(content, encoding="utf-8")


def create_site_config(site_dir: Path, site_id: str, name: str, domain: str):
    """创建站点配置文件"""
    config = {
        "id": site_id,
        "name": name,
        "domain": domain,
        "created_at": "2026-06-29",
        "status": "development",
        "tech_stack": {
            "frontend": "TanStack Start",
            "backend": "Python FastAPI (shared)",
            "deploy": "Vercel",
        },
        "features": {
            "blog": True,
            "faq": True,
            "privacy_policy": True,
            "terms_of_service": True,
            "cookie_consent": True,
            "adsense": False,
            "affiliate": False,
        },
        "seo": {
            "sitemap": True,
            "robots_txt": True,
            "structured_data": True,
            "hreflang": True,
        },
    }

    config_file = site_dir / "site-config.json"
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="CrazyMail 多站点生成器")
    parser.add_argument("--name", required=True, help="站点名称")
    parser.add_argument("--domain", required=True, help="域名")
    parser.add_argument("--theme", default="light", choices=["light", "dark"], help="主题")

    args = parser.parse_args()
    create_site(args.name, args.domain, args.theme)


if __name__ == "__main__":
    main()
