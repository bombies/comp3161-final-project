from marshmallow import Schema, fields

class CalendarEventSchema(Schema):
    course_id = fields.String(required=True)
    date = fields.Date(required=True)
    event_name = fields.String(required=True)
    event_no = fields.Int(required=True)
