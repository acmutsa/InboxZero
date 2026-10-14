from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    ENVIRONMENT: str = "development"
    CORS: str = "http://localhost:3000"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    AUDIENCE: str
    DATABASE_URL: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_PROJECT_ID: str
    GOOGLE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    GOOGLE_AUTH_PROVIDER_X509_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URIS: list[str]
    GOOGLE_JAVASCRIPT_ORIGINS: list[str]
    SCOPES: list[str]
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/gmail/auth/redirect"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def get_cors_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS.split(",")
            if origin.strip()
        ]

    @property
    def get_audience_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.AUDIENCE.split(",") if origin.strip()
        ]

    @property
    def get_google_redirect_uris(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.GOOGLE_REDIRECT_URIS.split(",")
            if origin.strip()
        ]

    @property
    def get_google_javascript_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.GOOGLE_JAVASCRIPT_ORIGINS.split(",")
            if origin.strip()
        ]
    
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
    
    @property
    def get_scopes(self) -> list[str]:
        return [
            origin.strip() 
            for origin in self.SCOPES.split(",") 
            if origin.strip()
        ]


def get_config() -> Config:
    return Config()


config = get_config()