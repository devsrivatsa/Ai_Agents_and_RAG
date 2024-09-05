## This is a general templae for an agentic Email automation with crewai and langgraph.
(This is based out of the example in the official crew ai repo but with a few changes)

- Update openai, tavily, langsmith api keys in the .env file and place it at the root of the project.
- Setup a credentials.json: Follow the google instructions ( https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application ), once you’ve downloaded the file, name it credentials.json and add to the root of the project.
- Install Dependencies: Run pip install -r requirements.txt
- Run main.py
