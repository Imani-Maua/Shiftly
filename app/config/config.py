from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST : str
    DB_NAME : str
    DB_USER : str
    DB_PASSWORD : str
    DATABASE_URL : str
    KEY : str
    SMTP_HOST : str
    SMTP_PORT : int
    SMTP_USER : str
    SMTP_PASS : str
    PASSWORD: str

    class Config:
        env_file = ".env"