# Form 模块

这个模块用于校验前端提交的数据

# 简单使用

```python
from utils import form


class Book(form.BaseForm):
    author = form.CharField(min_length=4, max_length=10)
    pages = form.IntegerField(min_value=100)


class Address(form.BaseForm):
    title = form.CharField(min_length=1, max_length=128)
    book = form.FormField(form_class=Book)


class User(form.BaseForm):
    choices = [
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
    ]
    name = form.CharField(max_length=10, min_length=3)
    age = form.IntegerField(min_value=1, max_value=150)
    is_monitor = form.BooleanField()
    score = form.FloatField()
    amount = form.DecimalField(max_digits=11, decimal_places=2)
    start = form.DateTimeField()
    born = form.DateField()
    end = form.FormatDateTimeField()
    dead = form.FormatDateField()
    favor = form.ChoiceField(choices=choices)
    likes = form.MultiChoiceField(choices=choices)
    books = form.ListField(item_field=form.FormField(form_class=Book))
    address = form.FormField(form_class=Address)

    def validate_name(self, value):
        if 'python' not in value:
            raise form.ValidationError('必须包含 python')


class User2(User):
    in_user = form.FormField(form_class=User)


data = {
    "name": "你好啊 python",
    "age": 1,
    "is_monitor": "NO",
    "score": "123.12313",
    "amount": "123456.01",
    "start": "2019-10-10 23:59:59",
    "born": "2019-10-31",
    "end": "2019-10-10 2:2:2",
    "dead": "2019-10-1",
    "favor": "a",
    "likes": ["x", "m"],
    "address": {
        "title": "长城",
        "book": {
            "author": "dddd",
            "pages": 1000.01
        }
    },
    "books": [
        {
            "author": "张三aa",
            "pages": 100
        },
        {
            "author": "张三aa",
            "pages": 1111
        },
    ],
    "in_user": {
        "name": "你好啊 python",
        "age": 1,
        "is_monitor": "N",
        "score": "123.12313",
        "amount": "123456.01",
        "start": "2019-10-10 2:2:2",
        "born": "2019-10-10",
        "end": "2019-10-10 2:2:2",
        "dead": "2019-10-10",
        "favor": "a",
        "likes": ["x", "m"],
        "address": {
            "title": "长城",
            "book": {
                "author": "dddd",
                "pages": 1000.01
            }
        },
        "books": [
            {
                "author": "张三dd",
                "pages": 100
            },
            {
                "author": "张三aa",
                "pages": 1111
            }
        ]
    }
}
user = User2(data)
if not user.is_valid():
    print(user.errors)
else:
    print(user.validated_data)
```

# 表单定义

## 表单类

所有的表单类继承自 `form.BaseForm` ，如下方式定义:

```python
class FormName(form.BaseForm)
    pass
```

## 字段定义

`字段名 = form.字段类型(选项)`

### 字段说明

所有字段类型继承自 `form.fields.Field`，如果字段没有给默认值的话，那么表示字段是必须上传的

### 通用字段选项

- `default` : 默认值
- `validators` : 数据校验函数列表，这里包含函数名，函数在定义时，不需要返回值，返回函数内部校验数据失败，应该**抛出 form.fields.ValidationError**
- `label` : 字段标签
- `help_text` : 帮助信息
- `error_messages` : 自定义字段错误信息，与 `default_error_messages` 格式相同

#### AnyField

通常情况下，前端提交的字段都是有固定数据类型的，特殊情况下，数据类型可能会不同，这里可以使用 `AnyField` 来接收任意数据类型。**如果使用 AnyField ，那么就需要手动来将前端提交的数据进行校验，可以通过在表单类中定义 `validate_字段名` 来进行校验以及数据类型转化**

#### BooleanField

bool 类型

以下数据将被转化 `True` : `['t', 'T', 'y', 'Y', 'yes', 'YES', 'true', 'True', 'TRUE', 'on', 'On', 'ON', '1', 1, True]`

以下数据将被转化 `False` : `['f', 'F', 'n', 'N', 'no', 'NO', 'false', 'False', 'FALSE', 'off', 'Off', 'OFF', '0', 0, 0.0, False]`
 
#### CharField

字符串类型，校验数据时会先将字符串两边的空白去除(如果`trim_whitespace=True`)，再执行后续校验。

选项:
- `blank` : 是否允许空字符串 `''`，默认 False
- `min_length` : 最小长度
- `max_length` : 最大长度
- `trim_whitespace` : 是否阶段字符串两边的空白符，默认 True

#### RegexField

继承自 `CharField`，将接受到的数据进行正则匹配，先按照 `CharField` 规则进行校验，校验成功后，再进行正则匹配

选项:
- `regex` : 正则匹配符

#### IntegerField

整数类型

选项:
- `min_value` : 最小值，合法范围 `value >= min_value`
- `max_value` : 最大值，合法范围 `value <= max_value`

#### FloatField

整数类型

选项:
- `min_value` : 最小值，合法范围 `value >= min_value`
- `max_value` : 最大值，合法范围 `value <= max_value`

#### DecimalField

整数类型

选项:
- `min_value` : 最小值，合法范围 `value >= min_value`
- `max_value` : 最大值，合法范围 `value <= max_value`
- `max_digits` : 最大数字个数
- `decimal_places` : 小数位个数

#### DateTimeField

日期时间类型

选项:
- `format_str` : 时间字符串格式，默认: `%Y-%m-%d %H:%M:%S`

#### DateField

日期时间类型

选项:
- `format_str` : 时间字符串格式，默认: `%Y-%m-%d`

#### FormatDateTimeField

日期时间字符串类型，前端提交的字符串格式，必须为 `format_str` 格式

选项:
- `format_str` : 时间字符串格式，默认: `%Y-%m-%d %H:%M:%S`

#### FormatDateField

日期时间字符串类型，前端提交的字符串格式，必须为 `format_str` 格式

选项:
- `format_str` : 时间字符串格式，默认: `%Y-%m-%d`

#### ChoiceField

单选类型，只能从 `choices` 中选择一个

选项:
- `choices` : 可选值列表: `[(1, '注释1'),(2, '注释2')]`

#### MultiChoiceField

单选类型，可以从 `choices` 中选择多个，校验时只会保留在 choices 中的值

选项:
- `choices` : 可选值列表: `[(1, '注释1'),(2, '注释2')]`

#### DictField

字典类型，这里只是校验数据是不是字典类型

#### FormField

嵌套表单类型 

当前端提交的数据是复杂结构时，比如包含了字典，如果想要对该字典中的数据进行校验，通过 `DictField` 无法实现，必须要使用 `FormField` 。`FormField` 会绑定到一个表单类上，通过该表单类对字典数据进行校验

选项:
- `form_class` : 指定表单类

#### ListField

数组类型，定义方式: `ListField(item_field=字段类型(选项))` ，

例如: `addresses = ListField(item_field=FormField(form_class=Address))`

选项:
- `item_field` : 数据中元素的类型
- `max_length` : 最大元素个数
- `min_length` : 最少元素个数
