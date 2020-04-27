import json
import logging
import requests

from github import Github
from flask import Flask
from flask import request
from flask import Response

from utils import log
from utils import fail_log
from config import configure_app


# Authentication for user filing issue (must have read/write access to
# repository to add issue to)
USERNAME = ''
PASSWORD = ''

# The repository to add this issue to
REPO_OWNER = ''
REPO_NAME = ''

TRIGGER_TYPE = "issue_created"
PROJECT_NAME = ""

app = Flask(__name__)
configure_app(app)


LOGIN_DICT = {}


def make_github_issue(title, assignee=None):
	try:
		g = Github(USERNAME, PASSWORD)
		repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
		if assignee:
			issue = repo.create_issue(title=title, assignee=assignee)
		else:
			issue = repo.create_issue(title=title)
	except Exception as e:
		log(logging.ERROR, "Could not create github issue {0}".format(e))

def get_named_user(dict_key):
	g = Github(USERNAME, PASSWORD)
	user = None
	try:
		search_term = LOGIN_DICT[dict_key]
		log(logging.INFO, "Searching user with {0}".format(search_term))
		user = g.get_user(search_term)
	except Exception as e:
		log(logging.ERROR, "Could not find user: {0}".format(e))
	return user

@app.route('/', methods=['POST'])
def handle_jira_webhook():
	try:
		request_json = request.get_json()
	except Exception as e:
		log(logging.ERROR, "Requst.get_json() failed: {0}".format(e))

	try:
		issue_event_type = request_json["issue_event_type_name"]
	except Exception as e:
		log(logging.ERROR, "Could not get issue event type: {0}".format(e))
		fail_log("Could not create issue for: {0} with error: {1}".format(request_json, e))
		return Response(status=200)

	log(logging.INFO, "issue_event_type: {0}".format(issue_event_type))
	if issue_event_type != TRIGGER_TYPE:
		log(logging.INFO, "Skipping: Different Issue Event Type -> {0}".format(issue_event_type))
		return Response(status=200)

	try:
		issue_project_name = request_json["issue"]["fields"]["project"]["name"]
	except Exception as e:
		log(logging.ERROR, "Could not get issue project name: {0}".format(e))
		fail_log("Could not create issue for: {0} with error: {1}".format(request_json, e))
		return Response(status=200)

	log(logging.INFO, "issue_project_name: {0}".format(issue_project_name))
	if issue_project_name != PROJECT_NAME:
		log(logging.INFO, "Skipping: Different Project -> {0}".format(issue_project_name))
		return Response(status=200)

	try:
		issue_key = request_json["issue"]["key"]
		issue_summary = request_json["issue"]["fields"]["summary"]
	except Exception as e:
		log(logging.ERROR, "Could not get necessary fields: {0}".format(e))
		fail_log(logging.ERROR, "Could not create issue for: {0} with error: {1}".format(request_json, e))
		return Response(status=200)

	try:
		issue_assignee_email = request_json["issue"]["fields"]["assignee"]["emailAddress"]	
	except Exception as e:
		issue_assignee_email = None	

	log(logging.INFO, "issue_summary: {0}".format(issue_summary))
	log(logging.INFO, "issue_key: {0}".format(issue_key))
	log(logging.INFO, "issue_assignee_email: {0}".format(issue_assignee_email))

	github_issue_title = "{0} {1}".format(issue_key, issue_summary)
	assignee = None
	if issue_assignee_email:
		assignee = get_named_user(issue_assignee_email)

	make_github_issue(github_issue_title, assignee=assignee)
	return Response(status=200)

if __name__ == "__main__":
	app.run(host='0.0.0.0')
