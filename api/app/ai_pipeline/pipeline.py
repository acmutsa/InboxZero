from states import EmailState
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from agents import agent_bin,agent_draft
from nodes import ai_draft_node,ai_bin_node,code_check_node,route_after_code_node,handle_failure

from fake_gmail import FAKE_GMAIL_MESSAGE, make_mock_service,get_body
from unittest.mock import Mock


# import time
# from langchain.chat_models import init_chat_model

# start = time.perf_counter()
# response = init_chat_model("google_genai:gemini-3.5-flash-lite").invoke("hi",max_retries=0,timeout=10)
# elapsed = time.perf_counter() - start

# print(response.content)
# print(f"Elapsed: {elapsed:.3f}s")

mock_service = Mock()
#print(message)

email: EmailState


g = StateGraph(EmailState)

g.add_node("code_check",code_check_node)
g.add_node("handle_failure",handle_failure)

g.add_edge(START,"code_check")

g.add_conditional_edges(
    "code_check",
    "route_after_code",
    {
        "Success":NEXT,
        "Error": "handle_failure",
    },



)

g.add_edge("handle_failure",END)

# g.add_node("draft", ai_draft_node)
# g.add_node("bin", ai_bin_node)
# g.add_edge(START, "bin")
# g.add_edge("bin", "draft")
# g.add_edge("draft", END)

# graph.add_conditional_edges(
#     "parse_output",          # after this node...
#     route_after_parse,       # ...run this function...
#     {                        # ...and map its answer to the next node
#         "success": END,
#         "retry": "call_model",
#         "give_up": "handle_failure",
#     },
# )

# graph.add_edge("handle_failure", END)






app = g.compile()

mock_service.users().messages().get().execute.return_value = FAKE_GMAIL_MESSAGE
message = mock_service.users().messages().get().execute()
headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
label_ids = message.get("labelIds", [])

result = app.invoke({
    "label_ids" : label_ids,
    "headers": headers,
    "body": get_body(message) or "",
    "raw_output": None,
    "parsed": None,
    "error": None,
    "attempts": 0,
})

print(result["header_from"])
