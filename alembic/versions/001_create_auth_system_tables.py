"""创建授权系统核心表

Revision ID: 001
Revises: 
Create Date: 2026-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建应用表
    op.create_table(
        'apps',
        sa.Column('id', sa.Integer(), nullable=False, comment='应用ID'),
        sa.Column('app_key', sa.String(length=100), nullable=False, comment='应用唯一标识'),
        sa.Column('app_name', sa.String(length=100), nullable=False, comment='应用名称'),
        sa.Column('status', sa.Enum('normal', 'disabled', name='appstatus'), nullable=False, comment='应用状态: normal-正常, disabled-禁用'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index(op.f('ix_apps_id'), 'apps', ['id'], unique=False)
    op.create_index(op.f('ix_apps_app_key'), 'apps', ['app_key'], unique=True)

    # 创建用户表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('username', sa.String(length=100), nullable=False, comment='用户名'),
        sa.Column('password_hash', sa.String(length=255), nullable=False, comment='密码哈希'),
        sa.Column('status', sa.Enum('normal', 'banned', name='userstatus'), nullable=False, comment='用户状态: normal-正常, banned-封禁'),
        sa.Column('role', sa.Enum('user', 'admin', name='userrole'), nullable=False, comment='用户角色: user-普通用户, admin-管理员'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
        sa.Column('last_login_at', sa.DateTime(), nullable=True, comment='最后登录时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 创建卡密表
    op.create_table(
        'cards',
        sa.Column('id', sa.Integer(), nullable=False, comment='卡密ID'),
        sa.Column('app_id', sa.Integer(), nullable=False, comment='所属应用ID'),
        sa.Column('card_key', sa.String(length=100), nullable=False, comment='卡密字符串'),
        sa.Column('status', sa.Enum('unused', 'used', 'disabled', name='cardstatus'), nullable=False, comment='卡密状态: unused-未使用, used-已使用, disabled-禁用'),
        sa.Column('expire_time', sa.DateTime(), nullable=False, comment='过期时间'),
        sa.Column('max_device_count', sa.Integer(), nullable=False, comment='最大可绑定设备数'),
        sa.Column('permissions', sa.JSON(), nullable=True, comment='权限配置 JSON'),
        sa.Column('remark', sa.String(length=255), nullable=True, comment='备注（套餐名称等）'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True, comment='更新时间'),
        sa.ForeignKeyConstraint(['app_id'], ['apps.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index(op.f('ix_cards_id'), 'cards', ['id'], unique=False)
    op.create_index(op.f('ix_cards_app_id'), 'cards', ['app_id'], unique=False)
    op.create_index(op.f('ix_cards_card_key'), 'cards', ['card_key'], unique=True)

    # 创建用户-卡密绑定表
    op.create_table(
        'user_cards',
        sa.Column('id', sa.Integer(), nullable=False, comment='绑定ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('card_id', sa.Integer(), nullable=False, comment='卡密ID'),
        sa.Column('bind_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='绑定时间'),
        sa.Column('status', sa.Enum('active', 'unbind', name='usercardstatus'), nullable=False, comment='绑定状态: active-激活, unbind-解绑'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True, comment='更新时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index(op.f('ix_user_cards_id'), 'user_cards', ['id'], unique=False)
    op.create_index(op.f('ix_user_cards_user_id'), 'user_cards', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_cards_card_id'), 'user_cards', ['card_id'], unique=False)
    op.create_index('idx_user_card', 'user_cards', ['user_id', 'card_id'], unique=True)

    # 创建卡密-设备绑定表
    op.create_table(
        'card_devices',
        sa.Column('id', sa.Integer(), nullable=False, comment='绑定ID'),
        sa.Column('card_id', sa.Integer(), nullable=False, comment='卡密ID'),
        sa.Column('device_id', sa.String(length=255), nullable=False, comment='设备唯一标识'),
        sa.Column('device_name', sa.String(length=255), nullable=True, comment='设备名称'),
        sa.Column('bind_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='绑定时间'),
        sa.Column('last_active_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='最后活跃时间'),
        sa.Column('status', sa.Enum('active', 'disabled', name='carddevicestatus'), nullable=False, comment='设备状态: active-激活, disabled-禁用'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True, comment='更新时间'),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index(op.f('ix_card_devices_id'), 'card_devices', ['id'], unique=False)
    op.create_index(op.f('ix_card_devices_card_id'), 'card_devices', ['card_id'], unique=False)
    op.create_index(op.f('ix_card_devices_device_id'), 'card_devices', ['device_id'], unique=False)
    op.create_index('idx_card_device', 'card_devices', ['card_id', 'device_id'], unique=True)

    # 创建用户Token表
    op.create_table(
        'user_tokens',
        sa.Column('id', sa.Integer(), nullable=False, comment='Token ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('app_id', sa.Integer(), nullable=False, comment='应用ID'),
        sa.Column('token', sa.String(length=500), nullable=False, comment='JWT Token'),
        sa.Column('device_id', sa.String(length=255), nullable=False, comment='设备标识'),
        sa.Column('expire_time', sa.DateTime(), nullable=False, comment='过期时间'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['app_id'], ['apps.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index(op.f('ix_user_tokens_id'), 'user_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_user_tokens_user_id'), 'user_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_tokens_app_id'), 'user_tokens', ['app_id'], unique=False)
    op.create_index(op.f('ix_user_tokens_token'), 'user_tokens', ['token'], unique=True)
    op.create_index(op.f('ix_user_tokens_device_id'), 'user_tokens', ['device_id'], unique=False)
    op.create_index('idx_user_app_device', 'user_tokens', ['user_id', 'app_id', 'device_id'], unique=False)


def downgrade() -> None:
    # 按相反顺序删除表（先删除有外键依赖的表）
    op.drop_index('idx_user_app_device', table_name='user_tokens')
    op.drop_index(op.f('ix_user_tokens_device_id'), table_name='user_tokens')
    op.drop_index(op.f('ix_user_tokens_token'), table_name='user_tokens')
    op.drop_index(op.f('ix_user_tokens_app_id'), table_name='user_tokens')
    op.drop_index(op.f('ix_user_tokens_user_id'), table_name='user_tokens')
    op.drop_index(op.f('ix_user_tokens_id'), table_name='user_tokens')
    op.drop_table('user_tokens')

    op.drop_index('idx_card_device', table_name='card_devices')
    op.drop_index(op.f('ix_card_devices_device_id'), table_name='card_devices')
    op.drop_index(op.f('ix_card_devices_card_id'), table_name='card_devices')
    op.drop_index(op.f('ix_card_devices_id'), table_name='card_devices')
    op.drop_table('card_devices')

    op.drop_index('idx_user_card', table_name='user_cards')
    op.drop_index(op.f('ix_user_cards_card_id'), table_name='user_cards')
    op.drop_index(op.f('ix_user_cards_user_id'), table_name='user_cards')
    op.drop_index(op.f('ix_user_cards_id'), table_name='user_cards')
    op.drop_table('user_cards')

    op.drop_index(op.f('ix_cards_card_key'), table_name='cards')
    op.drop_index(op.f('ix_cards_app_id'), table_name='cards')
    op.drop_index(op.f('ix_cards_id'), table_name='cards')
    op.drop_table('cards')

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_apps_app_key'), table_name='apps')
    op.drop_index(op.f('ix_apps_id'), table_name='apps')
    op.drop_table('apps')
