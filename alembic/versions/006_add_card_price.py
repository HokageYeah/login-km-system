"""add card price

Revision ID: 006_add_card_price
Revises: 005_add_fp_price
Create Date: 2026-04-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_add_card_price'
down_revision = '005_add_fp_price'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    给卡密补充最终售卖价格。

    权限价格只是生成时的定价依据，卡密生成后需要保存当次最终成交价；
    这样后续权限价格调整不会篡改历史已生成卡密的价格。
    """
    with op.batch_alter_table('cards') as batch_op:
        batch_op.add_column(
            sa.Column(
                'price',
                sa.Numeric(10, 2),
                nullable=False,
                server_default='0.00',
                comment='卡密售卖价格'
            )
        )


def downgrade() -> None:
    """回滚卡密售卖价格字段。"""
    with op.batch_alter_table('cards') as batch_op:
        batch_op.drop_column('price')
