from typing_extensions import TypedDict

class CalcState(TypedDict):

    request: str       # the original request
    result: str        # latest result (add step, then overwritten by multiply)
    mul_context: str   # number to multiply by