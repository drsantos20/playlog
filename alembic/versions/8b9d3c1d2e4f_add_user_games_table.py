"""add user games table

Revision ID: 8b9d3c1d2e4f
Revises: 3606cd79e59e
Create Date: 2026-03-24 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b9d3c1d2e4f'
down_revision: Union[str, None] = '3606cd79e59e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('hours_played', sa.Integer(), nullable=False),
        sa.Column('finished_at', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['game_id'], ['games.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'game_id', name='uq_user_games_user_id_game_id'),
    )
    op.create_index(op.f('ix_user_games_game_id'), 'user_games', ['game_id'], unique=False)
    op.create_index(op.f('ix_user_games_id'), 'user_games', ['id'], unique=False)
    op.create_index(op.f('ix_user_games_user_id'), 'user_games', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_games_user_id'), table_name='user_games')
    op.drop_index(op.f('ix_user_games_id'), table_name='user_games')
    op.drop_index(op.f('ix_user_games_game_id'), table_name='user_games')
    op.drop_table('user_games')