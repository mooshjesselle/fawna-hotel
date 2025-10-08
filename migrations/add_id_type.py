from utils.extensions import db

def upgrade():
    # Add id_type column to user table
    with db.engine.connect() as conn:
        conn.execute('ALTER TABLE user ADD COLUMN id_type VARCHAR(50)')

def downgrade():
    # Remove id_type column from user table
    with db.engine.connect() as conn:
        conn.execute('ALTER TABLE user DROP COLUMN id_type') 