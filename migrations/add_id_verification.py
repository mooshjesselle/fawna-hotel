from utils.extensions import db
 
def upgrade():
    # Add new columns to user table
    with db.engine.connect() as conn:
        conn.execute('ALTER TABLE user ADD COLUMN id_picture VARCHAR(255)')
        conn.execute("ALTER TABLE user ADD COLUMN registration_status VARCHAR(20) DEFAULT 'pending'") 