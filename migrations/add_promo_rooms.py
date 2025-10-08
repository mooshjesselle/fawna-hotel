from utils.extensions import db

def upgrade(app):
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS promo_rooms (
                    promo_id INTEGER NOT NULL,
                    room_id INTEGER NOT NULL,
                    PRIMARY KEY (promo_id, room_id),
                    FOREIGN KEY(promo_id) REFERENCES promo(id) ON DELETE CASCADE,
                    FOREIGN KEY(room_id) REFERENCES room(id) ON DELETE CASCADE
                )
            ''')

def downgrade(app):
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute('DROP TABLE IF EXISTS promo_rooms') 