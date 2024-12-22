from flask_smorest import abort, Blueprint
from flask.views import MethodView
from schema import JiraSchema
from sqlalchemy.exc import SQLAlchemyError
from requests.auth import HTTPBasicAuth
import requests
from dotenv import load_dotenv

from db import db
from models import JiraModel

import spacy

blp = Blueprint("jira", __name__, description = "Operations related to jira")

@blp.route("/jira")
class JiraResponse(MethodView):
  @blp.response(200,JiraSchema(many=True))
  def get(self):
    return JiraModel.query.all()


  @blp.arguments(JiraSchema)
  @blp.response(201,JiraSchema)
  def post(self,jira_data):
    jira = JiraModel(**jira_data)

    try:
      db.session.add(jira)
      db.session.commit()
    except SQLAlchemyError:
      abort(500,message="Error occured while inserting the item")

    return jira


@blp.route("/jira-check-similarity/<string:id>")
class CheckSimilarity(MethodView):
  def get(self,id):
    issue_id = id
    initial_url = "https://utkarshchauhanutc26.atlassian.net/rest/api/3/issue/"
    data_url = f"{initial_url}{issue_id}"
    API_KEY = ""
    EMAIL = ""
    load_dotenv()
    auth = HTTPBasicAuth(EMAIL, API_KEY)

    headers = {
      "Accept": "application/json"
    }

    response = requests.request(
      "GET",
      data_url,
      headers=headers,
      auth=auth
    )
    des = response.json()["fields"]["description"]["content"][0]["content"][0]["text"]
    results = []
    nlp = spacy.load("en_core_web_lg")

    user_des = nlp(str(des))

    for i in JiraModel.query.all():
      currentJira = i
      db_des = nlp(currentJira.summary)
      similarity = user_des.similarity(db_des)
      results.append({"jira id":currentJira.issue_id,"similarity":similarity})

    return results




@blp.route("/jira/<string:id>")
class DeleteJira(MethodView):
  def delete(self,id):
    jira = JiraModel.query.get_or_404(id)
    db.session.delete(jira)
    db.session.commit()
    return {"message": "Jira deleted"}, 200

