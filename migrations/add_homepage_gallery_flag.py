from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('gallery_image', sa.Column('is_homepage', sa.Boolean(), server_default=sa.false(), nullable=False))

def downgrade():
    op.drop_column('gallery_image', 'is_homepage') 