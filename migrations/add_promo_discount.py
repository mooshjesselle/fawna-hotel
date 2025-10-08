from utils.extensions import db

def upgrade(app):
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute('ALTER TABLE promo ADD COLUMN discount_percentage FLOAT DEFAULT 0.0')

def downgrade(app):
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute('ALTER TABLE promo DROP COLUMN discount_percentage') 