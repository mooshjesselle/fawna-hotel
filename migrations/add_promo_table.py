from utils.extensions import db

def upgrade(app):
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute('''
                CREATE TABLE promo (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    title VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    image VARCHAR(255),
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

def downgrade(app):
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute('DROP TABLE IF EXISTS promo') 