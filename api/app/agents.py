from tools import add,multiply
from langchain.agents import create_agent
mul_filename = "prompts/email_drafting.md"
add_filename = "prompts/email_binning.md"



def read_md(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        phrase = f.read()
        print(phrase)
        return f.read()


agent_add = create_agent(
    model="google_genai:gemini-3.5-flash-lite",
    tools=[add],
    system_prompt=read_md(add_filename)
)
agent_mul = create_agent(
    model="google_genai:gemini-3.5-flash-lite",
    tools=[multiply],
    system_prompt=read_md(mul_filename),
)


