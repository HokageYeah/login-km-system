"""add feature_permissions table

Revision ID: add_feature_permissions
Revises:
Create Date: 2026-01-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_feature_permissions'
# 该迁移是在核心授权表结构创建完成后追加的权限元数据扩展，
# 必须挂在主迁移链 001 之后，避免形成多个 head 导致部署时 upgrade head 失败。
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # 创建 feature_permissions 表
    op.create_table(
        'feature_permissions',
        # 功能权限主键必须是数据库自增列，否则新增权限与导入权限都会因为缺少默认值而失败。
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='功能权限ID'),
        sa.Column('permission_key', sa.String(length=100), nullable=False, comment='权限标识（如：wechat, ximalaya）'),
        sa.Column('permission_name', sa.String(length=100), nullable=False, comment='权限名称（如：微信抓取、喜马拉雅播放）'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='权限描述'),
        sa.Column('category', sa.String(length=50), nullable=True, comment='权限分类（如：数据抓取、媒体播放）'),
        sa.Column('icon', sa.String(length=100), nullable=True, comment='图标'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序，数字越小越靠前'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='normal', comment='状态：normal-正常，disabled-禁用'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='功能权限表：用于配置系统中所有可用的功能权限'
    )
    op.create_index('ix_feature_permissions_permission_key', 'feature_permissions', ['permission_key'], unique=True)
    op.create_index('ix_feature_permissions_id', 'feature_permissions', ['id'], unique=False)


def downgrade():
    # 删除 feature_permissions 表
    op.drop_index('ix_feature_permissions_permission_key', table_name='feature_permissions')
    op.drop_index('ix_feature_permissions_id', table_name='feature_permissions')
    op.drop_table('feature_permissions')
