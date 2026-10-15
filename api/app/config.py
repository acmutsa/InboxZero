from pathlib import Path

from typing import Annotated

from pydantic import AfterValidator
from pydantic import Field
from pydantic import HttpUrl
from pydantic import PostgresDsn
from pydantic import RedisDsn
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

HttpUrlStr = Annotated[HttpUrl, AfterValidator(str)]
PostgresUrlStr = Annotated[PostgresDsn, AfterValidator(str)]
RedisUrlStr = Annotated[RedisDsn, AfterValidator(str)]
Secret32 = Annotated[str, Field(min_length=44)]

class Config(BaseSettings):
    # postgres 
    POSTGRES_HOST:str 
    POSTGRES_PORT:int
    POSTGRES_USER:str 
    POSTGRES_PASSWORD:str
    POSTGRES_DB:str = "inbox-zero-db"
    POSTGRES_URL: PostgresUrlStr

    # redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: RedisUrlStr

    # google
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_PROJECT_ID: str
    GOOGLE_AUTH_URI: HttpUrlStr = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URI: HttpUrlStr = "https://oauth2.googleapis.com/token"
    GOOGLE_AUTH_PROVIDER_X509_CERT_URL: HttpUrlStr = "https://www.googleapis.com/oauth2/v1/certs"
    GOOGLE_REDIRECT_URIS: list[HttpUrl]
    GOOGLE_JAVASCRIPT_ORIGINS: list[HttpUrl]
    GOOGLE_REDIRECT_URI: HttpUrlStr = "http://localhost:8000/auth/google/callback"
    SCOPES: list[str]
    GOOGLE_STATE_SECRET: Secret32
    GOOGLE_STATE_EXPIRE_SECONDS: int = 600
    GOOGLE_REFRESH_TOKEN_SECRET: Secret32

    # app
    ENVIRONMENT: str = "development"
    CORS: list[HttpUrl] = ["http://localhost:3000"]
    ALGORITHM: str = "HS256"
    SECRET_KEY: Secret32
    AUDIENCE: list[HttpUrl]
    

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

    @property
    def get_cors_list(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.CORS]

    @property
    def get_audience_list(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.AUDIENCE]

    @property
    def get_google_redirect_uris(self) -> list[str]:
        return [str(uri).rstrip("/") for uri in self.GOOGLE_REDIRECT_URIS]

    @property
    def get_google_javascript_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.GOOGLE_JAVASCRIPT_ORIGINS]

    @property
    def get_google_client_config(self) -> dict:
        return {
            "web": {
                "client_id": self.GOOGLE_CLIENT_ID,
                "project_id": self.GOOGLE_PROJECT_ID,
                "auth_uri": self.GOOGLE_AUTH_URI,
                "token_uri": self.GOOGLE_TOKEN_URI,
                "auth_provider_x509_cert_url": self.GOOGLE_AUTH_PROVIDER_X509_CERT_URL,
                "client_secret": self.GOOGLE_CLIENT_SECRET,
                "redirect_uris": self.get_google_redirect_uris,
                "javascript_origins": self.get_google_javascript_origins,
            }
        }

def get_config() -> Config:
    return Config()


config = get_config()
