from pathlib import Path

from app.ai_pipeline.prompt_templates import user_prompt_middleware
from app.ai_pipeline.user_context import UserContext
from langchain.agents import create_agent
from app.config import config


PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
draft_filename = PROMPTS_DIR / "email_drafting.md"
bin_filename = PROMPTS_DIR / "email_binning.md"


def read_md(filename: Path) -> str:
    return filename.read_text(encoding="utf-8")

# The prompts are templates. The system prompt is filled in on every run from
# the UserContext passed as `context=` to invoke (see nodes.py).
agent_bin = create_agent(
    model=config.GEMINI_MODEL,
    model="google_genai:gemini-3.5-flash-lite",
    middleware=[user_prompt_middleware(read_md(bin_filename))],
    context_schema=UserContext,
)
agent_draft = create_agent(
    model=config.GEMINI_MODEL,
    model="google_genai:gemini-3.5-flash-lite",
    middleware=[user_prompt_middleware(read_md(draft_filename))],
    context_schema=UserContext,
)
