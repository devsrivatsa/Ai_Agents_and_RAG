from graph import Workflow

if __name__ == "__main__":
    app = Workflow().app
    app.invoke({"checked_emails_ids": None})