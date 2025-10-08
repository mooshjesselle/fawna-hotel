from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'home_page_settings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('carousel_interval', sa.Integer, default=4)
    )

def downgrade():
    op.drop_table('home_page_settings') 