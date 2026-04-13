"""normalize status enum values to lowercase

Revision ID: 002_normalize_status_enum_values
Revises: add_feature_permissions
Create Date: 2026-04-13 18:20:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '002_normalize_status_enum_values'
down_revision = 'add_feature_permissions'
branch_labels = None
depends_on = None


def _normalize_enum_column(table_name: str, column_name: str, values: list[str], comment: str) -> None:
    value_sql = ", ".join(f"'{value}'" for value in values)
    uppercase_pairs = [(value.upper(), value) for value in values]

    # 先改成 VARCHAR，消除旧枚举集合对大小写变更的限制
    op.execute(
        f"ALTER TABLE {table_name} "
        f"MODIFY COLUMN {column_name} VARCHAR(20) NOT NULL COMMENT '{comment}'"
    )

    # 兼容旧库里落成大写枚举名的数据
    for old_value, new_value in uppercase_pairs:
        op.execute(
            f"UPDATE {table_name} "
            f"SET {column_name} = '{new_value}' "
            f"WHERE {column_name} = '{old_value}'"
        )

    # 最终统一收敛回小写枚举值
    op.execute(
        f"ALTER TABLE {table_name} "
        f"MODIFY COLUMN {column_name} ENUM({value_sql}) NOT NULL COMMENT '{comment}'"
    )


def upgrade() -> None:
    _normalize_enum_column('apps', 'status', ['normal', 'disabled'], '应用状态: normal-正常, disabled-禁用')
    _normalize_enum_column('users', 'status', ['normal', 'banned'], '用户状态: normal-正常, banned-封禁')
    _normalize_enum_column('users', 'role', ['user', 'admin'], '用户角色: user-普通用户, admin-管理员')
    _normalize_enum_column('cards', 'status', ['unused', 'used', 'disabled'], '卡密状态: unused-未使用, used-已使用, disabled-禁用')
    _normalize_enum_column('user_cards', 'status', ['active', 'unbind'], '绑定状态: active-激活, unbind-解绑')
    _normalize_enum_column('card_devices', 'status', ['active', 'disabled'], '设备状态: active-激活, disabled-禁用')


def _restore_uppercase_enum_column(table_name: str, column_name: str, values: list[str], comment: str) -> None:
    uppercase_values = [value.upper() for value in values]
    value_sql = ", ".join(f"'{value}'" for value in uppercase_values)

    op.execute(
        f"ALTER TABLE {table_name} "
        f"MODIFY COLUMN {column_name} VARCHAR(20) NOT NULL COMMENT '{comment}'"
    )

    for value in values:
        op.execute(
            f"UPDATE {table_name} "
            f"SET {column_name} = '{value.upper()}' "
            f"WHERE {column_name} = '{value}'"
        )

    op.execute(
        f"ALTER TABLE {table_name} "
        f"MODIFY COLUMN {column_name} ENUM({value_sql}) NOT NULL COMMENT '{comment}'"
    )


def downgrade() -> None:
    _restore_uppercase_enum_column('card_devices', 'status', ['active', 'disabled'], '设备状态: active-激活, disabled-禁用')
    _restore_uppercase_enum_column('user_cards', 'status', ['active', 'unbind'], '绑定状态: active-激活, unbind-解绑')
    _restore_uppercase_enum_column('cards', 'status', ['unused', 'used', 'disabled'], '卡密状态: unused-未使用, used-已使用, disabled-禁用')
    _restore_uppercase_enum_column('users', 'role', ['user', 'admin'], '用户角色: user-普通用户, admin-管理员')
    _restore_uppercase_enum_column('users', 'status', ['normal', 'banned'], '用户状态: normal-正常, banned-封禁')
    _restore_uppercase_enum_column('apps', 'status', ['normal', 'disabled'], '应用状态: normal-正常, disabled-禁用')
