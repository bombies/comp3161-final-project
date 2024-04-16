from marshmallow import ValidationError, fields


class UnionField(fields.Field):
    """Field that deserializes multi-type input data to app-level objects."""

    def __init__(self, types: list = [], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if types:
            self.types = types
        else:
            raise AttributeError("No types provided on union field")

    def _deserialize(self, value, attr, data, **kwargs):
        if bool([isinstance(value, i) for i in self.types if isinstance(value, i)]):
            return value
        else:
            raise ValidationError(
                f'Field shoud be any of the following types: [{", ".join([str(i) for i in self.types])}]'
            )
