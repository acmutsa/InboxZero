from api.app.ai_pipeline.states import CalcState
from api.app.ai_pipeline.agents import agent_add,agent_mul

def add_node(state: CalcState):
    out = agent_add.invoke({"messages": [("user", state["request"])]})

    print(out)
    return {"result": out["messages"][-1].text}

def mul_node(state: CalcState):
    out = agent_mul.invoke(
        {"messages": [("user",
            f"Multiply {state['result']} by {state['mul_context']}.")]}
    )
    print(out)
    return {"result": out["messages"][-1].text}

def email_binning_gate():
    pass

def email_drafting_gate():
    pass
