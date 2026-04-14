"""bind feature_permissions to apps

Revision ID: 004_bind_fp_to_apps
Revises: 003_fix_fp_id_ai
Create Date: 2026-04-14 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_bind_fp_to_apps'
down_revision = '003_fix_fp_id_ai'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    给功能权限补充所属应用外键。

    设计说明：
    - 权限现在需要按应用维度管理，因此 app_id 应成为正式结构；
    - 这里先允许历史数据为空，不强行猜测旧权限属于哪个应用，避免错误回填；
    - 新增权限由业务层强制要求选择应用，旧数据则可在后台逐步补齐归属。
    """
    with op.batch_alter_table('feature_permissions') as batch_op:
        batch_op.add_column(sa.Column('app_id', sa.Integer(), nullable=True, comment='所属应用ID'))
        batch_op.create_index('ix_feature_permissions_app_id', ['app_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_feature_permissions_app_id_apps',
            'apps',
            ['app_id'],
            ['id']
        )


def downgrade() -> None:
    """回滚功能权限与应用的绑定关系。"""
    with op.batch_alter_table('feature_permissions') as batch_op:
        batch_op.drop_constraint('fk_feature_permissions_app_id_apps', type_='foreignkey')
        batch_op.drop_index('ix_feature_permissions_app_id')
        batch_op.drop_column('app_id')
