from pydantic import BaseModel, ConfigDict, Field, model_validator

class DraftValidate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)             
    placeholders: list[str] = []
    needs_review: bool

    @model_validator(mode="after")
    def placeholders_appear_in_body(self) -> "DraftValidate":
        missing = [p for p in self.placeholders if p not in self.body]
        if missing:
            raise ValueError(f"placeholders not found in body: {missing}")
        return self

  