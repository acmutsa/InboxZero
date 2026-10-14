from states import CalcState
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from agents import agent_add,agent_mul
from nodes import add_node,mul_node



# import time
# from langchain.chat_models import init_chat_model

# start = time.perf_counter()
# response = init_chat_model("google_genai:gemini-3.5-flash-lite").invoke("hi",max_retries=0,timeout=10)
# elapsed = time.perf_counter() - start

# print(response.content)
# print(f"Elapsed: {elapsed:.3f}s")


g = StateGraph(CalcState)
g.add_node("add", add_node)
g.add_node("mul", mul_node)
g.add_edge(START, "add")
g.add_edge("add", "mul")
g.add_edge("mul", END)
app = g.compile()


num1 = input("First number: ")
num2 = input("Second number: ")
num3 = input("Multiply by: ")

result = app.invoke({
    "request": f"Add {num1} and {num2}",
    "mul_context": num3,
})

print(result["result"])