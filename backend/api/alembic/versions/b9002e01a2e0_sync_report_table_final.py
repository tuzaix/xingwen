"""sync_report_table_final

Revision ID: b9002e01a2e0
Revises: 9efc1eeecc89
Create Date: 2026-05-05 03:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'b9002e01a2e0'
down_revision: Union[str, None] = '9efc1eeecc89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 为 reports 表补全缺失的列
    # 检查列是否存在，如果不存在则添加
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('reports')]
    
    if 'progress' not in columns:
        op.add_column('reports', sa.Column('progress', sa.Integer(), server_default='0', nullable=True))
    if 'progress_desc' not in columns:
        op.add_column('reports', sa.Column('progress_desc', sa.String(length=100), nullable=True))
    if 'sections' not in columns:
        op.add_column('reports', sa.Column('sections', sa.JSON(), nullable=True))
    if 'bazi' not in columns:
        op.add_column('reports', sa.Column('bazi', sa.String(length=100), nullable=True))
    else:
        # 如果已存在，确保长度正确
        op.alter_column('reports', 'bazi', type_=sa.String(length=100), existing_type=sa.String(length=256))
        
    if 'bazi_favorable_elements' not in columns:
        op.add_column('reports', sa.Column('bazi_favorable_elements', sa.String(length=200), nullable=True))
    else:
        # 如果已存在，确保长度正确
        op.alter_column('reports', 'bazi_favorable_elements', type_=sa.String(length=200), existing_type=sa.String(length=512))

    # 2. 清理多余索引或添加缺失索引 (根据 autogenerate 结果)
    # 这些索引可能是手动创建的优化索引，也可能是旧版遗留
    try:
        op.drop_index('idx_admin_status', table_name='admin_users')
    except: pass
    try:
        op.drop_index('idx_cards_batch_status', table_name='card_codes')
    except: pass
    try:
        op.drop_index('idx_cards_expire_status', table_name='card_codes')
    except: pass
    try:
        op.drop_index('idx_logs_admin_time', table_name='operation_logs')
    except: pass
    try:
        op.drop_index('idx_reports_card_code', table_name='reports')
    except: pass
    try:
        op.drop_index('idx_reports_status_created', table_name='reports')
    except: pass
    try:
        op.drop_index('idx_reports_user_id', table_name='reports')
    except: pass
    try:
        op.drop_index('idx_configs_key', table_name='system_configs')
    except: pass


def downgrade() -> None:
    # 简单的回滚逻辑
    op.drop_column('reports', 'progress')
    op.drop_column('reports', 'progress_desc')
    op.drop_column('reports', 'sections')
    op.drop_column('reports', 'bazi')
    op.drop_column('reports', 'bazi_favorable_elements')
