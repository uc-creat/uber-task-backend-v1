from flask_smorest import abort, Blueprint
from flask.views import MethodView
from schema import JiraSchema
from sqlalchemy.exc import SQLAlchemyError
from requests.auth import HTTPBasicAuth
import requests
from dotenv import load_dotenv
import os

from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model for text embeddings

from db import db
from models import JiraModel


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


@blp.route("/jira/<string:id>")
class DeleteJira(MethodView):
  def delete(self,id):
    jira = JiraModel.query.get_or_404(id)
    db.session.delete(jira)
    db.session.commit()
    return {"message": "Jira deleted"}, 200


@blp.route('/jira/similarity/<string:id>')
class SimilarityMethod(MethodView):
  def get(self,id):
    load_dotenv()
    id = id
    initial_url = os.getenv("INITIAL_URL")
    data_url = f"{initial_url}{id}"

    auth = HTTPBasicAuth(os.getenv("EMAIL"), os.getenv("API_KEY"))

    headers = {
      "Accept": "application/json"
    }

    response = requests.request(
      "GET",
      data_url,
      headers=headers,
      auth=auth
    )
    project_id = response.json()['fields']["customfield_10037"]
    issue_key = response.json()['fields']["customfield_10038"]
    issue_id = response.json()['fields']["customfield_10039"]
    issue_type = response.json()['fields']["customfield_10040"]
    summary = response.json()["fields"]["description"]["content"][0]["content"][0]["text"]
    priority = response.json()['fields']["customfield_10042"]
    status = response.json()['fields']["customfield_10041"]
    resolution = response.json()['fields']["customfield_10043"]
    des = response.json()["fields"]["description"]["content"][0]["content"][0]["text"]

    data = {
      "project_id":project_id,
      "issue_key":issue_key,
      "issue_id":issue_id,
      "issue_type":issue_type,
      "summary":summary,
      "priority":priority,
      "status":status,
      "resolution":resolution,
      "description":summary
    }

    results = []
    text2 = des
    for i in JiraModel.query.all():
      currentJira = i
      text1 = currentJira.summary
      embeddings = model.encode([text1, text2], convert_to_tensor=True)
      similarity = util.cos_sim(embeddings[0], embeddings[1])
      if round(similarity.item()*100,2)>65:
        results.append({"Issue Key":currentJira.issue_key,"Similarity score":str(round(similarity.item()*100,2))+"%"})
    return ({"results":results,"data":data})





