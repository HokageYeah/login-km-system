"""fix feature_permissions id autoincrement

Revision ID: 003_fix_fp_id_ai
Revises: 002_normalize_status_enum_values
Create Date: 2026-04-13 19:30:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '003_fix_fp_id_ai'
down_revision = '002_normalize_status_enum_values'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    修复 feature_permissions.id 不是自增列的问题。

    根因说明：
    - 历史迁移 add_feature_permissions_table 把主键错误建成了 autoincrement=False；
    - 在 MySQL 中这会导致插入时必须手动提供 id；
    - 结果不仅导入功能权限会失败，页面手动创建权限也会失败。

    这里采用表结构级修复，而不是在服务层人工分配 id，
    因为主键生成策略应由数据库统一负责，才能保证通用性与并发安全。
    """
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'mysql':
        op.execute(
            """
            ALTER TABLE feature_permissions
            MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT COMMENT '功能权限ID'
            """
        )


def downgrade() -> None:
    """
    回滚为历史错误结构仅用于保持迁移链完整。

    正常业务不应执行该回滚，因为它会重新引入新增权限失败的问题。
    """
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'mysql':
        op.execute(
            """
            ALTER TABLE feature_permissions
            MODIFY COLUMN id INT NOT NULL COMMENT '功能权限ID'
            """
        )
