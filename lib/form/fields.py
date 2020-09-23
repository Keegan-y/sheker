import re
import six
import datetime
import decimal
import asyncio

EMPTY = object()


class ValidationError(Exception):
    def __init__(self, detail, key=None):
        self.detail = detail
        self.key = key


class Field(object):
    default_error_messages = {
        'required': 'This field is required.',
    }
    default_validators = []

    def __init__(self, default=EMPTY, required=True,
                 error_messages={}, validators=[], name=None,
                 label='', help_text='', **kwargs):
        """name是带校验数据中的字段名,默认和当前字段同名
        """
        self.required = required
        self.default = default
        self.label = label
        self.help_text = help_text
        self.name = name

        self.validators = validators[:]

        messages = {}
        for cls in reversed(self.__class__.__mro__):
            messages.update(getattr(cls, 'default_error_messages', {}))
        messages.update(error_messages)
        self.error_messages = messages

    def get_default(self):
        if callable(self.default):
            if hasattr(self.default, 'set_context'):
                self.default.set_context(self)
            return self.default()
        return self.default

    async def run_validation(self, data=None):
        """
        如果没有字段数据,并且非比传字段,返回EMPTY
        如果没有字段数据,并且比传字段,检查默认值是否为EMPTY,是EMTPY就报错
        """
        if data is None and not self.required:
            return EMPTY
        if data is None and self.required:
            data = self.get_default()
        if data == EMPTY:
            self.fail('required')
        if asyncio.iscoroutinefunction(self.to_internal_value):
            value = await self.to_internal_value(data)
        else:
            value = self.to_internal_value(data)
        await self.run_validators(value)
        return value

    async def run_validators(self, value):
        """
        Test the given value against all the validators on the field,
        and either raise a `ValidationError` or simply return.
        """
        for validator in self.validators:
            if hasattr(validator, 'set_context'):
                validator.set_context(self)
            if asyncio.iscoroutinefunction(validator):
                value = await validator(value)
            else:
                value = validator(value)

    def to_internal_value(self, data):
        """
        将外部数据转化为python内置类型
        """
        raise NotImplementedError

    def to_representation(self, value):
        """
        将python内置类型转化为外部数据
        """
        return value

    def fail(self, key, **kwargs):
        """
        抛出错误消息
        @param str key: 错误消息的key
        @param dict kwargs: 用于格式化错误消息的参数
        """
        msg = self.error_messages[key]
        message_string = msg.format(**kwargs)
        raise ValidationError(message_string)


class AnyField(Field):
    """
    can accept any data type,
    you should set validators or validator_func on form class
    """

    def __init__(self, default=None, error_messages={}, validators=[], label='', help_text='', **kwargs):
        super(AnyField, self).__init__(default=default, error_messages=error_messages,
                                       validators=validators, label=label, help_text=help_text, **kwargs)
        self.required = False

    def to_internal_value(self, data):
        return data


class BooleanField(Field):
    default_error_messages = {
        'invalid': 'Must be a valid boolean.'
    }
    TRUE_VALUES = {
        't', 'T',
        'y', 'Y', 'yes', 'YES',
        'true', 'True', 'TRUE',
        'on', 'On', 'ON',
        '1', 1,
        True
    }
    FALSE_VALUES = {
        'f', 'F',
        'n', 'N', 'no', 'NO',
        'false', 'False', 'FALSE',
        'off', 'Off', 'OFF',
        '0', 0, 0.0,
        False
    }
    NULL_VALUES = {'null', 'Null', 'NULL', '', None}

    def to_internal_value(self, data):
        try:
            if data in self.TRUE_VALUES:
                return True
            elif data in self.FALSE_VALUES:
                return False
        except TypeError:  # Input is an unhashable type
            pass
        self.fail('invalid')

    def to_representation(self, value):
        if value in self.TRUE_VALUES:
            return True
        elif value in self.FALSE_VALUES:
            return False
        if value in self.NULL_VALUES and self.allow_null:
            return None
        return bool(value)


class CharField(Field):
    default_error_messages = {
        'invalid': 'Not a valid string.',
        'blank': 'This field may not be blank.',
        'max_length': 'Ensure this field has no more than {max_length} characters.',
        'min_length': 'Ensure this field has at least {min_length} characters.',
    }

    def __init__(self, max_length=None, min_length=None,
                 allow_blank=False, trim_whitespace=True,
                 **kwargs):
        self.allow_blank = allow_blank
        self.trim_whitespace = trim_whitespace
        self.max_length = max_length
        self.min_length = min_length
        super(CharField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        data = str(data)
        if self.trim_whitespace:
            data = data.strip()
        data_length = len(data)
        if data_length == 0 and not self.allow_blank:
            self.fail('blank')
        if self.max_length and data_length > self.max_length:
            self.fail('max_length', max_length=self.max_length)
        if self.min_length and data_length < self.min_length:
            self.fail('min_length', min_length=self.min_length)
        return data


class RegexField(CharField):
    default_error_messages = {
        'invalid': 'This value does not match the required pattern: {pattern}.'
    }

    def __init__(self, regex, **kwargs):
        self.regex = regex
        super(RegexField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        data = super(RegexField, self).to_internal_value(data)
        regex_matches = re.compile(self.regex).search(data)
        if not regex_matches:
            self.fail('invalid', pattern=self.regex)
        return data


class IntegerField(Field):
    default_error_messages = {
        'invalid': 'A valid integer is required.',
        'max_value': 'Ensure this value is less than or equal to {max_value}.',
        'min_value': 'Ensure this value is greater than or equal to {min_value}.',
        'max_string_length': 'String value too large.'
    }
    MAX_STRING_LENGTH = 1000

    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        super(IntegerField, self).__init__(**kwargs)

    def to_internal_value(self, data):

        if isinstance(data, six.text_type) and len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')
        try:
            data = int(float(data))  # 数字字符串不能直接转为int类型
        except (ValueError, TypeError):
            self.fail('invalid')
        if self.max_value and data > self.max_value:
            self.fail('max_value', max_value=self.max_value)
        if self.min_value and data < self.min_value:
            self.fail('min_value', min_value=self.min_value)
        return data


class FloatField(Field):
    default_error_messages = {
        'invalid': 'A valid number is required.',
        'max_value': 'Ensure this value is less than or equal to {max_value}.',
        'min_value': 'Ensure this value is greater than or equal to {min_value}.',
        'max_string_length': 'String value too large.'
    }
    MAX_STRING_LENGTH = 1000  #

    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        super(FloatField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if isinstance(data, six.text_type) and len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')
        try:
            data = float(data)
        except (TypeError, ValueError):
            self.fail('invalid')
        if self.max_value and data > self.max_value:
            self.fail('max_value', max_value=self.max_value)
        if self.min_value and data < self.min_value:
            self.fail('min_value', min_value=self.min_value)
        return data


class DecimalField(Field):
    """
    mongo 3.4 才有 Decimal 数据类型
    """
    default_error_messages = {
        'invalid': 'A valid number is required.',
        'max_value': 'Ensure this value is less than or equal to {max_value}.',
        'min_value': 'Ensure this value is greater than or equal to {min_value}.',
        'max_digits': 'Ensure that there are no more than {max_digits} digits in total.',
        'max_decimal_places': 'Ensure that there are no more than {max_decimal_places} decimal places.',
        'max_whole_digits': 'Ensure that there are no more than {max_whole_digits} digits before the decimal point.',
        'max_string_length': 'String value too large.'
    }
    MAX_STRING_LENGTH = 1000  # Guard against malicious string inputs.

    def __init__(self, max_digits, decimal_places, max_value=None, min_value=None, **kwargs):
        self.max_digits = max_digits
        self.decimal_places = decimal_places

        self.max_value = max_value
        self.min_value = min_value

        if self.max_digits is not None and self.decimal_places is not None:
            self.max_whole_digits = self.max_digits - self.decimal_places
        else:
            self.max_whole_digits = None

        super(DecimalField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        data = str(data).strip()

        if len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')

        try:
            value = decimal.Decimal(data)
        except decimal.DecimalException:
            self.fail('invalid')

        if value != value:
            self.fail('invalid')

        if value in (decimal.Decimal('Inf'), decimal.Decimal('-Inf')):
            self.fail('invalid')

        value = self.validate_precision(value)
        if self.min_value and value < self.min_value:
            self.fail('min_value', min_value=self.min_value)
        if self.max_value and value > self.max_value:
            self.fail('max_value', max_value=self.max_value)
        return value

    def validate_precision(self, value):
        sign, digittuple, exponent = value.as_tuple()

        if exponent >= 0:
            # 1234500.0
            total_digits = len(digittuple) + exponent
            whole_digits = total_digits
            decimal_places = 0
        elif len(digittuple) > abs(exponent):
            # 123.45
            total_digits = len(digittuple)
            whole_digits = total_digits - abs(exponent)
            decimal_places = abs(exponent)
        else:
            # 0.001234
            total_digits = abs(exponent)
            whole_digits = 0
            decimal_places = total_digits

        if self.max_digits is not None and total_digits > self.max_digits:
            self.fail('max_digits', max_digits=self.max_digits)
        if self.decimal_places is not None and decimal_places > self.decimal_places:
            self.fail('max_decimal_places',
                      max_decimal_places=self.decimal_places)
        if self.max_whole_digits is not None and whole_digits > self.max_whole_digits:
            self.fail('max_whole_digits',
                      max_whole_digits=self.max_whole_digits)

        return value

    def to_representation(self, value):
        return str(value)


class DateTimeField(Field):
    default_error_messages = {
        'invalid': 'Datetime has wrong format. Use this format instead: {format}.',
        'date': 'Expected a datetime but got a date.',
    }
    datetime_parser = datetime.datetime.strptime
    datetime_formater = datetime.datetime.strftime

    def __init__(self, format_str="%Y-%m-%d %H:%M:%S",  **kwargs):
        self.format_str = format_str
        super(DateTimeField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if isinstance(data, datetime.datetime):
            return data
        if isinstance(data, datetime.date):
            self.fail('date')
        try:
            data = self.datetime_parser(data, self.format_str)
        except Exception:
            self.fail('invalid', format=self.format_str)
        return data

    def to_representation(self, data):
        return self.datetime_formater(data, self.format_str)


class DateField(DateTimeField):
    default_error_messages = {
        'invalid': 'Date has wrong format. Use one of these formats instead: {format}.',
        'datetime': 'Expected a date but got a datetime.',
    }

    def __init__(self, format_str="%Y-%m-%d",  **kwargs):
        super(DateField, self).__init__(format_str=format_str, **kwargs)

    def to_internal_value(self, data):
        if isinstance(data, datetime.datetime):
            self.fail('datetime')
        if isinstance(data, datetime.date):
            return data
        try:
            data = self.datetime_parser(data, self.format_str).date()
        except Exception:
            self.fail('invalid', format=self.format_str)
        return data


class FormatDateTimeField(Field):
    default_error_messages = {
        'invalid': 'value has wrong format. Use the format instead: {format}.',
    }
    datetime_formater = datetime.datetime.strftime
    datetime_parser = datetime.datetime.strptime

    def __init__(self, format_str="%Y-%m-%d %H:%M:%S", **kwargs):
        self.format_str = format_str
        super(FormatDateTimeField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if isinstance(data, (datetime.datetime, datetime.date)):
            return self.datetime_formater(data, self.format_str)
        data = str(data)
        try:
            self.datetime_parser(data, self.format_str)
        except Exception:
            self.fail('invalid', format=self.format_str)
        return data


class FormatDateField(FormatDateTimeField):

    def __init__(self, format_str="%Y-%m-%d", **kwargs):
        self.format_str = format_str
        super(FormatDateTimeField, self).__init__(**kwargs)


class ChoiceField(Field):
    default_error_messages = {
        'invalid': '{value} not in [{choices}]',
    }
    # choices = [(1, '注释')]

    def __init__(self, choices, **kwargs):
        self.choices = choices
        super(ChoiceField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        for choice in self.choices:
            if data == choice[0]:
                return data
        self.fail('invalid', value=data, choices=','.join(
            [str(choice[0]) for choice in self.choices]))


class MultiChoiceField(Field):
    default_error_messages = {
        'invalid': '{value} not in [{choices}]',
        'not_a_list': 'Expected a list of items but got type "{input_type}".',
    }
    # choices = [(1, '注释')]

    def __init__(self, choices, **kwargs):
        self.choices = choices
        super(MultiChoiceField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if isinstance(data, type('')) or not hasattr(data, '__iter__'):
            self.fail('not_a_list', input_type=type(data).__name__)

        result = []
        for choice in self.choices:
            for item in data:
                if item == choice[0]:
                    result.append(item)
        if result == []:
            self.fail('invalid', value=','.join([str(i) for i in data]),
                      choices=','.join([str(choice[0]) for choice in self.choices]))
        return result


class ListField(Field):
    default_error_messages = {
        'not_a_list': 'Expected a list of items but got type "{input_type}".',
        'min_length': 'Ensure this field has at least {min_length} elements.',
        'max_length': 'Ensure this field has no more than {max_length} elements.'
    }

    def __init__(self, item_field, max_length=None, min_length=None, **kwargs):
        self.item_field = item_field
        self.max_length = max_length
        self.min_length = min_length
        super(ListField, self).__init__(**kwargs)

    async def to_internal_value(self, data):
        if not isinstance(data, list):
            self.fail('not_a_list', input_type=type(data).__name__)
        if isinstance(self.item_field, FormField):
            result = []
            for index, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValidationError(
                        {index: f'Expected a dict but got type {type(item).__name__}'})
                item_obj = self.item_field.form_class(item)
                if await item_obj.is_valid():
                    result.append(item_obj.validated_data)
                else:
                    raise ValidationError({index: item_obj.errors})
        elif isinstance(self.item_field, Field):
            result = []
            for index, item in enumerate(data):
                try:
                    value = await self.item_field.run_validation(item)
                    if value == EMPTY:
                        continue
                    result.append(value)
                except ValidationError as e:
                    raise ValidationError({index: e.detail})
        else:
            result = data
        data_length = len(result)
        if self.required and data_length == 0:
            self.fail('required')
        if self.max_length and data_length > self.max_length:
            self.fail('max_length', max_length=self.max_length)
        if self.min_length and data_length < self.min_length:
            self.fail('min_length', min_length=self.min_length)
        return result


class DictField(Field):
    default_error_messages = {
        'not_a_dict': 'Expected a dict but got type "{input_type}".',
    }

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            self.fail('not_a_dict', input_type=type(data).__name__)
        return data


class FormField(Field):
    default_error_messages = {
        'not_a_dict': 'Expected a dict but got type "{input_type}".',
    }

    def __init__(self, form_class, **kwargs):
        self.form_class = form_class
        super(FormField, self).__init__(**kwargs)

    async def to_internal_value(self, data):
        if not isinstance(data, dict):
            self.fail('not_a_dict', input_type=type(data).__name__)
        obj = self.form_class(data)
        is_valid = await obj.is_valid()
        if not is_valid:
            raise ValidationError(obj.errors)
        return obj.validated_data
