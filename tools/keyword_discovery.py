#!/usr/bin/env python3
"""关键词自动发现工具

自动发现和评估关键词，为内容工厂供词。

用法：
    python tools/keyword_discovery.py "temporary email" "disposable email"
    python tools/keyword_discovery.py -k "temp mail" -n 30
    python tools/keyword_discovery.py "temporary email" --feed-factory
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger
from openai import AsyncOpenAI

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# API 配置
API_CONFIG = {
    "base_url": "https://api.xiaomimimo.com/v1",
    "model": "mimo-v2.5-pro",
    "timeout": 60,
}


class KeywordDiscovery:
    """关键词发现器"""

    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> AsyncOpenAI:
        """懒加载 OpenAI 客户端"""
        if self._client is None:
            api_key = self._load_api_key()
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url=API_CONFIG["base_url"],
                timeout=API_CONFIG["timeout"],
            )
        return self._client

    def _load_api_key(self) -> str:
        """加载 MiMo API Key"""
        import os

        # 优先从环境变量读取
        api_key = os.getenv("MIMO_API_KEY")
        if api_key and api_key != "your_api_key_here":
            return api_key

        # 从 opencode 配置文件读取
        config_path = Path.home() / ".config" / "opencode" / "opencode.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    providers = config.get("provider", {})
                    for provider_name, provider_config in providers.items():
                        if "mimo" in provider_name.lower():
                            options = provider_config.get("options", {})
                            api_key = options.get("apiKey", "")
                            if api_key and api_key != "***":
                                return api_key
            except Exception as e:
                logger.warning(f"读取 opencode 配置失败: {e}")

        raise ValueError(
            "未找到 MiMo API Key。请通过以下方式之一配置：\n"
            "1. 设置环境变量 MIMO_API_KEY\n"
            "2. 在 .env 文件中添加 MIMO_API_KEY=your_key"
        )

    async def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """调用 LLM"""
        try:
            response = await self.client.chat.completions.create(
                model=API_CONFIG["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=4000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise

    async def discover(
        self,
        seed_keywords: list[str],
        num_results: int = 20,
        language: str = "en",
    ) -> dict:
        """发现关键词

        Args:
            seed_keywords: 种子关键词列表
            num_results: 返回结果数量
            language: 语言代码

        Returns:
            发现结果字典
        """
        logger.info(f"开始关键词发现: {seed_keywords}")

        # Stage 1: 关键词扩展
        logger.info("Stage 1: 关键词扩展...")
        expanded = await self._expand_keywords(seed_keywords, language)
        logger.info(f"扩展完成: {len(expanded)} 个关键词")

        # Stage 2: 关键词评分
        logger.info("Stage 2: 关键词评分...")
        scored = await self._score_keywords(expanded, seed_keywords)
        logger.info(f"评分完成: {len(scored)} 个关键词")

        # Stage 3: 去重和排序
        logger.info("Stage 3: 去重和排序...")
        deduplicated = await self._deduplicate_and_sort(scored, num_results)
        logger.info(f"去重完成: {len(deduplicated)} 个关键词")

        # 构建结果
        result = {
            "generated_at": datetime.now().isoformat(),
            "seed_keywords": seed_keywords,
            "total_discovered": len(deduplicated),
            "keywords": deduplicated,
        }

        # 保存到文件
        output_file = PROJECT_ROOT / "docs" / f"keyword-discovery-{datetime.now().strftime('%Y%m%d')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"结果已保存: {output_file}")

        return result

    async def _expand_keywords(self, seed_keywords: list[str], language: str) -> list[dict]:
        """扩展关键词"""
        system_prompt = """你是一个 SEO 关键词研究专家。根据给定的种子关键词，扩展出更多相关关键词。

扩展类型：
1. 问题型：how to X, what is X, is X safe, can I use X for Y
2. 比较型：X vs Y, X alternative, best X for Y
3. 长尾型：X for [use case], X without [limitation]
4. 场景型：X for [platform], X for [year]

返回 JSON 格式：
{
    "keywords": [
        {
            "keyword": "扩展的关键词",
            "type": "question/comparison/long-tail/scenario",
            "reason": "为什么这个关键词有价值"
        }
    ]
}

只返回 JSON，不要其他内容。确保 JSON 格式正确，所有字符串用双引号。"""

        user_prompt = f"""请为以下种子关键词扩展出 30-50 个相关关键词：

种子关键词：{', '.join(seed_keywords)}
语言：{language}

请返回 JSON 格式的扩展结果。"""

        result = await self._call_llm(system_prompt, user_prompt, temperature=0.8)

        try:
            # 尝试多种 JSON 提取方式
            json_match = re.search(r'\{[\s\S]*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # 修复常见的 JSON 问题
                json_str = re.sub(r',\s*}', '}', json_str)  # 移除末尾逗号
                json_str = re.sub(r',\s*]', ']', json_str)  # 移除数组末尾逗号
                data = json.loads(json_str)
            else:
                data = json.loads(result)
            return data.get("keywords", [])
        except Exception as e:
            logger.error(f"解析扩展结果失败: {e}")
            logger.debug(f"原始响应: {result[:500]}...")
            return []

    async def _score_keywords(self, keywords: list[dict], seed_keywords: list[str]) -> list[dict]:
        """评分关键词"""
        system_prompt = """你是一个 SEO 关键词评估专家。对给定的关键词进行评分。

评估维度：
1. 搜索意图（informational / transactional / navigational）
2. 竞争度估算（low / medium / high）
3. 内容类型匹配（blog / FAQ / landing page）
4. 与临时邮箱服务的相关性（1-10）

返回 JSON 格式：
{
    "scored_keywords": [
        {
            "keyword": "关键词",
            "type": "扩展类型",
            "intent": "informational/transactional/navigational",
            "competition": "low/medium/high",
            "content_type": "blog/FAQ/landing page",
            "relevance": 8,
            "suggested_title": "建议的文章标题",
            "score": 85
        }
    ]
}

评分标准：
- 相关性权重 40%
- 竞争度权重 30%（low=高分）
- 搜索意图权重 20%（informational=高分）
- 内容类型权重 10%（blog=高分）

只返回 JSON，不要其他内容。"""

        user_prompt = f"""请对以下关键词进行评分：

种子关键词：{', '.join(seed_keywords)}
待评分关键词：
{json.dumps([kw.get("keyword", "") for kw in keywords[:30]], ensure_ascii=False)}

请返回 JSON 格式的评分结果。"""

        result = await self._call_llm(system_prompt, user_prompt, temperature=0.3)

        try:
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(result)
            return data.get("scored_keywords", [])
        except Exception as e:
            logger.error(f"解析评分结果失败: {e}")
            return keywords

    async def _deduplicate_and_sort(self, keywords: list[dict], num_results: int) -> list[dict]:
        """去重和排序"""
        # 读取已有关键词
        existing_keywords = await self._load_existing_keywords()
        logger.info(f"已有关键词: {len(existing_keywords)} 个")

        # 去重
        unique_keywords = []
        seen = set()
        for kw in keywords:
            keyword = kw.get("keyword", "").lower().strip()
            if keyword and keyword not in seen and keyword not in existing_keywords:
                seen.add(keyword)
                unique_keywords.append(kw)

        # 按评分排序
        sorted_keywords = sorted(
            unique_keywords,
            key=lambda x: x.get("score", 0),
            reverse=True,
        )

        # 返回 Top N
        return sorted_keywords[:num_results]

    async def _load_existing_keywords(self) -> set[str]:
        """加载已有关键词"""
        existing = set()

        # 从 KEYWORD_RESEARCH.md 读取
        keyword_file = PROJECT_ROOT / "docs" / "KEYWORD_RESEARCH.md"
        if keyword_file.exists():
            try:
                content = keyword_file.read_text(encoding="utf-8")
                # 提取关键词（简单匹配）
                for line in content.split("\n"):
                    if line.strip().startswith("- ") or line.strip().startswith("* "):
                        keyword = line.strip()[2:].lower()
                        if keyword:
                            existing.add(keyword)
            except Exception as e:
                logger.warning(f"读取 KEYWORD_RESEARCH.md 失败: {e}")

        # 从已有文章标题读取
        blog_dir = PROJECT_ROOT / "sites" / "site-01" / "frontend" / "src" / "routes"
        if blog_dir.exists():
            for file in blog_dir.glob("blog.*.tsx"):
                try:
                    content = file.read_text(encoding="utf-8")
                    # 提取标题
                    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
                    if title_match:
                        title = title_match.group(1).strip().lower()
                        existing.add(title)
                except Exception as e:
                    logger.warning(f"读取 {file} 失败: {e}")

        return existing

    async def feed_factory(self, result: dict, num_articles: int = 5) -> list[str]:
        """将关键词喂给内容工厂

        Args:
            result: 关键词发现结果
            num_articles: 生成文章数量

        Returns:
            任务 ID 列表
        """
        from backend.services.content_factory import content_factory_service
        from backend.schemas.content_factory import ContentFactoryRequest

        task_ids = []
        keywords = result.get("keywords", [])[:num_articles]

        for kw in keywords:
            keyword = kw.get("keyword", "")
            if not keyword:
                continue

            logger.info(f"启动内容工厂: {keyword}")

            # 创建请求
            request = ContentFactoryRequest(
                keyword=keyword,
                language="en",
                word_count_min=1500,
                word_count_max=3000,
            )

            # 启动流水线
            task_id = None
            async for progress in content_factory_service.run_pipeline(request):
                if progress.stage_id == 0:  # 完成或失败
                    task_id = progress.task_id

            if task_id:
                task_ids.append(task_id)

        return task_ids


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="关键词自动发现工具 - 为内容工厂供词"
    )
    parser.add_argument(
        "keywords",
        nargs="*",
        help="种子关键词列表"
    )
    parser.add_argument(
        "-k", "--keyword",
        action="append",
        help="添加单个关键词（可多次使用）"
    )
    parser.add_argument(
        "-n", "--num",
        type=int,
        default=20,
        help="返回结果数量（默认 20）"
    )
    parser.add_argument(
        "-l", "--language",
        default="en",
        help="语言代码（默认 en）"
    )
    parser.add_argument(
        "--feed-factory",
        action="store_true",
        help="将 Top 5 关键词喂给内容工厂"
    )
    parser.add_argument(
        "--feed-num",
        type=int,
        default=5,
        help="喂给内容工厂的关键词数量（默认 5）"
    )

    args = parser.parse_args()

    # 合并关键词
    seed_keywords = args.keywords or []
    if args.keyword:
        seed_keywords.extend(args.keyword)

    if not seed_keywords:
        parser.print_help()
        print("\n❌ 错误：请提供至少一个种子关键词")
        sys.exit(1)

    # 创建发现器
    discovery = KeywordDiscovery()

    try:
        # 运行发现
        result = await discovery.discover(
            seed_keywords=seed_keywords,
            num_results=args.num,
            language=args.language,
        )

        # 打印结果
        print("\n" + "=" * 70)
        print(f"✅ 关键词发现完成")
        print("=" * 70)
        print(f"种子关键词：{', '.join(seed_keywords)}")
        print(f"发现数量：{result['total_discovered']}")
        print(f"输出文件：docs/keyword-discovery-{datetime.now().strftime('%Y%m%d')}.json")
        print()

        # 打印 Top 10
        print("📊 Top 10 关键词：")
        print("-" * 70)
        for i, kw in enumerate(result["keywords"][:10], 1):
            print(f"{i:2d}. {kw.get('keyword', '')}")
            print(f"    评分: {kw.get('score', 0)} | 竞争度: {kw.get('competition', 'N/A')} | 相关性: {kw.get('relevance', 0)}/10")
            print(f"    建议标题: {kw.get('suggested_title', 'N/A')}")
            print()

        # 喂给内容工厂
        if args.feed_factory:
            print("\n🚀 启动内容工厂...")
            task_ids = await discovery.feed_factory(result, args.feed_num)
            print(f"✅ 已启动 {len(task_ids)} 个任务")
            for task_id in task_ids:
                print(f"   - 任务 ID: {task_id}")

    except Exception as e:
        logger.error(f"关键词发现失败: {e}")
        print(f"\n❌ 失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
