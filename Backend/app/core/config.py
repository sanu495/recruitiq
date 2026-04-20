from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    # Database
    DATABASE_URL: str = "sqlite:///./recruitiq.db"

    # JWT
    SECRET_KEY: str = "36869c4d9d7df154cd03817e7a6202b6ab372b676a8dcf61100053e1a2745316"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
 
    # Groq AI
    GROQ_API_KEY: str = ""

    # Upload
    UPLOAD_DIR: str = "/tmp/uploads"

    class Config:
        env_file = ".env"

settings = Settings()
    