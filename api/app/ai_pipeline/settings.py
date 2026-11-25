from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class PipelineSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIPELINE_")
    bin_confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    max_retries: int = Field(default=2, ge=0)
    body_max_chars: int = Field(default=10_000, gt=0)
    previous_message_max_chars: int = Field(default=4_000, gt=0)


pipeline_settings = PipelineSettings()
