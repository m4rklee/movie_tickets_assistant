from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "mysql+pymysql://ticket:ticket_secret@127.0.0.1:3306/filmarchive_wallet"
    ticket_api_key: str = ""
    upload_dir: str = "./uploads"
    draft_ttl_days: int = 7
    cors_origins: str = "*"


settings = Settings()
