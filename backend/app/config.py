from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./luckydraw.db"
    DRAW_HASH_SALT: str = "lucky_salt"  # 可换成更安全的环境变量
    ADMIN_TOKEN: str = "admin123"  # 简易管理员令牌，可在 .env 覆盖

    class Config:
        env_file = ".env"

settings = Settings()
