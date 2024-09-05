import os
import time
from langchain_community.agent_toolkits import GmailToolkit

class Node:
    def __init__(self):
        self.gmail = GmailToolkit()
        self.gmail_tools = self.gmail.get_tools()

    def check_email(self, state):
        print("Checking email")
        search = self.gmail_tools[2]
        
        emails = search("after:newer_than:1d")
        checked_emails = state["checked_emails_ids"] if state["checked_emails_ids"] else []
        thread = []
        new_emails = []
        for email in emails:
            if (email["id"] not in checked_emails) \
                and (email["threadId"] not in thread) \
                and (os.environ["MY_EMAIL"] not in email["sender"]):

                thread.append(email["threadId"])
                new_emails.append(
                    {
                        "id": email["id"],
                        "threadId": email["threadId"],
                        "snippet": email["snippet"],
                        "sender": email["sender"]
                    }
                )
        checked_emails.extend([email["id"] for email in emails])
        return {
            **state,
            "emails": new_emails,
            "checked_emails_ids": checked_emails
        }

    def wait_next_run(self, state):
        print("##waiting for 180 seconds")
        time.sleep(180)
        return state

    def new_emails(self, state):
        if len(state["emails"]) == 0:
            print("## no new emails")
            return "__end__"
        else:
            print("## new emails found")
            return "continue"
    
if __name__ == "__main__":
    node = Node()
    print(node.gmail_tools)
