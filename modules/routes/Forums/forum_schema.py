from marshmallow import Schema, fields

class ForumSchema(Schema):
    topic = fields.Str(required=True)
    course_code = fields.Str(required=True)

class DiscussionThreadSchema(Schema):
    replies = fields.Int(required=True)
    timestamp = fields.DateTime(required=True)
    forum_id = fields.Int(required=True)

class DiscussionReplySchema(Schema):
    thread_id = fields.Int(required=True)
    reply_text = fields.Str(required=True)

class NewDiscussionThreadSchema(Schema):
    title = fields.Str(required=True)
    post = fields.Str(required=True)

class NewDiscussionReplySchema(Schema):
    thread_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    reply_text = fields.Str(required=True)
