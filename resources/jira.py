from flask_smorest import abort, Blueprint
from flask.views import MethodView
from schema import JiraSchema
from sqlalchemy.exc import SQLAlchemyError

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


@blp.route("/jira-check-similarity")
class CheckSimilarity(MethodView):
  @blp.arguments(JiraSchema)
  def get(self,jira_data):
    jira = JiraModel(**jira_data)
    results = []
    nlp = spacy.load("en_core_web_lg")

    user_des = nlp(str(jira.summary))

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







