from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    github_app_id:int
    github_private_key:str
    webhook_secret:str
    google_api_key: str
    model_config=SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")
settings=Settings()