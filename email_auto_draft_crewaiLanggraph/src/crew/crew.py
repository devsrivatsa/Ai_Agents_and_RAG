from crewai import Crew
from .agents import EmailFilterAgents
from .tasks import EmailFilterTasks

class EmailFilterCrew:
    def __init__(self):
        agents = EmailFilterAgents()
        self.filter_agent = agents.email_filter_agent()
        self.action_agent = agents.email_action_agent()
        self.writer_agent = agents.email_response_writer()

    def kickoff(self, state):
        print("### Filtering Emails ###")
        tasks = EmailFilterTasks()
        crew = Crew(
            agents=[self.filter_agent, self.action_agent, self.writer_agent],
            tasks=[
                tasks.filter_emails_task(self.filter_agent, self._format_emails(state['emails'])),
                tasks.action_required_emails_task(self.action_agent),
                tasks.draft_response_task(self.writer_agent)
            ],
            verbose=True
        )
        result = crew.kickoff()
        
        # Process the result and update the state
        processed_result = self._process_crew_result(result)
        return {
            **state,
            "checked_email_ids": processed_result.get("checked_email_ids", []),
            "action_required_email": processed_result.get("action_required_email", [])
        }

    def _process_crew_result(self, result):
        # This method should process the crew result and extract the required information
        # Adjust this based on the actual structure of your crew's output
        processed = {}
        for task_result in result:
            if isinstance(task_result, dict):
                processed.update(task_result)
        return processed

    def _format_emails(self, emails):
        emails_string = []
        for email in emails:
            arr = [
                f"ID: {email['id']}",
                f"- Thread ID: {email['threadId']}",
                f"- Snippet: {email['snippet']}",
                f"- From: {email['sender']}",
                f"..............................."
            ]
            emails_string.append("\n".join(arr))
        return "\n".join(emails_string)
