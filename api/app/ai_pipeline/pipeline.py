from langgraph.graph import StateGraph, START, END

from api.app.ai_pipeline.types.states import EmailState
from app.ai_pipeline.nodes import (
    code_check_node, ai_bin_node, categorize_node, ai_draft_node,
    record_skip, handle_failure, save_draft,
)
from app.ai_pipeline.gates import (
    email_binning_gate, email_drafting_gate,
    route_after_bin_gate, route_after_categorize, route_after_gate,
)

g = StateGraph(EmailState)

g.add_node("code_check", code_check_node)
g.add_node("ai_bin_check", ai_bin_node)
g.add_node("ai_bin_gate", email_binning_gate)
g.add_node("categorize", categorize_node)
g.add_node("draft_ai", ai_draft_node)
g.add_node("ai_draft_gate", email_drafting_gate)
g.add_node("save_draft", save_draft)
g.add_node("record_skip", record_skip)
g.add_node("handle_failure", handle_failure)

# 1. Gate 1: deterministic checks → (skip | classify)
# Only emails that pass are classified and categorized.
g.add_edge(START, "code_check")
g.add_conditional_edges("code_check", route_after_gate, {
    "Success": "ai_bin_check",
    "Skip": "record_skip",
    "Error": "handle_failure",
    "GiveUp": "handle_failure",
})

# 2. Gate 2: AI → gate → (retry AI | categorize)
g.add_edge("ai_bin_check", "ai_bin_gate")
g.add_conditional_edges("ai_bin_gate", route_after_bin_gate, {
    "Categorize": "categorize",
    "Error": "ai_bin_check",      
    "GiveUp": "handle_failure",
})

# Categorize: file the email in the DB and the mailbox → (skip if no reply | draft)
g.add_conditional_edges("categorize", route_after_categorize, {
    "Draft": "draft_ai",
    "Skip": "record_skip",
})

# 3. Gate 3: AI → gate → (retry AI | save)
g.add_edge("draft_ai", "ai_draft_gate")
g.add_conditional_edges("ai_draft_gate", route_after_gate, {
    "Success": "save_draft",
    "Skip": "record_skip",
    "Error": "draft_ai",
    "GiveUp": "handle_failure",
})

g.add_edge("save_draft", END)
g.add_edge("record_skip", END)
g.add_edge("handle_failure", END)

email_graph = g.compile()
