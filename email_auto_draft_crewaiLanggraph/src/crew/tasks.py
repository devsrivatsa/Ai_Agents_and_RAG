from crewai import Task
from textwrap import dedent

class EmailFilterTasks:
	
    def filter_emails_task(self, agent, emails):
        return Task(
			description=dedent(f"""\
				Filter through the following emails and identify which ones require action:

    			{emails}

    			Determine which emails need a response or action. Consider factors like:
    			- Urgency of the request
    			- Importance of the sender
    			- Complexity of the task requested
    			- Deadline mentioned in the email

    			Provide your analysis and list of emails requiring action.
    			"""),
			agent=agent,
			expected_output=dedent("""\
				A dictionary containing:
				- "checked_email_ids": A list of all email IDs that were checked
				- "action_required_email": A list of email IDs that require action
			""")
		)
	
    def action_required_emails_task(self, agent):
        return Task(
			description=dedent(f"""\
					  For each email thread, pull and analyze the complete threads using only the actual Thread ID.
					  Understand the context, key points and overall sentiment of the conversation.
					  
					  Identify the main query or concerns that need to be addressed in the response for each.
					  
					  Your final answer must be a list of all emails with:
					  - the thread_id
					  - the summary of the email thread
					  - a highlighting with the main points
					  - identify the user and who she/he will be answering to
					  - communication style in the thread
					  - the sender's email address
					  """),
			agent=agent,
			expected_output=dedent("""\
				A list of dictionaries, each containing:
				- "thread_id": The ID of the email thread
				- "summary": A brief summary of the email thread
				- "main_points": Key points highlighted from the thread
				- "user": The user who will be responding
				- "recipient": The person to whom the response will be sent
				- "communication_style": The style of communication observed in the thread
				- "sender_email": The email address of the sender
			""")
        )
	
    def draft_response_task(self, agent):
        return Task(
            description=dedent("""\
                                Draft responses for each of the identified action-required emails. 
                                Ensure that each response is tailored to address the specific needs and concerns outlined in the emails.

                               - Assume the persona of the user and mimic the communication style in the thread.
                               - If necessary, feel free to research more on the topic inorder to provide a more detailed response.
                               - If research is needed, do it before drafting the response.
                               - If you need to pull the thread, do it using the thread_id.

                               Use the tool provided to draft each of the responses. 
                               When using the tool, pass the following inputs:
                               - to (sender to be responded)
                               - subject
                               - message

                               You must create all the drafts before sending your final answer.
                               Your final answer must be a confirmation that all the responses have been drafted."""),
            agent=agent,
            expected_output=dedent("""\
                A dictionary containing:
                - "drafted_responses": A list of dictionaries, each containing:
                    - "to": The recipient's email address
                    - "subject": The subject of the email
                    - "message": The drafted message body
                - "confirmation": A string confirming that all responses have been drafted
            """)
        )
    