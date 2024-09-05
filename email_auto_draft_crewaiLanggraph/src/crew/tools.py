from langchain_community.agent_toolkits.gmail.toolkit import GmailToolkit
from langchain_community.tools.gmail.create_draft import GmailCreateDraft
from langchain.tools import tool

class CreateDraftTool:
    @tool("Create Draft")
    def create_draft(data):
        """useful to create an email draft.
        The input to this tool sould be a pipe (|) separated text of length 3, representing
        the recipient, subject, and the actual message of the email.
        For example: lorem@ipsum.com|Test|This is a test email"""

        email, subject, message = data.split("|")
        gmail = GmailToolkit()
        draft = GmailCreateDraft(api_resource=gmail.api_resource)
        result = draft({"to": [email], "subject": subject, "message": message})
        return f"\nDraft Created: {result}\n"
    