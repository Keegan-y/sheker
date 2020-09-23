import asyncio

from starapp.utils.form.fields import Field, ValidationError, EMPTY


class FormMeta(type):
    @classmethod
    def _get_fields(cls, bases, attrs):
        required_fields = dict()
        fields = dict()
        for key, value in attrs.items():
            if isinstance(value, Field):
                if value.name is None:
                    value.name = key
                fields[key] = value
                if value.required:
                    required_fields[key] = value
        for key in fields:
            del attrs[key]
        # find parent fields
        for base in reversed(bases):
            for field_name, field in getattr(base, '_fields', {}).items():
                fields[field_name] = field
            for field_name, field in getattr(base, '_required_fields', {}).items():
                required_fields[field_name] = field

        return fields, required_fields

    def __new__(meta, name, bases, attrs):
        attrs['_fields'], attrs['_required_fields'] = meta._get_fields(
            bases, attrs)
        cls = super(FormMeta, meta).__new__(meta, name, bases, attrs)
        return cls


class BaseForm(metaclass=FormMeta):
    def __init__(self, obj=None, data={}, *args, **kwargs):
        self.data = data
        self.obj = obj

    async def is_valid(self, raise_exception=False):
        try:
            validated_data = dict()
            for field_name, field in self._fields.items():
                data_field_name = field.name
                # 先使用字段进行数据校验
                value = await field.run_validation(
                    self.data.get(data_field_name))
                if value == EMPTY:
                    continue
                # 使用类中定义个f'validate_{field_name}'进行数据校验
                inner_validator_name = f'validate_{field_name}'
                if hasattr(self, inner_validator_name):
                    func = getattr(self, inner_validator_name)
                    if asyncio.iscoroutinefunction(func):
                        value = await func(value)
                    else:
                        value = func(value)
                validated_data[field_name] = value
            if hasattr(self, 'validate'):
                data_field_name = 'errors'
                func = getattr(self, 'validate')
                if asyncio.iscoroutinefunction(func):
                    validated_data = await func(validated_data)
                else:
                    validated_data = func(validated_data)
            self.validated_data = validated_data
            return True
        except ValidationError as e:
            if raise_exception:
                raise ValidationError(e.detail, data_field_name)
            else:
                self.errors = {data_field_name: e.detail}
                return False

    async def create(self, validated_data):
        pass

    async def update(self, validated_data):
        pass

    async def save(self):
        if self.obj:
            return await self.update(self.validated_data)
        else:
            return await self.update(self.validated_data)
