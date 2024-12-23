from marshmallow import Schema,fields

class JiraSchema(Schema):
  id = fields.Int(required=True)
  project_id = fields.Int(required=True)
  issue_key = fields.Str(required=True)
  issue_id = fields.Int(required=True)
  issue_type = fields.Str(required=True)
  summary = fields.Str(required=True)
  description = fields.Str(required=True)
  priority = fields.Str(required=True)
  status = fields.Str(required=True)
  resolution = fields.Str(required=True)