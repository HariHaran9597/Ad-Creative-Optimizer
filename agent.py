from langgraph.graph import StateGraph
from text_optimizer import generate_ad_variants
from image_analyzer import analyze_all_images
import json
from typing import TypedDict, List, Annotated
from typing_extensions import TypedDict

# Define state structure
class AgentState(TypedDict):
    text: str
    variants: List[str]
    image_analyses: List[dict]
    ranked_ads: List[dict]
    best_variant: str

# Initialize the graph
workflow = StateGraph(AgentState)

# Load sample ads and analyze all images
with open("data/ads.json") as f:
    ads = json.load(f)
image_analyses = analyze_all_images()

# Define nodes
def text_optimize(state: AgentState):
    variants = generate_ad_variants(state["text"])
    return {"variants": variants.split("\n")}

def image_analyze(state: AgentState):
    return {"image_analyses": image_analyses}

def rank_ads(state: AgentState):
    # Rank ads by text coverage
    ranked_ads = sorted(
        state["image_analyses"],
        key=lambda x: x["text_coverage"],
        reverse=True
    )
    
    # Get top variant
    best_variant = state["variants"][0]
    
    return {
        "ranked_ads": ranked_ads,
        "best_variant": best_variant
    }

# Add nodes to workflow
workflow.add_node("text_optimize", text_optimize)
workflow.add_node("image_analyze", image_analyze)
workflow.add_node("rank_ads", rank_ads)

# Define edges
workflow.add_edge("text_optimize", "rank_ads")
workflow.add_edge("image_analyze", "rank_ads")

# Set entry points (now properly using StateGraph)
workflow.add_conditional_edges(
    "rank_ads",
    lambda x: "end",
    None
)

# Set entry points for parallel execution
workflow.set_entry_point("text_optimize")
workflow.set_entry_point("image_analyze")

# Compile the workflow
app = workflow.compile()

# Execute with proper initial state
initial_state = {
    "text": ads[0]["text"],
    "variants": [],
    "image_analyses": [],
    "ranked_ads": [],
    "best_variant": ""
}

results = app.invoke(initial_state)
print(json.dumps(results, indent=2))