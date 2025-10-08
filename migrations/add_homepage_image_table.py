from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'home_page_image',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime),
        sa.Column('order', sa.Integer, default=0)
    )

def downgrade():
    op.drop_table('home_page_image') 