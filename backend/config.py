"""
CrazyMail 全局配置
所有配置项通过环境变量注入，不得硬编码
"""
import os
from pydantic import BaseModel


class Settings(BaseModel):
    """应用配置"""

    # 应用基础
    app_name: str = "CrazyMail"
    app_version: str = "0.1.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 数据库
    database_url: str = os.getenv("DATABASE_URL", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")

    # LLM API Keys
    mimo_api_key: str = os.getenv("MIMO_API_KEY", "")
    agnes_api_key: str = os.getenv("AGNES_API_KEY", "")

    # 内容生产配置
    content_pipeline_concurrency: int = int(os.getenv("CONTENT_PIPELINE_CONCURRENCY", "3"))
    qa_ai_detection_threshold: int = int(os.getenv("QA_AI_DETECTION_THRESHOLD", "30"))
    qa_seo_score_threshold: int = int(os.getenv("QA_SEO_SCORE_THRESHOLD", "75"))
    qa_max_retries: int = int(os.getenv("QA_MAX_RETRIES", "3"))
    human_review_enabled: bool = os.getenv("HUMAN_REVIEW_ENABLED", "true").lower() == "true"

    # LLM 模型选择
    writing_model_primary: str = os.getenv("WRITING_MODEL_PRIMARY", "mimo-v2.5-pro")
    writing_model_fallback: str = os.getenv("WRITING_MODEL_FALLBACK", "agnes-2.0-flash")
    research_model: str = os.getenv("RESEARCH_MODEL", "agnes-2.0-flash")

    # 皇城司配置
    isolation_scan_enabled: bool = os.getenv("ISOLATION_SCAN_ENABLED", "true").lower() == "true"
    isolation_scan_schedule: str = os.getenv("ISOLATION_SCAN_SCHEDULE", "0 6 * * *")

    # 人格系统配置
    persona_human_feel_heroes: float = float(os.getenv("PERSONA_HUMAN_FEEL_HEROES", "0.85"))
    persona_human_feel_officials: float = float(os.getenv("PERSONA_HUMAN_FEEL_OFFICIALS", "0.35"))
    persona_profiles_path: str = os.getenv("PERSONA_PROFILES_PATH", "backend/personas")


settings = Settings()
