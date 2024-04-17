from marshmallow import Schema, fields

class ForumSchema(Schema):
    forum_id = fields.Int(dump_only=True)
    topic = fields.Str(required=True)
    post_time = fields.DateTime(required=True)
    creator = fields.Int(required=True)
    course_code = fields.Str(required=True)

class DiscussionThreadSchema(Schema):
    thread_id = fields.Int(dump_only=True)
    replies = fields.Int(required=True)
    timestamp = fields.DateTime(required=True)
    forum_id = fields.Int(required=True)

class DiscussionReplySchema(Schema):
    reply_id = fields.Int(dump_only=True)
    thread_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    reply_time = fields.DateTime(required=True)
    reply_text = fields.Str(required=True)

class NewDiscussionThreadSchema(Schema):
    title = fields.Str(required=True)
    post = fields.Str(required=True)

class NewDiscussionReplySchema(Schema):
    thread_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    reply_text = fields.Str(required=True)
