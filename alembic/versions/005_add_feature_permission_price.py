"""add feature permission price

Revision ID: 005_add_fp_price
Revises: 004_bind_fp_to_apps
Create Date: 2026-04-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_fp_price'
down_revision = '004_bind_fp_to_apps'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    给功能权限补充售卖价格。

    价格属于权限元数据本身，创建、编辑、导入导出都应复用同一字段，避免前端单点保存导致不同入口不一致。
    """
    with op.batch_alter_table('feature_permissions') as batch_op:
        batch_op.add_column(
            sa.Column(
                'price',
                sa.Numeric(10, 2),
                nullable=False,
                server_default='0.00',
                comment='权限售卖价格'
            )
        )


def downgrade() -> None:
    """回滚功能权限售卖价格字段。"""
    with op.batch_alter_table('feature_permissions') as batch_op:
        batch_op.drop_column('price')
