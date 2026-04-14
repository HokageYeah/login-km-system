from enum import Enum

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator


class NormalizedEnumType(TypeDecorator):
    """
    兼容历史大小写差异的枚举类型。

    项目早期库里部分状态字段落的是大写枚举名（如 NORMAL），
    后续迁移又改成了小写业务值（如 normal）。如果 ORM 只按某一种格式解析，
    就会在读取旧数据或新数据时随机报错。

    这里统一做两件事：
    1. 读取时兼容大小写，最终都还原成 Python Enum
    2. 写入时统一落为业务 value（小写），方便后续数据库逐步收敛
    """

    impl = String
    cache_ok = True

    def __init__(self, enum_cls: type[Enum], length: int | None = None):
        self.enum_cls = enum_cls
        max_length = length or max(len(item.value) for item in enum_cls)
        super().__init__(length=max_length)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, self.enum_cls):
            return value.value

        if isinstance(value, str):
            normalized = value.strip()
            try:
                return self.enum_cls(normalized.lower()).value
            except ValueError:
                try:
                    return self.enum_cls[normalized.upper()].value
                except KeyError as exc:
                    raise ValueError(f"无效的枚举值: {value}") from exc

        raise ValueError(f"不支持的枚举类型: {type(value)}")

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, self.enum_cls):
            return value

        normalized = str(value).strip()

        try:
            return self.enum_cls(normalized.lower())
        except ValueError:
            try:
                return self.enum_cls[normalized.upper()]
            except KeyError as exc:
                raise LookupError(
                    f"数据库中的枚举值 {value} 无法映射到 {self.enum_cls.__name__}"
                ) from exc


def build_value_enum(enum_cls: type[Enum], enum_name: str) -> NormalizedEnumType:
    return NormalizedEnumType(enum_cls)
