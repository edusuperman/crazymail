#!/usr/bin/env python3
"""
梁山好汉 Q版卡通角色图生成脚本
=================================
研究结论：小米 MiMo API 官方不提供文生图（image generation）接口。
MiMo 平台支持的能力：文本生成、多模态理解（图片/音频/视频理解）、语音合成(TTS)。
/v1/images/generations 返回 404。

替代方案：
1. xiaomi-api.apifox.cn 中的 ideogram 代理接口 (POST /ideogram/generate)
   服务器：https://vip.123everything.com
2. 其他支持文生图的 API（如 MiniMax image-01、DALL-E 等）
"""

import os
import sys
import json
import time
import base64
import requests
from pathlib import Path

# ══════════════════════════════════════
# 配置
# ══════════════════════════════════════

OUTPUT_DIR = Path(r"D:\xcode\20260608_疯邮（英文名：CrazyMail）\pic\mimo_generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IDEOGRAM_URL = "https://vip.123everything.com/ideogram/generate"
MINIMAX_URL = "https://api.minimaxi.com/v1/image_generation"


def load_env():
    env_path = Path(r"D:\xcode\20260608_疯邮（英文名：CrazyMail）\.env")
    env = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


# ══════════════════════════════════════
# 角色 Prompt 定义
# ══════════════════════════════════════

STYLE_BASE = (
    "cute Chinese Song Dynasty cartoon style, 108 Heroes series, "
    "chibi big-head doll proportions, ink wash with light color, "
    "low saturation vintage tones, high definition 8k, "
    "clean white background, character design sheet style"
)

CHARACTERS = [
    {
        "name": "宋江",
        "name_en": "songjiang",
        "prompt": (
            f"{STYLE_BASE}, "
            "a cute chibi male character wearing a gray-brown long robe, "
            "scholar square hat, thin mustache, holding a white feather fan, "
            "melancholic worried expression, kind eyes, "
            "Chinese ink painting style, detailed clothing patterns"
        ),
        "negative_prompt": "ugly, blurry, low quality, deformed, realistic photo",
    },
    {
        "name": "吴用",
        "name_en": "wuyong",
        "prompt": (
            f"{STYLE_BASE}, "
            "a cute chibi male strategist character wearing a gray-green long robe, "
            "round glasses, holding a feather fan, thinking pose with hand on chin, "
            "clever wise expression, Chinese ink painting style, detailed clothing"
        ),
        "negative_prompt": "ugly, blurry, low quality, deformed, realistic photo",
    },
    {
        "name": "林冲",
        "name_en": "linchong",
        "prompt": (
            f"{STYLE_BASE}, "
            "a cute chibi male warrior character wearing black-gold armor, "
            "dark red cape flowing in wind, holding a long spear, "
            "majestic dignified expression, strong build, "
            "Chinese ink painting style, detailed armor patterns"
        ),
        "negative_prompt": "ugly, blurry, low quality, deformed, realistic photo",
    },
    {
        "name": "武松",
        "name_en": "wusong",
        "prompt": (
            f"{STYLE_BASE}, "
            "a cute chibi male warrior character wearing gray-blue short martial arts outfit, "
            "leopard print vest, holding two curved blades, "
            "cold stern expression, muscular build, "
            "Chinese ink painting style, detailed clothing"
        ),
        "negative_prompt": "ugly, blurry, low quality, deformed, realistic photo",
    },
]


# ══════════════════════════════════════
# 图片生成函数
# ══════════════════════════════════════

def generate_via_ideogram(api_key, character):
    """通过 ideogram 代理生成图片"""
    payload = {
        "image_request": {
            "prompt": character["prompt"],
            "aspect_ratio": "ASPECT_1_1",
            "model": "V_2",
            "magic_prompt_option": "AUTO",
            "seed": 42,
            "style_type": "ANIME",
            "negative_prompt": character["negative_prompt"],
            "num_images": 1,
            "resolution": "1024x1024",
        }
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print("  调用 ideogram API...")
    try:
        resp = requests.post(IDEOGRAM_URL, headers=headers, json=payload, timeout=120)
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return False

    # 检查响应是否为 JSON
    try:
        data = resp.json()
    except Exception:
        print(f"  ❌ HTTP {resp.status_code}: 非JSON响应")
        print(f"     Content-Type: {resp.headers.get('content-type', 'unknown')}")
        print(f"     响应前200字: {resp.text[:200]}")
        return False

    if resp.status_code == 200 and "data" in data and len(data["data"]) > 0:
        image_url = data["data"][0].get("url", "")
        if image_url:
            img_resp = requests.get(image_url, timeout=60)
            if img_resp.status_code == 200:
                out_path = OUTPUT_DIR / f"{character['name_en']}.png"
                with open(out_path, "wb") as f:
                    f.write(img_resp.content)
                print(f"  ✅ 已保存: {out_path}")
                return True
        print(f"  ⚠️ 响应中无图片URL")
        return False
    else:
        print(f"  ❌ HTTP {resp.status_code}: {json.dumps(data, ensure_ascii=False)[:300]}")
        return False


def generate_via_minimax(api_key, character):
    """通过 MiniMax image-01 生成图片"""
    payload = {
        "model": "image-01",
        "prompt": character["prompt"],
        "aspect_ratio": "1:1",
        "response_format": "url",
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print("  调用 MiniMax API...")
    try:
        resp = requests.post(MINIMAX_URL, headers=headers, json=payload, timeout=120)
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return False

    try:
        data = resp.json()
    except Exception:
        print(f"  ❌ HTTP {resp.status_code}: 非JSON响应")
        return False

    if resp.status_code == 200:
        images = data.get("data", {}).get("image_urls", [])
        if not images:
            images = data.get("data", {}).get("image_base64", [])
        if images:
            img_data = images[0]
            out_path = OUTPUT_DIR / f"{character['name_en']}.png"
            if img_data.startswith("http"):
                img_resp = requests.get(img_data, timeout=60)
                with open(out_path, "wb") as f:
                    f.write(img_resp.content)
            else:
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(img_data))
            print(f"  ✅ 已保存: {out_path}")
            return True
        print(f"  ⚠️ 响应中无图片")
        return False
    else:
        print(f"  ❌ HTTP {resp.status_code}: {json.dumps(data, ensure_ascii=False)[:300]}")
        return False


# ══════════════════════════════════════
# 主流程
# ══════════════════════════════════════

def main():
    env = load_env()
    mimo_key = env.get("MIMO_API_KEY", "")

    print("=" * 60)
    print("梁山好汉 Q版卡通角色图生成")
    print("=" * 60)
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"API Key: {mimo_key[:10]}... (长度: {len(mimo_key)})")
    print()

    # 检查 API Key 是否为占位符
    if mimo_key in ("***", "tp-xxxx", ""):
        print("❌ MIMO_API_KEY 为占位符或空值，无有效 API Key")
        print()
        print("=" * 60)
        print("研究结论")
        print("=" * 60)
        print()
        print("1. 小米 MiMo API 官方【不支持】文生图（image generation）")
        print("   - 官方文档 sidebar 仅有: 文本生成、工具调用、联网搜索、")
        print("     深度思考、结构化输出、多模态理解(图片/音频/视频理解)、语音")
        print("   - 无'图片生成'分类")
        print("   - /v1/images/generations 返回 404")
        print()
        print("2. MiMo 平台支持的能力:")
        print("   - 文本生成 (chat/completions)")
        print("   - 多模态理解 (图片/音频/视频理解 - 不是生成)")
        print("   - 语音合成 (TTS)")
        print()
        print("3. 替代方案:")
        print("   a) xiaomi-api.apifox.cn 中有 ideogram 代理接口")
        print("      POST https://vip.123everything.com/ideogram/generate")
        print("   b) MiniMax image-01 API (api.minimaxi.com)")
        print("   c) OpenAI DALL-E API")
        print()
        print("4. 需要用户提供有效的 API Key 才能生成图片")
        print()

        # 保存 prompt 配置供后续使用
        prompts_path = OUTPUT_DIR / "prompts.json"
        with open(prompts_path, "w", encoding="utf-8") as f:
            json.dump(CHARACTERS, f, ensure_ascii=False, indent=2)
        print(f"已保存 Prompt 配置到: {prompts_path}")
        return 1

    # 尝试生成
    print(f"使用 API Key 前缀: {mimo_key[:5]}...")
    success_count = 0

    for i, char in enumerate(CHARACTERS):
        print(f"\n[{i+1}/4] 生成 {char['name']}...")

        # 尝试 ideogram 代理
        ok = generate_via_ideogram(mimo_key, char)
        if not ok:
            print("  尝试 MiniMax 方案...")
            ok = generate_via_minimax(mimo_key, char)

        if ok:
            success_count += 1

        # 避免频率限制
        if i < len(CHARACTERS) - 1:
            time.sleep(2)

    print(f"\n{'=' * 60}")
    print(f"完成: {success_count}/4 张图片生成成功")
    print(f"输出目录: {OUTPUT_DIR}")

    # 保存 prompt 配置
    prompts_path = OUTPUT_DIR / "prompts.json"
    with open(prompts_path, "w", encoding="utf-8") as f:
        json.dump(CHARACTERS, f, ensure_ascii=False, indent=2)

    return 0 if success_count == 4 else 1


if __name__ == "__main__":
    sys.exit(main())
