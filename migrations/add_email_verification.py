from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add email verification columns to user table
    op.add_column('user', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('email_verification_token', sa.String(100), unique=True, nullable=True))
    op.add_column('user', sa.Column('email_verification_sent_at', sa.DateTime(), nullable=True))

def downgrade():
    # Remove email verification columns from user table
    op.drop_column('user', 'email_verification_sent_at')
    op.drop_column('user', 'email_verification_token')
    op.drop_column('user', 'email_verified') 