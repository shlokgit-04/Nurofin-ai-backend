try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nurofin Executive AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "a-very-secret-key-change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "qwerty"
    POSTGRES_DB: str = "nurofin_db"
    POSTGRES_PORT: str = "5432"
    
    GOOGLE_CLIENT_ID: str = "YOUR_GOOGLE_CLIENT_ID"
    GOOGLE_CLIENT_SECRET: str = "YOUR_GOOGLE_CLIENT_SECRET"
    GOOGLE_PROJECT_ID: str = "YOUR_PROJECT_ID"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        import os
        
        # 1. Use DATABASE_URL if it's provided (e.g. by Render)
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
            elif db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
            return db_url
            
        # 2. Use explicit SQLite fallback
        if os.getenv("USE_SQLITE", "").lower() in ("true", "1"):
            return "sqlite+aiosqlite:///./nurofin_db.db"
            
        # 3. Fallback to local Postgres
        import socket
        try:
            with socket.create_connection((self.POSTGRES_SERVER, int(self.POSTGRES_PORT)), timeout=0.5):
                return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        except Exception:
            return "sqlite+aiosqlite:///./nurofin_db.db"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

