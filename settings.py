from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):

    """데이터베이스 설정"""
    DB_USER: str = "your_username"
    DB_PASSWORD: str = "your_password"
    DB_HOST: str = "localhost"
    DB_PORT: str = "1521"
    DB_SERVICE: str = "your_service"

    # 추가 설정들
    SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    SQLALCHEMY_DATABASE_URL: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    ORGANIZATION_ID: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: Optional[str] = None
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    ORACLE_CLIENT_DIR: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False  # 환경 변수 이름의 대소문자 구분 없앰
        extra = "ignore"  # 추가 필드 허용


@lru_cache()
def get_settings() -> Settings:
    """데이터베이스 설정 싱글톤"""
    return Settings()
