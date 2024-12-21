from db import db

class JiraModel(db.Model):
  __tablename__ = 'jira'
  id = db.Column(db.Integer, primary_key=True)
  project_id = db.Column(db.Integer, unique = True, nullable=False)
  issue_key = db.Column(db.String(80), unique = True, nullable=False)
  issue_id = db.Column(db.Integer, unique = True, nullable=False)
  issue_type = db.Column(db.String(80), nullable=False)
  summary = db.Column(db.String(500),nullable=False)
  description = db.Column(db.String(500))
  priority = db.Column(db.String(10))
  status = db.Column(db.String(20))
  resolution = db.Column(db.String(20))
