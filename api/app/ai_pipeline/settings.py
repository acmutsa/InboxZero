"""Pipeline thresholds, read from environment variables with a PIPELINE_ prefix.

Kept separate from app.config so the gates can be imported and tested without
the database, Redis and Google settings. Every value has a default.
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class PipelineSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIPELINE_")

    # Gate 2: minimum classifier confidence to go on to drafting. The binning
    # prompt tells the model to lean toward "reply" and use 0.5-0.69 for real
    # judgment calls, so 0.5 lets those through. Raise it for fewer drafts.
    bin_confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

    # How many times an LLM step is retried after its gate rejects the output.
    max_retries: int = Field(default=2, ge=0)

    # Longest text sent to the LLM for the email itself and for the previous
    # message in its thread. Longer text is cut, to bound tokens and cost.
    body_max_chars: int = Field(default=10_000, gt=0)
    previous_message_max_chars: int = Field(default=4_000, gt=0)


pipeline_settings = PipelineSettings()
