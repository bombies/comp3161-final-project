from marshmallow import Schema, fields


class CreateCourseSchema(Schema):
    course_code = fields.String(required=True)
    course_name = fields.String(required=True)
    lecturer_id = fields.Int(required=True)
    semester = fields.Int(required=True)


class UpdateCourseSchema(Schema):
    course_name = fields.String(required=False)
    lecturer_id = fields.Int(required=False)
    semester = fields.Int(required=False)


class CreateAssignmentSchema(Schema):
    course_code = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str(required=False)
    deadline = fields.DateTime(required=True)
    total_marks = fields.Float(required=True)


class GradeAssignmentSchema(Schema):
    grade = fields.Float(required=True)


class CreateCourseSectionSchema(Schema):
    section_name = fields.Str(required=True)


class CreateCourseSectionItemSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=False)
    deadline = fields.DateTime(required=False)
    link = fields.Str(required=False)
    file_location = fields.Str(required=False)
