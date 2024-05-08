from marshmallow import Schema, fields


class CalendarEventSchema(Schema):
    course_id = fields.String(required=True)
    date = fields.DateTime(required=True)
    event_name = fields.String(required=True)


class DateRangeSchema(Schema):
    start_date = fields.DateTime(required=False, allow_none=True)
    end_date = fields.DateTime(required=False, allow_none=True)
