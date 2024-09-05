from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph

from nodes import Node
from state import EmailState
from crew.crew import EmailFilterCrew

class Workflow:
    def __init__(self):
        nodes = Node()
        workflow = StateGraph(EmailState)
        #nodes    
        workflow.add_node("check_new_emails", nodes.check_email)
        workflow.add_node("wait_next_run", nodes.wait_next_run)
        workflow.add_node("draft_responses", EmailFilterCrew().kickoff)
        #entry point
        workflow.set_entry_point("check_new_emails")
        #edges
        workflow.add_edge("draft_responses", "wait_next_run")
        workflow.add_edge("wait_next_run", "check_new_emails")
        workflow.add_conditional_edges(
            "check_new_emails",
            nodes.new_emails,
            {
                "continue": "draft_responses",
                "__end__": "wait_next_run"
            }
        )
        self.app = workflow.compile()

# if __name__ == "__main__":
#     from IPython.display import Image, display
    
#     app = Workflow()
#     display(Image(app.get_graph().draw_mermaid(), width=800, height=800))