from utils.extensions import db
from flask_login import UserMixin
from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from utils.datetime_utils import format_datetime
from sqlalchemy.orm import validates
import re
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(200))
    
    # Fields for ID verification
    id_picture = db.Column(db.String(255))  # Path to uploaded ID
    id_type = db.Column(db.String(50))  # Type of ID uploaded
    registration_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), unique=True)
    email_verification_sent_at = db.Column(db.DateTime)
    verification_token = db.Column(db.String(100))
    
    # Relationships
    bookings = db.relationship('Booking', foreign_keys='Booking.user_id', back_populates='user', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='author', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Bookings approved/rejected by this user (as admin)
    approved_bookings = db.relationship('Booking', 
                                      foreign_keys='Booking.approved_by',
                                      back_populates='approved_by_user',
                                      passive_deletes=True)
    rejected_bookings = db.relationship('Booking', 
                                      foreign_keys='Booking.rejected_by',
                                      back_populates='rejected_by_user',
                                      passive_deletes=True)

    def generate_verification_token(self):
        """Generate a new email verification token"""
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = datetime.utcnow()
        return self.email_verification_token

    def set_password(self, password):
        """Set the user's password using secure hashing."""
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email}>'

class RoomType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    rooms = db.relationship('Room', backref='room_type', lazy=True)
    
    @validates('price_per_night')
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        if price > 50000:
            raise ValueError("Price cannot exceed ₱50,000")
        return price
    
    @validates('name')
    def validate_name(self, key, name):
        # Validate length
        if len(name) < 2 or len(name) > 50:
            raise ValueError("Name must be between 2 and 50 characters")
        
        # Validate word count
        word_count = len(name.split())
        if word_count > 20:
            raise ValueError("Name cannot exceed 20 words")
        
        # Validate repeated characters
        if re.search(r'(.)\1{4,}', name):
            raise ValueError("Name contains too many repeated characters")
            
        return name
        
    @validates('description')
    def validate_description(self, key, description):
        # Validate length
        if len(description) < 10 or len(description) > 500:
            raise ValueError("Description must be between 10 and 500 characters")
        
        # Validate word count
        word_count = len(description.split())
        if word_count > 100:
            raise ValueError("Description cannot exceed 100 words")
            
        # Validate repeated characters
        if re.search(r'(.)\1{4,}', description):
            raise ValueError("Description contains too many repeated characters")
        
        return description

# Define the association table for Room-Amenity relationship
room_amenities = db.Table('room_amenities',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'), primary_key=True)
)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    occupancy_limit = db.Column(db.Integer, nullable=False, default=2)
    image = db.Column(db.String(255))
    amenities = db.relationship('Amenity', secondary=room_amenities, backref='rooms')
    bookings = db.relationship('Booking', back_populates='room', lazy=True)

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    additional_cost = db.Column(db.Float, default=0)
    
    @validates('additional_cost')
    def validate_cost(self, key, cost):
        if cost < 0:
            raise ValueError("Additional cost cannot be negative")
        if cost > 20000:
            raise ValueError("Additional cost cannot exceed ₱20,000")
        return cost
        
    @validates('name')
    def validate_name(self, key, name):
        # Validate length
        if len(name) < 2 or len(name) > 50:
            raise ValueError("Name must be between 2 and 50 characters")
        
        # Validate word count
        word_count = len(name.split())
        if word_count > 20:
            raise ValueError("Name cannot exceed 20 words")
        
        # Validate repeated characters
        if re.search(r'(.)\1{4,}', name):
            raise ValueError("Name contains too many repeated characters")
            
        return name
        
    @validates('description')
    def validate_description(self, key, description):
        # Validate length
        if len(description) < 10 or len(description) > 500:
            raise ValueError("Description must be between 10 and 500 characters")
        
        # Validate word count
        word_count = len(description.split())
        if word_count > 100:
            raise ValueError("Description cannot exceed 100 words")
            
        # Validate repeated characters
        if re.search(r'(.)\1{4,}', description):
            raise ValueError("Description contains too many repeated characters")
        
        return description

# Association table for Booking-Amenity (selected amenities per booking)
booking_amenity = db.Table('booking_amenity',
    db.Column('booking_id', db.Integer, db.ForeignKey('booking.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'), primary_key=True)
)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    num_guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, cancelled, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    
    # Payment information
    payment_method = db.Column(db.String(20), nullable=False)  # pay_on_site, gcash
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid
    payment_reference = db.Column(db.String(100))  # For GCash reference number
    payment_screenshot = db.Column(db.String(255))  # Path to payment screenshot
    
    # Approval/rejection tracking
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    approved_at = db.Column(db.DateTime)
    rejected_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    rejected_at = db.Column(db.DateTime)
    
    # Cancellation tracking
    cancellation_reason = db.Column(db.Text)
    cancelled_at = db.Column(db.DateTime)
    # Rejection tracking (separate from cancellation)
    rejection_reason = db.Column(db.Text)
    
    # Relationships
    room = db.relationship('Room', back_populates='bookings')
    user = db.relationship('User', foreign_keys=[user_id], back_populates='bookings')
    approved_by_user = db.relationship('User', foreign_keys=[approved_by], back_populates='approved_bookings')
    rejected_by_user = db.relationship('User', foreign_keys=[rejected_by], back_populates='rejected_bookings')
    comments = db.relationship('Comment', back_populates='booking')
    # New: selected amenities for this booking
    selected_amenities = db.relationship('Amenity', secondary=booking_amenity, backref='bookings_selected')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Use back_populates instead of backref
    author = db.relationship('User', back_populates='comments')
    booking = db.relationship('Booking', back_populates='comments')

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_homepage = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'is_homepage': self.is_homepage
        }

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'booking', 'system', etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', back_populates='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': format_datetime(self.created_at)
        }

class HomePageImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'created_at': self.created_at,
            'order': self.order
        }

class HomePageSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carousel_interval = db.Column(db.Integer, default=4)  # seconds

    @staticmethod
    def get_settings():
        settings = HomePageSettings.query.first()
        if not settings:
            settings = HomePageSettings(carousel_interval=4)
            db.session.add(settings)
            db.session.commit()
        return settings 

promo_rooms = db.Table('promo_rooms',
    db.Column('promo_id', db.Integer, db.ForeignKey('promo.id'), primary_key=True),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True)
)

class Promo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))  # Path to promo image
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    discount_percentage = db.Column(db.Float, default=0.0)  # New field for discount
    rooms = db.relationship('Room', secondary=promo_rooms, backref='promos')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_active': self.is_active,
            'discount_percentage': self.discount_percentage
        } 