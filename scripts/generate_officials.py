#!/usr/bin/env python3
"""生成编制内7人角色素材"""

import requests
import time
from pathlib import Path
from PIL import Image
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
API_KEY_FILE = PROJECT_ROOT / "doc" / "02-tempmails.top改善建议_Grok编写" / "agnes api.txt"
OUTPUT_DIR = PROJECT_ROOT / "pic" / "agnes_generated"
RESULT_DIR = PROJECT_ROOT / "pic" / "test_results"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

API_KEY=API_KE...gt;strip()
API_URL = "https://apihub.agnes-ai.com/v1/images/generations"

STYLE = """Chibi 2-head-body ratio Q-version character, Chinese ink wash and watercolor hand-drawn style, 
fine black ink outlines with soft watercolor blending, low-saturation traditional muted tones 
with subtle bright accent colors, 
Song Dynasty Chinese ancient costume details, cute office worker temperament, 
high definition, 8K quality, character design sheet style."""

OFFICIALS = [
    {
        "name": "李清照",
        "role": "写作",
        "iconic_age": "30-40岁",
        "prompt": "A talented Chinese woman aged 30-40 with elegant features, wearing Song Dynasty female hair ornaments with pearls, light-colored ruqun dress, holding a calligraphy brush, scholarly and graceful temperament."
    },
    {
        "name": "岳飞",
        "role": "质检",
        "iconic_age": "35-45岁",
        "prompt": "A righteous Chinese warrior general aged 35-45 with resolute face, wearing warrior helmet and armor robe, holding a magnifying glass inspecting bamboo scrolls, loyal and patriotic temperament."
    },
    {
        "name": "张择端",
        "role": "大纲/研究",
        "iconic_age": "35-45岁",
        "prompt": "A Chinese painter aged 35-45 with refined features, wearing scholar hat and cyan robe, holding a painting brush with a scroll in front, artistic temperament."
    },
    {
        "name": "李纲",
        "role": "策略/规划",
        "iconic_age": "40-50岁",
        "prompt": "A Chinese strategist aged 40-50 with dignified and wise face, wearing official hat and dark official robes, holding a command flag pointing at a sand table, strategic mastermind temperament."
    },
    {
        "name": "韩世忠",
        "role": "部署/发布",
        "iconic_age": "35-45岁",
        "prompt": "A heroic Chinese warrior aged 35-45 with brave and bold face, wearing warrior helmet and red battle robe, holding a horn, deployment commander temperament."
    },
    {
        "name": "宗泽",
        "role": "监控/运维",
        "iconic_age": "50-60岁",
        "prompt": "An aged Chinese official aged 50-60 with weathered but spirited face, wearing official hat and dark official robes, holding a telescope looking over city walls, guardian temperament."
    },
]


def remove_green_background(img_path, output_path):
    """绿幕抠图"""
    img = Image.open(img_path).convert('RGBA')
    data = np.array(img)
    rgb = data[:, :, :3].astype(float)
    R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    
    green_mask = (G > 150) & (G > R * 1.3) & (G > B * 1.3)
    skin_mask = (R > 180) & (G > 100) & (B > 80) & (R > G * 0.9)
    dark_mask = (R < 60) & (G < 60) & (B < 60)
    red_mask = (R > 150) & (R > G * 1.3) & (R > B * 1.2)
    
    remove_mask = green_mask & ~skin_mask & ~dark_mask & ~red_mask
    data[remove_mask, 3] = 0
    
    result = Image.fromarray(data)
    result.save(output_path)
    
    alpha = data[:, :, 3]
    return (alpha < 10).sum() / alpha.size * 100


def generate_character(char, max_retries=3):
    """生成单个角色"""
    name = char["name"]
    role = char["role"]
    
    full_prompt = f"""{STYLE}

{char['prompt']}

SOLID BRIGHT GREEN BACKGROUND (#00FF00), single uniform green color, no patterns, no gradients.
A calligraphy name plaque below reads "{name}·{role}" with a small red traditional Chinese seal stamp."""

    print(f"\n{'='*50}")
    print(f"🎭 生成: {name}（{role}）")
    print(f"   标志性年龄: {char['iconic_age']}")
    print(f"{'='*50}")
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"   ⏳ 重试 {attempt + 1}/{max_retries}...")
                time.sleep(30)
            
            response = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={"model": "agnes-image-2.1-flash", "prompt": full_prompt, "n": 1, "size": "1024x1024"},
                timeout=180
            )
            
            if response.status_code != 200:
                print(f"   ❌ API错误: {response.status_code}")
                if attempt < max_retries - 1:
                    continue
                return False
            
            image_url = response.json()["data"][0]["url"]
            
            for dl_attempt in range(3):
                try:
                    img_response = requests.get(image_url, timeout=120)
                    break
                except Exception:
                    if dl_attempt < 2:
                        time.sleep(10)
                    else:
                        raise
            
            original_path = OUTPUT_DIR / f"{name}.png"
            original_path.write_bytes(img_response.content)
            print(f"   ✅ 原图: {original_path}")
            
            transparent_path = RESULT_DIR / f"{name}_transparent.png"
            pct = remove_green_background(original_path, transparent_path)
            print(f"   ✅ 抠图: {transparent_path} (透明: {pct:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            if attempt < max_retries - 1:
                continue
            return False
    
    return False


def main():
    print("🏛️ 编制内7人角色素材生成")
    print(f"   宋徽宗已有素材，跳过")
    print(f"   待生成: {len(OFFICIALS)} 人")
    
    success = 0
    fail = 0
    
    for i, char in enumerate(OFFICIALS):
        if generate_character(char):
            success += 1
        else:
            fail += 1
        
        if (i + 1) % 2 == 0 and i < len(OFFICIALS) - 1:
            print(f"\n⏳ 已生成 {i + 1} 个，暂停 1 分钟...")
            time.sleep(60)
    
    print(f"\n{'='*50}")
    print(f"✅ 完成！成功: {success}, 失败: {fail}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
