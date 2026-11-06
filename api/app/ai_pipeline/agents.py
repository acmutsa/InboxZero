from tools import add,multiply
from langchain.agents import create_agent
draft_filename = "prompts/email_drafting.md"
bin_filename = "prompts/email_binning.md"



def read_md(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        phrase = f.read()
        #print(phrase)
        return f.read()


agent_bin = create_agent(
    model="google_genai:gemini-3.5-flash-lite",
    tools=[add],
    system_prompt=read_md(bin_filename)
)
agent_draft = create_agent(
    model="google_genai:gemini-3.5-flash-lite",
    tools=[multiply],
    system_prompt=read_md(draft_filename),
)



