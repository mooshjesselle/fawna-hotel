from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, current_app, Blueprint
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Room, RoomType, Booking, Amenity, Comment, GalleryImage, Notification, HomePageImage, HomePageSettings, Promo
from blueprints.forms import LoginForm, RegistrationForm, ForgotPasswordForm
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
from functools import wraps
import time
from flask_mail import Message
from utils.extensions import mail
import re
import random
import string
from utils.notifications import (
    create_notification,
    create_booking_notification,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    get_unread_notifications_count,
    get_user_notifications
)
from utils.datetime_utils import format_datetime
from utils.email_utils import generate_otp, send_otp_email, store_otp, verify_otp
import threading
from utils.food_service_api import get_food_menu, send_food_order, send_order_to_checkout_php, get_food_order_history, cancel_food_order, delete_food_order, get_food_service_ip, get_food_rating, post_food_rating
import requests
import json


def format_name(name):
    """Format a name to title case and remove any non-letter characters except spaces"""
    if not name:
        return ""
    # Remove any characters that aren't letters or spaces
    name = re.sub(r'[^A-Za-z\s]', '', name)
    # Convert to title case
    return " ".join(word.capitalize() for word in name.lower().split())

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Make format_datetime available to all templates
@app.context_processor
def utility_processor():
    return dict(format_datetime=format_datetime)
@app.route('/sw.js')
def service_worker():
    # Minimal service worker with push and notification click
    sw_js = (
        "self.addEventListener('install', e => { self.skipWaiting(); });\n"
        "self.addEventListener('activate', e => { self.clients.claim(); });\n"
        "self.addEventListener('push', function(event){\n"
        "  let data = {};\n"
        "  try { data = event.data ? event.data.json() : {}; } catch(e) { data = { title: 'Notification', body: event.data ? event.data.text() : '' }; }\n"
        "  const title = data.title || 'FAWNA Hotel';\n"
        "  const options = { body: data.body || '', icon: data.icon || '/static/images/fawna.png', data: data.url || '/' };\n"
        "  event.waitUntil(self.registration.showNotification(title, options));\n"
        "});\n"
        "self.addEventListener('notificationclick', function(event){\n"
        "  event.notification.close();\n"
        "  const url = event.notification.data || '/';\n"
        "  event.waitUntil(clients.matchAll({ type: 'window' }).then(list => {\n"
        "    for (const client of list) { if (client.url === url && 'focus' in client) return client.focus(); }\n"
        "    if (clients.openWindow) return clients.openWindow(url);\n"
        "  }));\n"
        "});\n"
    )
    return app.response_class(sw_js, mimetype='application/javascript')

@app.route('/push/vapid-public-key')
def get_vapid_public_key():
    return jsonify({ 'key': current_app.config.get('VAPID_PUBLIC_KEY', '') })

@app.route('/push/subscribe', methods=['POST'])
def push_subscribe():
    try:
        subscription = request.get_json(force=True)
        subs_path = os.path.join(app.instance_path, 'push_subscriptions.json')
        os.makedirs(app.instance_path, exist_ok=True)
        existing = []
        if os.path.exists(subs_path):
            with open(subs_path, 'r', encoding='utf-8') as f:
                try:
                    existing = json.load(f)
                except Exception:
                    existing = []
        # upsert by endpoint
        existing = [s for s in existing if s.get('endpoint') != subscription.get('endpoint')]
        existing.append(subscription)
        with open(subs_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f)
        return jsonify({ 'success': True })
    except Exception as e:
        return jsonify({ 'success': False, 'message': str(e) }), 400

# Authentication routes
@app.route('/')
def index():
    """Homepage route - FAWNA Hotel landing page"""
    homepage_images = HomePageImage.query.order_by(HomePageImage.order, HomePageImage.created_at.desc()).all()
    settings = HomePageSettings.get_settings()
    today = datetime.now().date()
    promos = Promo.query.filter(
        Promo.is_active == True,
        Promo.start_date <= today,
        Promo.end_date >= today
    ).order_by(Promo.start_date.desc()).all()
    food_service_ip = current_app.config.get('FOOD_SERVICE_IPV4')
    return render_template('index.html', homepage_images=homepage_images, carousel_interval=settings.carousel_interval, promos=promos, food_service_ip=food_service_ip)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Unified login route for both users and admins"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard' if current_user.is_admin else 'dashboard'))
    
    form = LoginForm()
    register_form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if not user:
                flash('Email not found. Please register first.', 'danger')
                return render_template('auth/login.html', form=form, register_form=register_form, user_type='user')

            # Admin login path
            if user.is_admin:
                if check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    flash('Welcome back, Administrator!', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid password', 'danger')
                    return render_template('auth/login.html', form=form, register_form=register_form, user_type='admin')

            # Regular user login path
            if user.registration_status == 'rejected':
                flash('Email not found. Please register first.', 'danger')
                return render_template('auth/login.html', form=form, register_form=register_form, user_type='user')

            if not user.email_verified:
                flash('Please verify your email address first. Check your inbox or click below to resend verification email.', 'warning')
                return render_template('auth/login.html', form=form, register_form=register_form, user_type='user', unverified_email=user.email)

            if user.registration_status == 'pending':
                flash('Your account is pending approval from admin. Please wait for verification.', 'warning')
                return render_template('auth/login.html', form=form, register_form=register_form, user_type='user')

            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash('Login successful!', 'success')
                return redirect(next_page if next_page else url_for('dashboard'))
            else:
                flash('Incorrect password. Please try again.', 'danger')
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
    return render_template('auth/login.html', form=form, register_form=register_form, user_type='user')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('auth/register.html', title='Create Your Account')

@app.route('/send-verification-email', methods=['POST'])
def send_verification_email():
    try:
        data = request.get_json()
        email = data.get('email', '').lower()
        
        # Validate email format
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        email_pattern = r'^[a-z0-9._%+-]{3,}@([a-z0-9.-]+\.[a-z]{2,})$'
        
        if not re.match(email_pattern, email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format. Email must have at least 3 characters before @ and use lowercase letters.'
            }), 400
        
        domain = email.split('@')[-1]
        if domain not in allowed_domains:
            return jsonify({
                'success': False,
                'message': f'Email domain not allowed. Please use one of: {", ".join(allowed_domains)}'
            }), 400
        
        # Check if email already exists and is verified
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.email_verified:
            return jsonify({
                'success': False,
                'message': 'This email is already registered.'
            }), 400
        
        # Generate 6-digit verification code
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        # Store verification code in session with timestamp
        session['email_verification'] = {
            'email': email,
            'code': verification_code,
            'timestamp': datetime.now().timestamp(),
            'attempts': 0
        }
        
        # Send verification email with timeout handling
        msg = Message('Email Verification - FAWNA Hotel',
                     recipients=[email])
        msg.html = render_template('auth/email/verification_code.html',
                                 code=verification_code)
        
        # Use async email sending to prevent timeouts
        from utils.email_utils import send_email_async
        send_email_async(mail, msg)
        
        return jsonify({
            'success': True,
            'message': 'Verification code sent successfully.'
        })
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to send verification code. Please try again.'
        }), 500

@app.route('/verify-email-code', methods=['POST'])
def verify_email_code():
    try:
        data = request.get_json()
        email = data.get('email', '').lower()
        code = data.get('code', '')
        
        # Get verification data from session
        verification_data = session.get('email_verification')
        if not verification_data:
            return jsonify({
                'success': False,
                'message': 'Verification session expired. Please request a new code.'
            }), 400
        
        # Check if verification is for the same email
        if verification_data['email'] != email:
            return jsonify({
                'success': False,
                'message': 'Invalid verification attempt.'
            }), 400
        
        # Check if code has expired (5 minutes)
        timestamp = datetime.fromtimestamp(verification_data['timestamp'])
        if datetime.now() - timestamp > timedelta(minutes=5):
            session.pop('email_verification', None)
            return jsonify({
                'success': False,
                'message': 'Verification code has expired. Please request a new code.'
            }), 400
        
        # Check if code matches
        if verification_data['code'] != code:
            verification_data['attempts'] += 1
            if verification_data['attempts'] >= 3:
                session.pop('email_verification', None)
                return jsonify({
                    'success': False,
                    'message': 'Too many incorrect attempts. Please request a new code.'
                }), 400
            
            return jsonify({
                'success': False,
                'message': f'Invalid code. {3 - verification_data["attempts"]} attempts remaining.'
            }), 400
        
        # Store verified email in session
        session['verified_email'] = email
        session.pop('email_verification', None)
        
        # Get any previously stored registration data
        registration_data = session.get('registration_data', {})
        
        return jsonify({
            'success': True,
            'message': 'Email verified successfully.',
            'registration_data': registration_data
        })
    except Exception as e:
        print(f"Error verifying email code: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to verify code. Please try again.'
        }), 500

@app.route('/complete-registration', methods=['POST'])
def complete_registration():
    try:
        # Get form data
        first_name = format_name(request.form.get('first_name'))
        middle_name = format_name(request.form.get('middle_name'))
        surname = format_name(request.form.get('surname'))
        suffix = request.form.get('suffix')
        phone = request.form.get('phone')
        email = request.form.get('verified_email')
        password = request.form.get('password')
        id_type = request.form.get('id_type')
        id_picture = request.files.get('id_picture')
        
        # Validate required fields
        if not all([first_name, surname, phone, email, password, id_type, id_picture]):
            return jsonify({
                'success': False,
                'message': 'All required fields must be filled out.'
            }), 400

        # Validate password strength: 8+ chars, 1 upper, 1 lower, 1 digit, 1 special
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};:\'"\\|,.<>\/?]).{8,}$'
        if not re.match(password_pattern, password or ''):
            return jsonify({
                'success': False,
                'error_type': 'validation',
                'field': 'password',
                'message': 'Password must be at least 8 characters and include uppercase, lowercase, number, and special character.'
            }), 400

        # Validate phone number format
        if not re.match(r'^\+639\d{9}$', phone):
            return jsonify({
                'success': False,
                'message': 'Invalid phone number format. Must be in +639XXXXXXXXX format.',
                'field': 'phone'
            }), 400

        # Check if email exists and is verified
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email already registered.'
            }), 400

        # Save ID picture to static/ids so URL paths are /static/ids/<file>
        if id_picture:
            # Validate file extension and mimetype
            filename_original = id_picture.filename or ''
            filename_lower = filename_original.lower()
            allowed_exts = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg'})
            has_allowed_ext = '.' in filename_lower and filename_lower.rsplit('.', 1)[1] in allowed_exts
            is_image_type = (id_picture.mimetype or '').startswith('image/')

            if not has_allowed_ext or not is_image_type:
                return jsonify({
                    'success': False,
                    'message': 'Invalid ID image. Please upload a PNG or JPG image.',
                    'field': 'id_picture'
                }), 400

            filename = secure_filename(f"{int(time.time())}_{filename_original}")
            upload_folder = os.path.join(app.static_folder, 'ids')
            
            # Create directory if it doesn't exist
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            id_picture.save(os.path.join(upload_folder, filename))
        else:
            return jsonify({
                'success': False,
                'message': 'ID picture is required.',
                'field': 'id_picture'
            }), 400

        # Combine name parts into full name
        full_name_parts = [first_name]
        if middle_name:
            full_name_parts.append(middle_name)
        full_name_parts.append(surname)
        if suffix:
            full_name_parts.append(suffix)
        full_name = " ".join(full_name_parts)
        
        # Create new user
        new_user = User(
            name=full_name,
            email=email,
            phone=phone,
            password=generate_password_hash(password),
            id_picture=f"ids/{filename}",
            id_type=id_type,
            registration_status='pending',
            email_verified=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Clear email verification from session
        session.pop('email_verification', None)

        return jsonify({
            'success': True,
            'message': 'Registration successful! Please wait for admin approval.',
            'redirect': url_for('login')
        })
        
    except RequestEntityTooLarge:
        # File too large (exceeds MAX_CONTENT_LENGTH)
        return jsonify({
            'success': False,
            'message': 'ID image is too large. Max size is 5MB.',
            'field': 'id_picture'
        }), 413
    except Exception as e:
        print(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration failed. Please try again.'
        }), 500

@app.route('/verify-email/<token>')
def verify_email(token):
    try:
        # Find user by token
        user = User.query.filter_by(email_verification_token=token).first()
        if not user:
            flash('Invalid verification link.', 'danger')
            return redirect(url_for('login'))
        
        # Check if token is expired (24 hours)
        if user.email_verification_sent_at:
            expiration = user.email_verification_sent_at + timedelta(hours=24)
            if datetime.utcnow() > expiration:
                flash('Verification link has expired. Please register again.', 'danger')
                return redirect(url_for('register'))
        
        # Mark email as verified
        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_sent_at = None
        db.session.commit()
        
        # Use session to carry success message specifically for user login
        flash('Email verified successfully! You can now login to your account.', 'success')
        return redirect(url_for('login'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Verification failed. Please try again. Error: {str(e)}', 'danger')
        return redirect(url_for('login'))

@app.route('/resend-verification')
def resend_verification():
    email = request.args.get('email')
    if not email:
        flash('Email address is required.', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Email address not found.', 'danger')
        return redirect(url_for('login'))
    
    if user.email_verified:
        flash('Email is already verified. Please login.', 'info')
        return redirect(url_for('login'))
    
    # Check if we should allow resending (prevent spam)
    if user.email_verification_sent_at:
        last_sent = user.email_verification_sent_at
        if datetime.utcnow() - last_sent < timedelta(minutes=5):
            flash('Please wait 5 minutes before requesting another verification email.', 'warning')
            return redirect(url_for('login'))
    
    if send_verification_email(user):
        flash('Verification email has been resent. Please check your inbox.', 'success')
    else:
        flash('Failed to send verification email. Please try again later.', 'danger')
    
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Main routes
@app.route('/dashboard')
@login_required
def dashboard():
    food_service_ip = current_app.config.get('FOOD_SERVICE_IPV4')
    print("DEBUG: food_service_ip =", food_service_ip)
    """User dashboard"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Handle expired bookings first
    handle_expired_bookings()
    
    try:
        print(f"Loading dashboard for user {current_user.id} - {current_user.name}")
        
        # More explicit join to ensure comments are loaded
        bookings = (Booking.query
            .filter_by(user_id=current_user.id)
            .outerjoin(Comment, Booking.id == Comment.booking_id)
            .options(
                db.contains_eager(Booking.comments),
                db.joinedload(Booking.room).joinedload(Room.room_type)
            )
            .order_by(Booking.created_at.desc())  # Sort by created_at in descending order (most recent first)
            .all()
        )
        
        # Get all room types for the room type filter
        room_types = RoomType.query.all()
        
        # Debug output
        print(f"Found {len(bookings)} bookings for user")
        for booking in bookings:
            print(f"Booking {booking.id} - Room {booking.room.room_number} - Status: {booking.status}")
            print(f"  Comments: {len(booking.comments)}")
            
            # Print info about each comment
            for comment in booking.comments:
                print(f"  - Comment {comment.id}: Rating {comment.rating}, Content: {comment.content[:30]}...")
                print(f"    Created at: {comment.created_at}")
        
        return render_template('dashboard.html', bookings=bookings, room_types=room_types, food_service_ipv4=current_app.config.get('FOOD_SERVICE_IPV4'), food_service_ip=food_service_ip)
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash("Error loading your bookings. Please try again later.", "error")
        return render_template('dashboard.html', bookings=[], food_service_ipv4=current_app.config.get('FOOD_SERVICE_IPV4'), food_service_ip=food_service_ip)

@app.route('/admin-dashboard')
@login_required
@admin_required
def admin_dashboard():
    try:
        # Get time period from query parameters, default to last 7 days
        period = request.args.get('period', '7days')
        custom_start = request.args.get('start')
        custom_end = request.args.get('end')

        # Calculate date range based on period
        today = datetime.now()
        if custom_start and custom_end:
            start_date = datetime.strptime(custom_start, '%Y-%m-%d')
            end_date = datetime.strptime(custom_end, '%Y-%m-%d')
        else:
            if period == '30days':
                start_date = today - timedelta(days=29)
            elif period == '90days':
                start_date = today - timedelta(days=89)
            else:  # Default to 7 days
                start_date = today - timedelta(days=6)
            end_date = today

        dates = [(start_date + timedelta(days=x)).strftime('%Y-%m-%d') 
                for x in range((end_date - start_date).days + 1)]
        
        # Get booking statistics
        total_bookings = Booking.query.count()
        pending_bookings = Booking.query.filter_by(status='pending').count()
        approved_bookings = Booking.query.filter_by(status='approved').count()
        completed_bookings = Booking.query.filter_by(status='completed').count()
        rejected_bookings = Booking.query.filter_by(status='rejected').count()
        cancelled_bookings = Booking.query.filter_by(status='cancelled').count()
        
        # Enhanced room statistics with detailed occupancy data
        room_stats = db.session.query(
            Room.id,
            Room.room_number,
            RoomType.name.label('room_type'),
            Room.is_available,
            db.func.count(Booking.id).label('total_bookings')
        ).join(RoomType, Room.room_type_id == RoomType.id)\
         .outerjoin(Booking, db.and_(
             Room.id == Booking.room_id,
             Booking.status.in_(['approved', 'pending'])
         ))\
         .group_by(Room.id, Room.room_number, RoomType.name, Room.is_available)\
         .order_by(RoomType.name, Room.room_number)\
         .all()

        # Process room statistics
        room_occupancy_data = {
            'labels': [],
            'occupied': [],
            'available': [],
            'room_types': []
        }

        current_room_type = None
        type_occupied = 0
        type_available = 0

        for room in room_stats:
            if current_room_type != room.room_type:
                if current_room_type is not None:
                    room_occupancy_data['labels'].append(current_room_type)
                    room_occupancy_data['occupied'].append(type_occupied)
                    room_occupancy_data['available'].append(type_available)
                current_room_type = room.room_type
                type_occupied = 0
                type_available = 0
            
            if not room.is_available or room.total_bookings > 0:
                type_occupied += 1
            else:
                type_available += 1

        # Add the last room type
        if current_room_type is not None:
            room_occupancy_data['labels'].append(current_room_type)
            room_occupancy_data['occupied'].append(type_occupied)
            room_occupancy_data['available'].append(type_available)
        
        # Get room booking trends
        room_trends = db.session.query(
            Room.id,
            RoomType.name.label('room_type'),
            db.func.count(Booking.id).label('booking_count')
        ).join(RoomType, Room.room_type_id == RoomType.id)\
         .join(Booking, Room.id == Booking.room_id)\
         .filter(
             Booking.created_at >= start_date,
             Booking.created_at <= end_date
         ).group_by(Room.id, RoomType.name)\
         .order_by(db.func.count(Booking.id).desc())\
         .limit(5)\
         .all()

        # Get hourly booking trends with additional metrics
        hourly_trends = db.session.query(
            db.func.extract('hour', Booking.created_at).label('hour'),
            db.func.count(Booking.id).label('count'),
            db.func.avg(Booking.total_price).label('avg_price')
        ).filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date
        ).group_by('hour')\
         .order_by('hour')\
         .all()

        hourly_data = {
            'labels': [str(i).zfill(2) for i in range(24)],
            'bookings': [0] * 24,
            'revenue': [0.0] * 24
        }
        
        for hour, count, avg_price in hourly_trends:
            hour_index = int(hour)
            hourly_data['bookings'][hour_index] = count
            hourly_data['revenue'][hour_index] = float(avg_price or 0) * count
        
        # Get user statistics
        total_users = User.query.count()
        admin_users = User.query.filter_by(is_admin=True).count()
        regular_users = User.query.filter_by(is_admin=False).count()
        
        # Calculate revenue statistics
        revenue_stats = db.session.query(
            db.func.sum(Booking.total_price).label('total'),
            db.func.avg(Booking.total_price).label('average'),
            db.func.count(Booking.id).label('count')
        ).filter(Booking.status.in_(['approved', 'completed']))\
         .first()
        
        total_revenue = float(revenue_stats.total or 0)
        avg_revenue_per_booking = float(revenue_stats.average or 0)
            
        # Get booking trends
        booking_trends = db.session.query(
            db.func.date(Booking.created_at).label('date'),
            db.func.count(Booking.id).label('count')
        ).filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date
        ).group_by('date').all()
        
        booking_data = {date: 0 for date in dates}
        for date, count in booking_trends:
            booking_data[date.strftime('%Y-%m-%d')] = count
            
        # Get revenue trends with daily averages
        revenue_trends = db.session.query(
            db.func.date(Booking.created_at).label('date'),
            db.func.sum(Booking.total_price).label('revenue'),
            db.func.avg(Booking.total_price).label('avg_revenue'),
            db.func.count(Booking.id).label('booking_count')
        ).filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status.in_(['approved', 'completed'])
        ).group_by('date').all()
        
        revenue_data = {
            'total': {date: 0 for date in dates},
            'average': {date: 0 for date in dates}
        }
        
        for date, revenue, avg_revenue, count in revenue_trends:
            date_str = date.strftime('%Y-%m-%d')
            revenue_data['total'][date_str] = float(revenue or 0)
            revenue_data['average'][date_str] = float(avg_revenue or 0)
        
        # Get recent bookings with more details
        recent_bookings = Booking.query\
            .join(User, Booking.user_id == User.id)\
            .join(Room, Booking.room_id == Room.id)\
            .join(RoomType, Room.room_type_id == RoomType.id)\
            .options(
                db.joinedload(Booking.user),
                db.joinedload(Booking.room).joinedload(Room.room_type)
            )\
            .order_by(Booking.created_at.desc())\
            .limit(5)\
            .all()
        
        # New: Bookings per Room Name
        room_booking_counts = (
            db.session.query(
                Room.room_number,
                db.func.count(Booking.id).label('booking_count')
            )
            .outerjoin(Booking, Room.id == Booking.room_id)
            .group_by(Room.room_number)
            .order_by(Room.room_number)
            .all()
        )

        room_bookings = {
            'labels': [r.room_number for r in room_booking_counts],
            'data': [r.booking_count for r in room_booking_counts]
        }
        
        # Get booking trends grouped by date and room name
        booking_trends_query = (
            db.session.query(
                db.func.date(Booking.created_at).label('date'),
                Room.room_number.label('room_name'),
                db.func.count(Booking.id).label('count')
            )
            .join(Room, Booking.room_id == Room.id)
            .filter(
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
            .group_by('date', 'room_name')
            .order_by('date', 'room_name')
            .all()
        )

        # Build a dict: {room_name: {date: count}}
        room_date_counts = {}
        for date, room_name, count in booking_trends_query:
            if room_name not in room_date_counts:
                room_date_counts[room_name] = {d: 0 for d in dates}
            room_date_counts[room_name][date.strftime('%Y-%m-%d')] = count

        # Prepare Chart.js datasets
        booking_trends_datasets = []
        colors = ['#FF6B6B', '#42A5F5', '#66BB6A', '#FFA726', '#8D6E63', '#AB47BC', '#26A69A', '#EC407A']
        for i, (room_name, date_counts) in enumerate(room_date_counts.items()):
            booking_trends_datasets.append({
                'label': room_name,
                'data': [date_counts[d] for d in dates],
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)],
                'fill': False
            })

        # Find the earliest booking date
        earliest_booking = Booking.query.order_by(Booking.created_at.asc()).first()
        has_30_days = False
        has_90_days = False
        if earliest_booking:
            days_of_data = (today - earliest_booking.created_at).days
            has_30_days = days_of_data >= 29
            has_90_days = days_of_data >= 89

        data = {
            'booking_stats': {
                'total': total_bookings,
                'pending': pending_bookings,
                'approved': approved_bookings,
                'completed': completed_bookings,
                'rejected': rejected_bookings,
                'cancelled': cancelled_bookings
            },
            'room_occupancy': room_occupancy_data,
            'room_trends': [{
                'room_type': trend.room_type,
                'booking_count': trend.booking_count
            } for trend in room_trends],
            'hourly_trends': hourly_data,
            'user_stats': {
                'total': total_users,
                'admin': admin_users,
                'regular': regular_users
            },
            'revenue_stats': {
                'total': total_revenue,
                'average': avg_revenue_per_booking,
                'booking_count': revenue_stats.count
            },
            'booking_trends': {
                'labels': dates,
                'datasets': booking_trends_datasets
            },
            'revenue_trends': {
                'labels': list(revenue_data['total'].keys()),
                'data': list(revenue_data['total'].values()),
                'averages': list(revenue_data['average'].values())
            },
            'recent_bookings': [{
                'id': booking.id,
                'user': booking.user.name,
                'room_type': booking.room.room_type.name,
                'room_number': booking.room.room_number,
                'check_in': booking.check_in_date.strftime('%Y-%m-%d'),
                'check_out': booking.check_out_date.strftime('%Y-%m-%d'),
                'total_price': float(booking.total_price),
                'status': booking.status,
                'created_at': format_datetime(booking.created_at)
            } for booking in recent_bookings],
            'room_bookings': room_bookings,
            'has_30_days': has_30_days,
            'has_90_days': has_90_days
        }
        
        print("DASHBOARD DATA:", data)
        return render_template('admin/dashboard.html', data=data)
    except Exception as e:
        import traceback
        print(f"Error in admin dashboard: {str(e)}")
        traceback.print_exc()
        # Provide default values so the dashboard always renders
        data = {
            'booking_stats': {
                'total': 0,
                'pending': 0,
                'approved': 0,
                'completed': 0,
                'rejected': 0,
                'cancelled': 0
            },
            'room_occupancy': {
                'labels': [],
                'occupied': [],
                'available': []
            },
            'room_trends': [],
            'hourly_trends': {
                'labels': [str(i).zfill(2) for i in range(24)],
                'bookings': [0]*24,
                'revenue': [0.0]*24
            },
            'user_stats': {
                'total': 0,
                'admin': 0,
                'regular': 0
            },
            'revenue_stats': {
                'total': 0,
                'average': 0,
                'booking_count': 0
            },
            'booking_trends': {
                'labels': [],
                'datasets': []
            },
            'revenue_trends': {
                'labels': [],
                'data': [],
                'averages': []
            },
            'recent_bookings': [],
            'room_bookings': {
                'labels': [],
                'data': []
            }
        }
        print("DASHBOARD DATA (ERROR):", data)
        flash('Error loading dashboard data', 'error')
        return render_template('admin/dashboard.html', data=data)

# Room management
@app.route('/rooms')
def rooms():
    try:
        handle_expired_bookings()
        search_query = request.args.get('search', '').strip().lower()
        room_type_id = request.args.get('room_type')
        promo_id = request.args.get('promo_id', type=int)
        promo = None
        if promo_id:
            promo = Promo.query.get(promo_id)
        room_types = RoomType.query.all()
        rooms_query = Room.query.options(
            db.joinedload(Room.room_type),
            db.joinedload(Room.amenities),
            db.joinedload(Room.bookings).joinedload(Booking.comments)
        )
        rooms_query = rooms_query.filter(Room.is_available == True)
        if room_type_id:
            rooms_query = rooms_query.filter(Room.room_type_id == room_type_id)
        rooms = rooms_query.all()
        if search_query:
            filtered_rooms = []
            for room in rooms:
                if search_query in room.room_type.name.lower():
                    filtered_rooms.append(room)
                    continue
                room_number_str = str(room.room_number).lower()
                if search_query in room_number_str:
                    filtered_rooms.append(room)
                    continue
                for amenity in room.amenities:
                    if search_query in amenity.name.lower():
                        filtered_rooms.append(room)
                        break
                if search_query in room.room_type.description.lower():
                    filtered_rooms.append(room)
                    continue
            rooms = filtered_rooms
        room_ratings = {}
        for room in rooms:
            total_rating = 0
            review_count = 0
            for booking in room.bookings:
                for comment in booking.comments:
                    if comment and comment.rating:
                        total_rating += comment.rating
                        review_count += 1
            room_ratings[room.id] = {
                'avg_rating': round(total_rating / review_count, 1) if review_count > 0 else 0,
                'review_count': review_count
            }
        return render_template('rooms.html', 
                             rooms=rooms,
                             room_types=room_types,
                             room_ratings=room_ratings,
                             promo=promo)
    except Exception as e:
        print(f"Error loading rooms: {e}")
        import traceback
        traceback.print_exc()
        return render_template('rooms.html', 
                             rooms=[],
                             room_types=[],
                             error="Error loading rooms",
                             promo=None)

@app.route('/room/<int:room_id>')
def room_detail(room_id):
    try:
        promo_id = request.args.get('promo_id', type=int)
        promo = None
        room = Room.query.filter_by(id=room_id).options(
            db.joinedload(Room.room_type),
            db.joinedload(Room.amenities),
            db.joinedload(Room.bookings).joinedload(Booking.comments).joinedload(Comment.author)
        ).first_or_404()
        if promo_id:
            candidate = Promo.query.get(promo_id)
            if candidate and room in candidate.rooms:
                promo = candidate
        # Calculate ratings and collect comments
        total_rating = 0
        review_count = 0
        comments = []
        for booking in room.bookings:
            if booking.status == 'completed':
                for comment in booking.comments:
                    if comment and comment.rating:
                        total_rating += comment.rating
                        review_count += 1
                        comments.append({
                            'user': comment.author.name if comment.author else 'Anonymous',
                            'rating': comment.rating,
                            'content': comment.content,
                            'date': comment.created_at.strftime("%B %d, %Y")
                        })
        avg_rating = round(total_rating / review_count, 1) if review_count > 0 else 0
        unavailable_dates = []
        booking_ranges = []
        for booking in room.bookings:
            if booking.status in ['pending', 'approved']:
                # Add all dates in the range to unavailable_dates
                current_date = booking.check_in_date
                while current_date < booking.check_out_date:
                    unavailable_dates.append(current_date)
                    current_date += timedelta(days=1)
                # Add the booking range (inclusive of checkout)
                booking_ranges.append({
                    'check_in': booking.check_in_date,
                    'check_out': booking.check_out_date,
                    'status': booking.status,
                    'guest_name': booking.user.name if hasattr(booking, 'user') and booking.user else None
                })
        return render_template('room_detail.html', 
                             room=room,
                             comments=comments,
                             avg_rating=avg_rating,
                             review_count=review_count,
                             unavailable_dates=unavailable_dates,
                             booking_ranges=booking_ranges,
                             promo=promo)
    except Exception as e:
        print(f"Error loading room details: {e}")
        import traceback
        traceback.print_exc()
        return render_template('error.html', error="Error loading room details")

# Booking management
@app.route('/book_room/<int:room_id>', methods=['POST'])
@login_required
def book_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        check_in = datetime.strptime(request.form.get('check_in'), '%Y-%m-%d')
        check_out = datetime.strptime(request.form.get('check_out'), '%Y-%m-%d')
        guests = request.form.get('guests')
        promo_id = request.form.get('promo_id', type=int)
        promo = None
        if promo_id:
            promo = Promo.query.get(promo_id)
        # Validate required fields
        if not all([check_in, check_out, guests]):
            flash('All fields are required.', 'error')
            return redirect(url_for('room_detail', room_id=room_id))
        # Calculate total price
        nights = (check_out - check_in).days
        price_per_night = room.room_type.price_per_night
        if promo and promo.discount_percentage > 0:
            price_per_night = price_per_night * (1 - promo.discount_percentage / 100)
        total_price = price_per_night * nights
        # Create the booking
        booking = Booking(
            user_id=current_user.id,
            room_id=room_id,
            check_in_date=check_in,
            check_out_date=check_out,
            num_guests=int(guests),
            total_price=total_price,
            status='pending'
        )
        # Optionally store promo_id in booking if supported
        if hasattr(booking, 'promo_id') and promo_id:
            booking.promo_id = promo_id
        db.session.add(booking)
        db.session.commit()
        # Create notification for the booking
        create_booking_notification(booking, 'created')
        flash('Booking request submitted successfully! Please wait for admin approval.', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while processing your booking request.', 'error')
        return redirect(url_for('room_detail', room_id=room_id))

@app.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        # Check if the booking belongs to the current user
        if booking.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'You do not have permission to cancel this booking.'
            }), 403
        # Check if the booking can be cancelled
        if booking.status not in ['pending', 'approved']:
            return jsonify({
                'success': False,
                'message': 'This booking cannot be cancelled.'
            }), 400
        # Prevent cancellation if approved for more than 3 days
        from datetime import datetime, timedelta
        if booking.status == 'approved' and booking.approved_at:
            if datetime.utcnow() - booking.approved_at > timedelta(days=3):
                return jsonify({
                    'success': False,
                    'message': 'This booking was approved more than 3 days ago and can no longer be cancelled.'
                }), 400
        # Get and validate the cancellation reason
        try:
            data = request.get_json()
            reason_select = data.get('reason_select')
            other_reason = data.get('other_reason', '').strip()
            if not reason_select:
                return jsonify({
                    'success': False,
                    'message': 'Please select a reason for cancellation.'
                }), 400
            if reason_select == 'Other':
                if not other_reason:
                    return jsonify({
                        'success': False,
                        'message': 'Please provide a reason for cancellation.'
                    }), 400
                reason = f"Other: {other_reason}"
            else:
                reason = reason_select
        except Exception as e:
            app.logger.error(f"Error parsing request data: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Invalid request data.'
            }), 400
        # Store the current status to check if it was approved
        was_approved = booking.status == 'approved'
        try:
            # Update booking status
            booking.status = 'cancelled'
            booking.cancellation_reason = reason
            booking.cancelled_at = datetime.now()
            # If the booking was approved, make the room available again
            if was_approved:
                room = Room.query.get(booking.room_id)
                if room:
                    room.is_available = True
            db.session.commit()
            # Create notification for admin
            try:
                create_notification(
                    user_id=1,  # Admin user ID
                    title='Booking Cancelled',
                    message=f'Booking #{booking.id} has been cancelled by {current_user.name}.',
                    type='booking'
                )
            except Exception as e:
                app.logger.error(f"Error creating notification: {str(e)}")
                # Don't fail the whole operation if notification fails
                pass
            return jsonify({
                'success': True,
                'message': 'Booking has been cancelled successfully.'
            }), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating booking: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to update booking status.'
            }), 500
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in cancel_booking: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing your request.'
        }), 500

@app.route('/bookings/<int:booking_id>/delete', methods=['POST'])
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'You do not have permission to delete this booking.'
        }), 403
    
    # Only allow deletion of cancelled, rejected, or completed bookings
    if booking.status not in ['cancelled', 'rejected', 'completed']:
        return jsonify({
            'success': False,
            'message': 'Only cancelled, rejected, or completed bookings can be deleted from history.'
        }), 400
    
    try:
        # Delete associated comments first
        Comment.query.filter_by(booking_id=booking.id).delete()
        # Delete the booking
        db.session.delete(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Booking has been deleted from your history.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'An error occurred while deleting the booking.'
        }), 500

# Admin routes
@app.route('/admin/rooms', methods=['GET', 'POST'])
@login_required
def admin_rooms():
    """Admin rooms management"""
    if not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            # Check if room number already exists
            room_number = request.form.get('room_number')
            existing_room = Room.query.filter_by(room_number=room_number).first()
            if existing_room:
                flash(f'Room number {room_number} already exists. Please use a different room number.', 'danger')
                return redirect(url_for('admin_rooms'))

            # Handle image upload
            image_path = None
            cropped_image = request.form.get('cropped_image')
            
            if cropped_image:
                # Remove the data:image/jpeg;base64, prefix
                if 'base64,' in cropped_image:
                    cropped_image = cropped_image.split('base64,')[1]
                
                import base64
                from io import BytesIO
                
                # Convert base64 to image file
                image_data = base64.b64decode(cropped_image)
                image_file = BytesIO(image_data)
                
                # Generate unique filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"room_{timestamp}.jpg"
                
                # Save the cropped image
                image_path = f'room_images/{filename}'
                upload_path = os.path.join(app.root_path, 'static', 'room_images')
                os.makedirs(upload_path, exist_ok=True)
                
                with open(os.path.join(upload_path, filename), 'wb') as f:
                    f.write(image_data)

            # Create new room
            room = Room(
                room_number=room_number,
                room_type_id=request.form.get('room_type_id'),
                floor=request.form.get('floor'),
                occupancy_limit=request.form.get('occupancy_limit', 2),
                image=image_path,
                is_available=True
            )
            
            db.session.add(room)
            db.session.flush()  # Get the room ID before committing
            
            # Handle amenities
            if 'amenities' in request.form:
                amenity_ids = request.form.getlist('amenities')
                for amenity_id in amenity_ids:
                    amenity = Amenity.query.get(int(amenity_id))
                    if amenity:
                        room.amenities.append(amenity)
            
            db.session.commit()
            flash('Room added successfully', 'success')
            return redirect(url_for('admin_rooms'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding room: {str(e)}', 'error')
            return redirect(url_for('admin_rooms'))

    # GET request - show rooms list
    rooms = Room.query.all()
    room_types = RoomType.query.all()
    amenities = Amenity.query.all()
    return render_template('admin/rooms.html', 
                         rooms=rooms,
                         room_types=room_types,
                         amenities=amenities)

@app.route('/admin/amenities', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_amenities():
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            # Remove fa- prefix if it exists, then add it back
            icon = request.form['icon'].replace('fa-', '')
            additional_cost = float(request.form['additional_cost'])

            amenity = Amenity(
                name=name,
                description=description,
                icon=icon,  # Store without fa- prefix
                additional_cost=additional_cost
            )
            db.session.add(amenity)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Amenity added successfully'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400

    # GET request - show amenities page
    amenities = Amenity.query.all()
    return render_template('admin/amenities.html', amenities=amenities)

@app.route('/admin/amenities/<int:amenity_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def manage_amenity(amenity_id):
    amenity = Amenity.query.get_or_404(amenity_id)

    if request.method == 'GET':
        return jsonify({
            'id': amenity.id,
            'name': amenity.name,
            'description': amenity.description,
            'icon': amenity.icon,
            'additional_cost': float(amenity.additional_cost)
        })

    elif request.method == 'PUT':
        try:
            data = request.form
            amenity.name = data['name']
            amenity.description = data['description']
            amenity.icon = data['icon']
            amenity.additional_cost = float(data['additional_cost'])

            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Amenity updated successfully'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400

    elif request.method == 'DELETE':
        try:
            # Instead of checking and returning an error, let's remove the associations
            if amenity.rooms:
                # Get list of rooms for logging/debugging
                room_numbers = [room.room_number for room in amenity.rooms]
                print(f"Removing amenity {amenity.name} from rooms: {', '.join(room_numbers)}")
                
                # Remove the amenity from all rooms
                for room in amenity.rooms:
                    room.amenities.remove(amenity)
                
                # Commit these changes first
                db.session.commit()
                print(f"Successfully removed amenity from all rooms")
            
            # Now delete the amenity
            db.session.delete(amenity)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Amenity deleted successfully'
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting amenity: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400

@app.route('/admin/amenities/<int:id>')
@login_required
@admin_required
def get_amenity(id):
    try:
        amenity = Amenity.query.get_or_404(id)
        return jsonify({
            'id': amenity.id,
            'name': amenity.name,
            'description': amenity.description,
            'icon': amenity.icon,
            'additional_cost': float(amenity.additional_cost or 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/amenities/<int:amenity_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_amenity(amenity_id):
    try:
        amenity = Amenity.query.get_or_404(amenity_id)
        
        # Extract and validate additional cost
        additional_cost = float(request.form['additional_cost'])
        if additional_cost < 0:
            return jsonify({
                'success': False,
                'message': 'Additional cost cannot be negative'
            }), 400
            
        if additional_cost > 20000:
            return jsonify({
                'success': False,
                'message': 'Additional cost cannot exceed ₱20,000'
            }), 400
        
        # Update amenity details
        amenity.name = request.form['name']
        amenity.description = request.form['description']
        # Remove fa- prefix if it exists, then store without prefix
        amenity.icon = request.form['icon'].replace('fa-', '')
        amenity.additional_cost = additional_cost
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Amenity updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/admin/amenities/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_amenity(id):
    try:
        amenity = Amenity.query.get_or_404(id)
        
        # Instead of checking and returning an error, let's remove the associations
        if amenity.rooms:
            # Get list of rooms for logging/debugging
            room_numbers = [room.room_number for room in amenity.rooms]
            print(f"Removing amenity {amenity.name} from rooms: {', '.join(room_numbers)}")
            
            # Remove the amenity from all rooms
            for room in amenity.rooms:
                room.amenities.remove(amenity)
            
            # Commit these changes first
            db.session.commit()
            print(f"Successfully removed amenity from all rooms")
        
        # Now delete the amenity
        db.session.delete(amenity)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Amenity deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting amenity: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/amenities/<int:id>/details')
@login_required
@admin_required
def get_amenity_details(id):
    try:
        print(f"Fetching details for amenity ID: {id}")
        
        # Get amenity without trying to load rooms
        amenity = Amenity.query.get_or_404(id)
        print(f"Found amenity: {amenity.name}")
        
        response_data = {
            'id': amenity.id,
            'name': amenity.name,
            'description': amenity.description or '',
            'icon': amenity.icon or '',
            'additional_cost': float(amenity.additional_cost or 0),
            'rooms': []  # Empty list for now until we fix the relationship
        }
        print(f"Prepared response data: {response_data}")
        
        return jsonify(response_data), 200
    except Exception as e:
        import traceback
        print(f"Error in get_amenity_details: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to load amenity details. Please try again.'}), 500

# Comments and Reviews
@app.route('/booking/<int:booking_id>/comment', methods=['POST'])
@login_required
def add_comment(booking_id):
    """Add a comment/review to a booking"""
    try:
        # Get the booking with room details
        booking = Booking.query.filter_by(
            id=booking_id, 
            user_id=current_user.id
        ).options(
            db.joinedload(Booking.room)
        ).first_or_404()
        
        # Only allow review if booking is completed
        if booking.status != 'completed':
            flash("You can only review a booking after your stay is completed.", "warning")
            return redirect(url_for('dashboard'))
        
        # Debug: Print form data
        print(f"Received form data for comment on booking {booking_id}:")
        for key, value in request.form.items():
            print(f"  {key}: {value}")
        
        # Get rating and text from form
        rating = request.form.get('rating')
        text = request.form.get('comment')
        
        print(f"Rating: {rating}, Comment text: {text}")
        
        if not rating or not text:
            flash("Rating and comment are required", "error")
            return redirect(url_for('dashboard'))
        
        # Limit comment to 100 words
        words = text.split()
        limited_words = []
        
        # Limit each word to 30 characters
        for word in words:
            if len(word) > 30:
                limited_words.append(word[:30])
            else:
                limited_words.append(word)
        
        if len(words) > 100:
            text = ' '.join(limited_words[:100])
            flash("Your comment was truncated to 100 words", "info")
        else:
            text = ' '.join(limited_words)
        
        # Check if a comment already exists
        existing_comment = Comment.query.filter_by(booking_id=booking_id).first()
        if existing_comment:
            flash("You have already reviewed this booking", "warning")
            return redirect(url_for('dashboard'))
        
        # Create a new comment
        comment = Comment(
            booking_id=booking_id,
            user_id=current_user.id,
            rating=int(rating),
            content=text
        )
        
        print(f"Adding comment: Rating={comment.rating}, Content={comment.content}")
        
        # Add to database
        db.session.add(comment)
        db.session.commit()
        
        # Confirm the comment was added successfully
        added_comment = Comment.query.filter_by(id=comment.id).first()
        if added_comment:
            print(f"Successfully added comment with ID {comment.id}")
            print(f"Saved content: {added_comment.content}, rating: {added_comment.rating}")
            flash("Your review has been submitted successfully!", "success")
        else:
            flash("There was an error saving your review", "error")
            
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding comment: {e}")
        import traceback
        traceback.print_exc()
        flash("Error submitting your review. Please try again.", "error")
        return redirect(url_for('dashboard'))

@app.route('/booking/<int:booking_id>/comment/edit', methods=['POST'])
@login_required
def edit_comment(booking_id):
    """Edit an existing comment/review for a booking"""
    try:
        # Get the booking with room details
        booking = Booking.query.filter_by(
            id=booking_id, 
            user_id=current_user.id
        ).options(
            db.joinedload(Booking.room)
        ).first_or_404()
        
        # Debug: Print form data
        print(f"Received form data for editing comment on booking {booking_id}:")
        for key, value in request.form.items():
            print(f"  {key}: {value}")
        
        # Get rating and text from form
        rating = request.form.get('rating')
        text = request.form.get('comment')
        
        print(f"Rating: {rating}, Comment text: {text}")
        
        if not rating or not text:
            flash("Rating and comment are required", "error")
            return redirect(url_for('dashboard'))
        
        # Limit comment to 100 words
        words = text.split()
        limited_words = []
        
        # Limit each word to 30 characters
        for word in words:
            if len(word) > 30:
                limited_words.append(word[:30])
            else:
                limited_words.append(word)
        
        if len(words) > 100:
            text = ' '.join(limited_words[:100])
            flash("Your comment was truncated to 100 words", "info")
        else:
            text = ' '.join(limited_words)
        
        # Find the existing comment
        existing_comment = Comment.query.filter_by(booking_id=booking_id, user_id=current_user.id).first()
        
        if not existing_comment:
            flash("No review found to edit", "error")
            return redirect(url_for('dashboard'))
        
        # Update the comment
        existing_comment.rating = int(rating)
        existing_comment.content = text
        
        print(f"Updating comment: Rating={existing_comment.rating}, Content={existing_comment.content}")
        
        # Save to database
        db.session.commit()
        
        flash("Your review has been updated successfully!", "success")
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating comment: {e}")
        import traceback
        traceback.print_exc()
        flash("Error updating your review. Please try again.", "error")
        return redirect(url_for('dashboard'))

# Add a route to view all reviews for a room
@app.route('/rooms/<int:room_id>/reviews')
def room_reviews(room_id):
    room = Room.query.get_or_404(room_id)
    
    # Get all approved bookings for this room that have comments
    bookings_with_comments = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.status == 'approved'
    ).join(Comment).all()
    
    # Extract comments from these bookings
    comments = []
    for booking in bookings_with_comments:
        for comment in booking.comments:
            comments.append({
                'author': comment.author.name,
                'rating': comment.rating,
                'content': comment.content,
                'date': comment.created_at.strftime('%B %d, %Y')
            })
    
    # Calculate average rating
    if comments:
        avg_rating = sum(c['rating'] for c in comments) / len(comments)
    else:
        avg_rating = 0
    
    return render_template(
        'room_reviews.html',
        room=room,
        comments=comments,
        avg_rating=avg_rating
    )

# Reports
@app.route('/admin/reports')
@login_required
def reports():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    
    total_bookings = Booking.query.count()
    active_bookings = Booking.query.filter_by(status='approved').count()  # Changed from 'confirmed' to 'approved'
    cancelled_bookings = Booking.query.filter_by(status='cancelled').count()
    total_revenue = db.session.query(db.func.sum(Booking.total_price)).filter_by(status='completed').scalar() or 0
    
    return render_template('admin/reports.html',
                         total_bookings=total_bookings,
                         active_bookings=active_bookings,
                         cancelled_bookings=cancelled_bookings,
                         total_revenue=total_revenue)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define the upload folder for profile images
PROFILE_UPLOAD_FOLDER = 'static/images/profiles'  # Changed to use forward slashes for URL compatibility
os.makedirs(os.path.join(app.root_path, PROFILE_UPLOAD_FOLDER), exist_ok=True)

# Update the profile picture upload logic
@app.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        try:
            print("Starting profile update...")  # Debug print
            
            # Get form data
            name = request.form.get('name')
            phone = request.form.get('phone')
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # Validate required fields
            if not name or not phone:
                flash('Name and phone number are required.', 'danger')
                return redirect(url_for('profile'))

            # Update user information
            user = User.query.get(current_user.id)
            user.name = name
            user.phone = phone

            # Handle profile picture upload
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                print(f"Received file: {file.filename}")  # Debug print
                
                if file and file.filename:  # Check if file was actually selected
                    if allowed_file(file.filename):
                        # Delete old profile picture if it exists
                        if user.profile_pic:
                            old_pic_path = os.path.join(app.root_path, 'static', user.profile_pic)
                            print(f"Checking old picture at: {old_pic_path}")  # Debug print
                            try:
                                if os.path.exists(old_pic_path):
                                    os.remove(old_pic_path)
                                    print("Old profile picture deleted")  # Debug print
                            except Exception as e:
                                print(f"Error deleting old profile picture: {e}")

                        # Generate unique filename
                        filename = secure_filename(file.filename)
                        unique_filename = f"profile_{user.id}_{int(time.time())}_{filename}"
                        
                        # Save the new profile picture
                        save_path = os.path.join(app.root_path, PROFILE_UPLOAD_FOLDER, unique_filename)
                        print(f"Saving new picture to: {save_path}")  # Debug print
                        file.save(save_path)
                        
                        # Update user's profile picture in database - store relative path
                        user.profile_pic = f"images/profiles/{unique_filename}"
                        print(f"Updated database path to: {user.profile_pic}")  # Debug print
                    else:
                        flash('Invalid file type. Please upload an image file (png, jpg, jpeg, gif).', 'danger')
                        return redirect(url_for('profile'))

            # Handle password change if requested
            if new_password:
                if not current_password:
                    flash('Current password is required to change password.', 'danger')
                    return redirect(url_for('profile'))
                
                if not check_password_hash(user.password, current_password):
                    flash('Current password is incorrect.', 'danger')
                    return redirect(url_for('profile'))
                
                if new_password != confirm_password:
                    flash('New passwords do not match.', 'danger')
                    return redirect(url_for('profile'))
                
                # Generate password hash using the correct method
                user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

            db.session.commit()
            print("Profile update successful!")  # Debug print
            flash('Profile updated successfully!', 'success')
            
            # If password was changed, update the session
            if new_password:
                login_user(user)
                
        except Exception as e:
            db.session.rollback()
            print(f"Error updating profile: {str(e)}")  # Debug print
            flash(f'Failed to update profile. Error: {str(e)}', 'danger')
        
        return redirect(url_for('profile'))


# Admin booking management
@app.route('/admin/bookings')
@login_required
def admin_bookings():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    # Handle expired bookings first
    handle_expired_bookings()
    
    try:
        # Get bookings with all relationships loaded
        pending_bookings = Booking.query.filter_by(status='pending')\
            .join(User, Booking.user_id == User.id)\
            .join(Room, Booking.room_id == Room.id)\
            .join(RoomType, Room.room_type_id == RoomType.id)\
            .options(
                db.joinedload(Booking.user),
                db.joinedload(Booking.room).joinedload(Room.room_type),
                db.load_only(
                    Booking.id, Booking.check_in_date, Booking.check_out_date,
                    Booking.total_price, Booking.status, Booking.payment_method,
                    Booking.payment_reference, Booking.payment_screenshot
                )
            )\
            .order_by(Booking.created_at.desc()).all()
        
        approved_bookings = Booking.query.filter_by(status='approved')\
            .join(User, Booking.user_id == User.id)\
            .join(Room, Booking.room_id == Room.id)\
            .join(RoomType, Room.room_type_id == RoomType.id)\
            .options(
                db.joinedload(Booking.user),
                db.joinedload(Booking.room).joinedload(Room.room_type),
                db.joinedload(Booking.approved_by_user),
                db.load_only(
                    Booking.id, Booking.check_in_date, Booking.check_out_date,
                    Booking.total_price, Booking.status, Booking.payment_method,
                    Booking.payment_reference, Booking.payment_screenshot
                )
            )\
            .order_by(Booking.approved_at.desc()).all()
        
        completed_bookings = Booking.query.filter_by(status='completed')\
            .join(User, Booking.user_id == User.id)\
            .join(Room, Booking.room_id == Room.id)\
            .join(RoomType, Room.room_type_id == RoomType.id)\
            .options(
                db.joinedload(Booking.user),
                db.joinedload(Booking.room).joinedload(Room.room_type),
                db.load_only(
                    Booking.id, Booking.check_in_date, Booking.check_out_date,
                    Booking.total_price, Booking.status, Booking.payment_method,
                    Booking.payment_reference, Booking.payment_screenshot
                )
            )\
            .order_by(Booking.check_out_date.desc()).all()
        
        rejected_bookings = Booking.query.filter_by(status='rejected')\
            .join(User, Booking.user_id == User.id)\
            .join(Room, Booking.room_id == Room.id)\
            .join(RoomType, Room.room_type_id == RoomType.id)\
            .options(
                db.joinedload(Booking.user),
                db.joinedload(Booking.room).joinedload(Room.room_type),
                db.joinedload(Booking.rejected_by_user),
                db.load_only(
                    Booking.id, Booking.check_in_date, Booking.check_out_date,
                    Booking.total_price, Booking.status, Booking.payment_method,
                    Booking.payment_reference, Booking.payment_screenshot
                )
            )\
            .order_by(Booking.rejected_at.desc()).all()
        
        cancelled_bookings = Booking.query.filter_by(status='cancelled')\
            .join(User, Booking.user_id == User.id)\
            .join(Room, Booking.room_id == Room.id)\
            .join(RoomType, Room.room_type_id == RoomType.id)\
            .options(
                db.joinedload(Booking.user),
                db.joinedload(Booking.room).joinedload(Room.room_type),
                db.load_only(
                    Booking.id, Booking.check_in_date, Booking.check_out_date,
                    Booking.total_price, Booking.status, Booking.payment_method,
                    Booking.payment_reference, Booking.payment_screenshot
                )
            )\
            .order_by(Booking.created_at.desc()).all()
        
        return render_template('admin/bookings.html', 
                             pending_bookings=pending_bookings,
                             approved_bookings=approved_bookings,
                             completed_bookings=completed_bookings,
                             rejected_bookings=rejected_bookings,
                             cancelled_bookings=cancelled_bookings)
                             
    except Exception as e:
        print(f"Error loading bookings: {str(e)}")
        flash('Error loading bookings. Please try again.', 'danger')
        return redirect(url_for('admin_dashboard'))


# Lightweight updates API for admin bookings (polling)
@app.route('/api/admin/bookings/updates')
@login_required
@admin_required
def admin_bookings_updates():
    try:
        status = request.args.get('status', 'pending')
        after_id = request.args.get('after_id', type=int)
        since = request.args.get('since')

        query = Booking.query
        if status:
            query = query.filter(Booking.status == status)

        if after_id:
            query = query.filter(Booking.id > after_id)
        elif since:
            try:
                from datetime import datetime
                since_dt = datetime.fromisoformat(since)
                query = query.filter(Booking.created_at > since_dt)
            except Exception:
                pass

        query = query.join(User, Booking.user_id == User.id)\
            .join(Room, Booking.room_id == Room.id)\
            .join(RoomType, Room.room_type_id == RoomType.id)\
            .options(
                db.joinedload(Booking.user),
                db.joinedload(Booking.room).joinedload(Room.room_type)
            )\
            .order_by(Booking.created_at.desc())\
            .limit(20)

        def serialize(b: Booking):
            return {
                'id': b.id,
                'guest_name': b.user.name if b.user else '',
                'room_number': b.room.room_number if b.room else '',
                'room_type': b.room.room_type.name if b.room and b.room.room_type else '',
                'num_guests': b.num_guests,
                'check_in_date': b.check_in_date.strftime('%Y-%m-%d') if b.check_in_date else '',
                'check_out_date': b.check_out_date.strftime('%Y-%m-%d') if b.check_out_date else '',
                'total_price': float(b.total_price) if b.total_price is not None else 0.0,
                'status': b.status,
                'payment_method': b.payment_method,
                'payment_reference': b.payment_reference,
                'payment_screenshot': b.payment_screenshot,
                'created_at': b.created_at.isoformat() if b.created_at else None
            }

        bookings = [serialize(b) for b in query.all()]
        return jsonify({ 'success': True, 'status': status, 'bookings': bookings })
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500

@app.route('/admin/bookings/<int:booking_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Update booking status
        booking.status = 'approved'  # Changed from 'confirmed' to 'approved'
        booking.approved_by = current_user.id
        booking.approved_at = datetime.utcnow()
        
        # Calculate rates including selected amenities
        nights = (booking.check_out_date - booking.check_in_date).days
        price_per_night = booking.room.room_type.price_per_night
        amenities_total = 0.0
        try:
            for amenity in getattr(booking, 'selected_amenities', []) or []:
                amenities_total += float(getattr(amenity, 'additional_cost', 0) or 0) * nights
        except Exception:
            amenities_total = 0.0
        total_price = nights * price_per_night + amenities_total
        
        # Update total price in booking
        booking.total_price = total_price

        # Reject and notify other pending bookings for the same room and overlapping dates
        overlapping_pending = Booking.query.filter(
            Booking.room_id == booking.room_id,
            Booking.status == 'pending',
            Booking.id != booking.id,
            Booking.check_in_date < booking.check_out_date,
            Booking.check_out_date > booking.check_in_date
        ).all()
        for other in overlapping_pending:
            other.status = 'rejected'
            db.session.flush()
            create_notification(
                user_id=other.user_id,
                title='Booking Rejected',
                message=f'Your booking for Room {booking.room.room_number} from {other.check_in_date} to {other.check_out_date} was rejected because the room was booked by another guest.',
                type='booking'
            )
        
        db.session.commit()
        
        # Create notification for the approval
        create_booking_notification(booking, 'approved')
        
        # Show rates in flash message
        if amenities_total > 0:
            flash(f'Booking approved. Room: ₱{price_per_night:,.2f}/night × {nights} nights; Amenities: ₱{amenities_total:,.2f}; Total: ₱{total_price:,.2f}', 'success')
        else:
            flash(f'Booking approved. Rate: ₱{price_per_night:,.2f}/night × {nights} nights = Total: ₱{total_price:,.2f}', 'success')
        return redirect(url_for('admin_bookings'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while approving the booking.', 'error')
        return redirect(url_for('admin_bookings'))

@app.route('/admin/bookings/<int:booking_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Update booking status
        booking.status = 'rejected'
        booking.rejected_by = current_user.id
        booking.rejected_at = datetime.utcnow()
        # Save rejection reason
        reason = request.form.get('reason')
        if reason:
            # Primary field
            booking.rejection_reason = reason
            # Backward-compat: also populate cancellation_reason if column exists
            try:
                # Some databases may not yet have the new column applied
                booking.cancellation_reason = reason
            except Exception:
                pass
        db.session.commit()
        
        # Create notification for the rejection
        create_booking_notification(booking, 'rejected')
        
        flash('Booking rejected successfully.', 'success')
        return redirect(url_for('admin_bookings'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while rejecting the booking.', 'error')
        return redirect(url_for('admin_bookings'))

@app.route('/admin/room-types/<int:room_type_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_room_type(room_type_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    room_type = RoomType.query.get_or_404(room_type_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price_per_night'))
            
            # Validate price
            if price < 0:
                flash('Price cannot be negative', 'danger')
                return render_template('admin/edit_room_type.html', room_type=room_type)
                
            if price > 50000:
                flash('Price cannot exceed ₱50,000', 'danger')
                return render_template('admin/edit_room_type.html', room_type=room_type)
            
            # Word count validation
            if len(name.split()) > 20:
                flash('Name cannot exceed 20 words', 'danger')
                return render_template('admin/edit_room_type.html', room_type=room_type)
                
            if len(description.split()) > 100:
                flash('Description cannot exceed 100 words', 'danger')
                return render_template('admin/edit_room_type.html', room_type=room_type)
            
            # Repeated characters validation
            import re
            if re.search(r'(.)\1{4,}', name):
                flash('Name contains too many repeated characters', 'danger')
                return render_template('admin/edit_room_type.html', room_type=room_type)
                
            if re.search(r'(.)\1{4,}', description):
                flash('Description contains too many repeated characters', 'danger')
                return render_template('admin/edit_room_type.html', room_type=room_type)
            
            # Update room type
            room_type.name = name
            room_type.description = description
            room_type.price_per_night = price
            
            db.session.commit()
            flash('Room type updated successfully!', 'success')
            return redirect(url_for('admin_rooms'))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('admin/edit_room_type.html', room_type=room_type)
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('admin/edit_room_type.html', room_type=room_type)
    
    return render_template('admin/edit_room_type.html', room_type=room_type)

@app.route('/admin/room-types/<int:room_type_id>', methods=['DELETE'])
@login_required
def admin_delete_room_type(room_type_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    try:
        room_type = RoomType.query.get_or_404(room_type_id)
        
        # Check if there are any rooms of this type
        if room_type.rooms:
            return jsonify({
                'success': False, 
                'message': 'Cannot delete room type that has rooms assigned to it'
            }), 400
        
        db.session.delete(room_type)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/room-types/add', methods=['POST'])
@login_required
def admin_add_room_type():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price_per_night'))
        
        # Validate price
        if price < 0:
            flash('Price cannot be negative', 'danger')
            return redirect(url_for('admin_rooms'))
            
        if price > 50000:
            flash('Price cannot exceed ₱50,000', 'danger')
            return redirect(url_for('admin_rooms'))
        
        # Word count validation
        if len(name.split()) > 20:
            flash('Name cannot exceed 20 words', 'danger')
            return redirect(url_for('admin_rooms'))
            
        if len(description.split()) > 100:
            flash('Description cannot exceed 100 words', 'danger')
            return redirect(url_for('admin_rooms'))
        
        # Repeated characters validation
        import re
        if re.search(r'(.)\1{4,}', name):
            flash('Name contains too many repeated characters', 'danger')
            return redirect(url_for('admin_rooms'))
            
        if re.search(r'(.)\1{4,}', description):
            flash('Description contains too many repeated characters', 'danger')
            return redirect(url_for('admin_rooms'))
        
        room_type = RoomType(
            name=name,
            description=description,
            price_per_night=price
        )
        db.session.add(room_type)
        db.session.commit()
        
        flash('Room type added successfully!', 'success')
        return redirect(url_for('admin_rooms'))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('admin_rooms'))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin_rooms'))

@app.route('/admin/room-types/<int:room_type_id>')
@login_required
def admin_view_room_type(room_type_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    room_type = RoomType.query.get_or_404(room_type_id)
    # Get all rooms of this type
    rooms = Room.query.filter_by(room_type_id=room_type_id).all()
    
    return render_template('admin/view_room_type.html', room_type=room_type, rooms=rooms)

@app.route('/admin/rooms/<int:room_id>')
@login_required
def admin_view_room(room_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    room = Room.query.get_or_404(room_id)
    # Get booking history for this room with all relationships loaded
    bookings = Booking.query.filter_by(room_id=room_id)\
        .join(User, Booking.user_id == User.id)\
        .options(
            db.joinedload(Booking.user),
            db.joinedload(Booking.approved_by_user),
            db.joinedload(Booking.rejected_by_user)
        )\
        .order_by(Booking.check_in_date.desc()).all()
    
    return render_template('admin/view_room.html', room=room, bookings=bookings)

@app.route('/admin/rooms/<int:room_id>', methods=['DELETE'])
@login_required
@admin_required
def admin_delete_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        
        # Check if room has ANY bookings (not just active ones)
        bookings = Booking.query.filter_by(room_id=room_id).first()
            
        if bookings:
            return jsonify({
                'success': False,
                'message': 'Cannot delete room that has bookings. You must delete all bookings for this room first.'
            }), 400
        
        # Delete the room's image if it exists
        if room.image:
            image_path = os.path.join(app.static_folder, room.image)
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error deleting room image: {e}")
        
        # Delete the room
        db.session.delete(room)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Room deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete room: {str(e)}'
        }), 500

@app.route('/admin/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_room(room_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    room = Room.query.get_or_404(room_id)
    room_types = RoomType.query.all()
    amenities = Amenity.query.all()
    
    if request.method == 'POST':
        try:
            room.room_number = request.form.get('room_number')
            room.room_type_id = int(request.form.get('room_type_id'))
            room.floor = int(request.form.get('floor'))
            room.occupancy_limit = int(request.form.get('occupancy_limit'))
            
            # Fix for availability toggle
            room.is_available = request.form.get('is_available') == 'true'
            
            # Handle image upload if provided
            if 'image' in request.files:
                image = request.files['image']
                if image.filename:
                    # Delete old image if it exists
                    if room.image:
                        old_image_path = os.path.join(app.static_folder, room.image.replace('/', os.path.sep))
                        try:
                            if os.path.exists(old_image_path):
                                os.remove(old_image_path)
                        except Exception as e:
                            print(f"Error deleting old image: {e}")
                    
                    # Generate unique filename with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"room_{timestamp}_{secure_filename(image.filename)}"
                    # Use forward slashes for URL compatibility
                    room.image = f'room_images/{filename}'
                    # Ensure upload directory exists
                    upload_path = os.path.join(app.static_folder, 'room_images')
                    os.makedirs(upload_path, exist_ok=True)
                    # Save the new image
                    image.save(os.path.join(upload_path, filename))
                    print(f"Updated image saved to: {os.path.join(upload_path, filename)}")
                    print(f"Updated image path stored in database: {room.image}")
            
            # Update amenities
            selected_amenities = request.form.getlist('amenities')
            # Clear existing amenities
            room.amenities = []
            # Add selected amenities
            for amenity_id in selected_amenities:
                amenity = Amenity.query.get(int(amenity_id))
                if amenity:
                    room.amenities.append(amenity)
            
            db.session.commit()
            flash('Room updated successfully', 'success')
            return redirect(url_for('admin_rooms'))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to update room: {str(e)}', 'danger')
    
    # Get current amenities for the room
    current_amenities = [a.id for a in room.amenities]
    
    return render_template('admin/edit_room.html', 
                         room=room, 
                         room_types=room_types,
                         amenities=amenities,
                         current_amenities=current_amenities)

@app.route('/admin/amenities/add', methods=['POST'])
def add_amenity():
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
        
    try:
        name = request.form['name']
        description = request.form['description']
        icon = request.form['icon']
        additional_cost = float(request.form['additional_cost'])
        
        if additional_cost < 0:
            return jsonify({'success': False, 'message': 'Additional cost cannot be negative'}), 400
            
        if additional_cost > 20000:
            return jsonify({'success': False, 'message': 'Additional cost cannot exceed ₱20,000'}), 400
            
        amenity = Amenity(
            name=name,
            description=description,
            icon=icon,
            additional_cost=additional_cost
        )
        
        db.session.add(amenity)
        db.session.commit()
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Amenity added successfully'})
        
        flash('Amenity added successfully', 'success')
        return redirect(url_for('admin_amenities'))
        
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 400
        
        flash('Error adding amenity: ' + str(e), 'error')
        return redirect(url_for('admin_amenities'))

# Static page routes
@app.route('/accommodations')
def accommodations():
    return redirect(url_for('rooms'))

@app.route('/amenities')
def amenities():
    # You could fetch amenities from the database if needed
    return render_template('amenities.html')

@app.route('/special-offers')
def special_offers():
    today = datetime.now().date()
    promos = Promo.query.filter(
        Promo.is_active == True,
        Promo.start_date <= today,
        Promo.end_date >= today
    ).order_by(Promo.start_date.desc()).all()
    return render_template('special_offers.html', promos=promos)

UPLOAD_FOLDER = 'static/images/gallery'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/gallery')
def gallery():
    try:
        # Debug print to check if we're hitting this route
        print("Accessing gallery route")
        
        # Get all gallery images
        gallery_images = GalleryImage.query.all()
        
        # Debug print to see what we got from the database
        print(f"Found {len(gallery_images)} images")
        for img in gallery_images:
            print(f"Image: {img.filename}, Title: {img.title}")
            # Check if file exists
            filepath = os.path.join('static', 'images', 'gallery', img.filename)
            print(f"File exists: {os.path.exists(filepath)}")
        
        return render_template('gallery.html', gallery_images=gallery_images)
    except Exception as e:
        import traceback
        print("Error in gallery route:")
        print(traceback.format_exc())
        flash('Error loading gallery images', 'error')
        return render_template('gallery.html', gallery_images=[])

@app.route('/admin/gallery')
@login_required
@admin_required
def admin_gallery():
    gallery_images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    return render_template('admin/gallery.html', gallery_images=gallery_images)

@app.route('/admin/gallery/add', methods=['POST'])
@login_required
@admin_required
def admin_add_gallery_image():
    if 'image' not in request.files:
        flash('No image file', 'error')
        return redirect(url_for('admin_gallery'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('admin_gallery'))
    
    if file and allowed_file(file.filename):
        # Create a unique filename using timestamp
        filename = secure_filename(file.filename)
        filename = f"{int(time.time())}_{filename}"
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save the file
        file.save(os.path.join(app.root_path, UPLOAD_FOLDER, filename))
        
        # Create new gallery image record
        new_image = GalleryImage(
            filename=filename,
            title=request.form['title'],
            description=request.form['description'],
            category=request.form['category']
        )
        
        try:
            db.session.add(new_image)
            db.session.commit()
            flash('Image added successfully', 'success')
        except Exception as e:
            db.session.rollback()
            # Delete the uploaded file if database insert fails
            os.remove(os.path.join(app.root_path, UPLOAD_FOLDER, filename))
            flash(f'Error adding image: {str(e)}', 'error')
        
        return redirect(url_for('admin_gallery'))

    flash('Invalid file type', 'error')
    return redirect(url_for('admin_gallery'))

@app.route('/admin/gallery/<int:image_id>', methods=['DELETE'])
@login_required
@admin_required
def admin_delete_gallery_image(image_id):
    image = GalleryImage.query.get_or_404(image_id)
    
    try:
        os.remove(os.path.join(app.root_path, UPLOAD_FOLDER, image.filename))
    except:
        pass
    
    db.session.delete(image)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin/gallery/<int:image_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_gallery_image(image_id):
    image = GalleryImage.query.get_or_404(image_id)
    
    try:
        # Update basic info
        image.title = request.form.get('title')
        image.description = request.form.get('description')
        image.category = request.form.get('category')
        
        # Handle new image if uploaded
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Delete old image
                try:
                    old_image_path = os.path.join(app.root_path, UPLOAD_FOLDER, image.filename)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                except Exception as e:
                    print(f"Error deleting old image: {e}")
                
                # Create a unique filename using timestamp
                filename = secure_filename(file.filename)
                filename = f"{int(time.time())}_{filename}"
                
                # Save new image
                file.save(os.path.join(app.root_path, UPLOAD_FOLDER, filename))
                image.filename = filename
        
        db.session.commit()
        flash('Gallery image updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating image: {str(e)}', 'error')
    
    return redirect(url_for('admin_gallery'))

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    # Clear any existing session data related to password reset only on GET request
    if request.method == 'GET':
        session.pop('password_reset_verification', None)

    if request.method == 'POST':
        try:
            if 'email' in request.form:
                # Handle email submission
                email = request.form.get('email').lower()
                user = User.query.filter_by(email=email).first()
                
                if not user:
                    flash('Email not found.', 'danger')
                    return render_template('auth/forgot_password.html')
                
                # Generate 6-digit verification code
                verification_code = ''.join(random.choices(string.digits, k=6))
                
                # Store verification data in session
                session['password_reset_verification'] = {
                    'email': email,
                    'code': verification_code,
                    'timestamp': datetime.now().timestamp(),
                    'attempts': 0
                }
                
                # Send verification email
                if send_verification_email(email, verification_code):
                    flash('A verification code has been sent to your email.', 'info')
                else:
                    flash('Failed to send verification code. Please try again.', 'danger')
                    return render_template('auth/forgot_password.html')
            
            elif 'code' in request.form:
                # Handle verification code submission
                code = request.form.get('code')
                verification_data = session.get('password_reset_verification')
                
                if not verification_data:
                    flash('Verification session expired. Please request a new code.', 'danger')
                    return redirect(url_for('forgot_password'))
                
                # Check if code has expired (5 minutes)
                timestamp = datetime.fromtimestamp(verification_data['timestamp'])
                if datetime.now() - timestamp > timedelta(minutes=5):
                    session.pop('password_reset_verification', None)
                    flash('Verification code has expired. Please request a new code.', 'danger')
                    return redirect(url_for('forgot_password'))
                
                # Check if code matches
                if verification_data['code'] == code:
                    return redirect(url_for('reset_password'))
                else:
                    verification_data['attempts'] += 1
                    if verification_data['attempts'] >= 3:
                        session.pop('password_reset_verification', None)
                        flash('Too many incorrect attempts. Please request a new code.', 'danger')
                        return redirect(url_for('forgot_password'))
                    flash(f'Invalid verification code. {3 - verification_data["attempts"]} attempts remaining.', 'danger')
        
        except Exception as e:
            flash('An error occurred. Please try again.', 'danger')
            print(f"Password reset error: {str(e)}")
    
    return render_template('auth/forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    # Check if user has verified their email
    verification_data = session.get('password_reset_verification')
    
    # If no verification data exists or if accessed directly through URL, redirect to home
    if not verification_data:
       
        return redirect(url_for('index'))

    # Check if verification has expired (5 minutes)
    timestamp = datetime.fromtimestamp(verification_data['timestamp'])
    if datetime.now() - timestamp > timedelta(minutes=5):
        session.pop('password_reset_verification', None)
        flash('Your verification has expired. Please start the password reset process again.', 'danger')
        return redirect(url_for('forgot_password'))
    
    # Check if the verification code was actually verified
    if not verification_data.get('verified', False):
        flash('Please verify your email with the OTP code first.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        try:
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate password match
            if new_password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('auth/reset_password.html')
            
            # Validate password length
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return render_template('auth/reset_password.html')
            
            # Validate password contains at least one number and one letter
            if not (any(c.isdigit() for c in new_password) and any(c.isalpha() for c in new_password)):
                flash('Password must contain at least one number and one letter.', 'danger')
                return render_template('auth/reset_password.html')
            
            # Get user and update password
            email = verification_data['email']
            user = User.query.filter_by(email=email).first()
            
            if not user:
                flash('User not found. Please try the password reset process again.', 'danger')
                return redirect(url_for('forgot_password'))
            
            # Update password using the set_password method
            user.set_password(new_password)
            db.session.commit()
            
            # Clear the reset verification session
            session.pop('password_reset_verification', None)
            
            flash('Your password has been reset successfully. You can now login with your new password.', 'success')
            return redirect(url_for('user_login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while resetting your password. Please try again.', 'danger')
            return render_template('auth/reset_password.html')
            
    return render_template('auth/reset_password.html')

@app.route('/debug/check-admin')
def check_admin():
    admin = User.query.filter_by(email='admin@example.com').first()
    if admin:
        return {
            'exists': True,
            'name': admin.name,
            'email': admin.email,
            'is_admin': admin.is_admin,
            'password_check': check_password_hash(admin.password, 'admin123')
        }
    return {'exists': False}

@app.route('/debug/reset-admin')
def reset_admin():
    try:
        from werkzeug.security import generate_password_hash
        # First, try to find existing admin
        admin = User.query.filter_by(email='admin@example.com').first()
        
        if admin:
            # Update existing admin password
            admin.password = generate_password_hash('admin123', method='pbkdf2:sha256')
        else:
            # Create new admin user
            admin = User(
                name='Administrator',
                email='admin@example.com',
                phone='+1234567890',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                is_admin=True
            )
            db.session.add(admin)
        
        db.session.commit()
        
        # Verify the password hash
        verify = check_password_hash(admin.password, 'admin123')
        
        return {
            'success': True,
            'admin_id': admin.id,
            'admin_email': admin.email,
            'is_admin': admin.is_admin,
            'password_verify': verify,
            'password_hash': admin.password
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/admin/users/<int:user_id>')
@login_required
@admin_required
def get_user_details(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
            'registration_status': user.registration_status,
            'id_type': user.id_type,
            'id_picture': user.id_picture,
            'created_at': format_datetime(user.created_at)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/users/<int:user_id>/delete', methods=['POST', 'DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        return {'success': False, 'message': 'Cannot delete admin user.'}, 400
    try:
        # Delete the user - cascade options will handle related records
        db.session.delete(user)
        db.session.commit()
        return {'success': True, 'message': 'User deleted successfully.'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500

@app.route('/admin/users')
@login_required
def admin_users():
    """Admin users management view"""
    if not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Get all non-admin users with their bookings
        users = User.query.filter_by(is_admin=False).all()
        
        # Calculate statistics
        total_users = len(users)
        total_bookings = sum(len(user.bookings) for user in users)
        
        return render_template('admin/users.html',
                             users=users,
                             total_users=total_users,
                             total_bookings=total_bookings)
    except Exception as e:
        print(f"Error loading users: {str(e)}")
        flash('Error loading users', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/users/<int:user_id>/read')
@login_required
def read_user(user_id):
    """Get user details for viewing"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        recent_bookings = Booking.query\
            .filter_by(user_id=user_id)\
            .join(Room, Booking.room_id == Room.id)\
            .join(RoomType, Room.room_type_id == RoomType.id)\
            .order_by(Booking.created_at.desc())\
            .limit(5)\
            .all()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'registration_status': user.registration_status,
                'id_type': user.id_type,
                'id_picture': user.id_picture,
                'total_bookings': len(user.bookings),
                'join_date': user.created_at.strftime('%Y-%m-%d') if user.created_at else 'N/A',
                'booking_history': [{
                    'room_number': booking.room.room_number,
                    'room_type': booking.room.room_type.name,
                    'check_in': booking.check_in_date.strftime('%Y-%m-%d'),
                    'check_out': booking.check_out_date.strftime('%Y-%m-%d'),
                    'status': booking.status,
                    'total_price': float(booking.total_price)
                } for booking in recent_bookings]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/users/<int:user_id>/update', methods=['POST'])
@login_required
def update_user(user_id):
    """Update user details"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Update user details
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        user.phone = data.get('phone', user.phone)
        
        # Update password if provided
        if 'new_password' in data and data['new_password']:
            user.set_password(data['new_password'])
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'User updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/debug/check-auth')
def check_auth():
    if current_user.is_authenticated:
        return {
            'authenticated': True,
            'is_admin': current_user.is_admin,
            'user_id': current_user.id,
            'email': current_user.email
        }
    return {'authenticated': False}

@app.route('/admin/profile')
@login_required
@admin_required
def admin_profile():
    return render_template('admin/profile.html')

@app.route('/admin/profile/update', methods=['POST'])
@login_required
@admin_required
def admin_update_profile():
    try:
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                if allowed_file(file.filename):
                    # Delete old profile picture if it exists
                    if current_user.profile_pic:
                        old_pic_path = os.path.join(app.root_path, 'static', current_user.profile_pic)
                        try:
                            if os.path.exists(old_pic_path):
                                os.remove(old_pic_path)
                        except Exception as e:
                            print(f"Error deleting old profile picture: {e}")

                    # Generate unique filename
                    filename = secure_filename(file.filename)
                    unique_filename = f"profile_{current_user.id}_{int(time.time())}_{filename}"
                    
                    # Save the new profile picture
                    save_path = os.path.join(app.root_path, PROFILE_UPLOAD_FOLDER, unique_filename)
                    file.save(save_path)
                    
                    # Update user's profile picture in database - store relative path
                    current_user.profile_pic = f"images/profiles/{unique_filename}"
                else:
                    flash('Invalid file type. Please upload an image file (png, jpg, jpeg, gif).', 'danger')
                    return redirect(url_for('admin_profile'))

        # Update other profile information
        current_user.name = request.form.get('name')
        current_user.email = request.form.get('email')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while updating your profile: {str(e)}', 'error')
    
    return redirect(url_for('admin_profile'))

@app.route('/admin/profile/change-password', methods=['POST'])
@login_required
@admin_required
def admin_change_password():
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password:
            flash('Current password is required.', 'danger')
            return redirect(url_for('admin_profile'))
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('admin_profile'))
        
        if not new_password:
            flash('New password is required.', 'danger')
            return redirect(url_for('admin_profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('admin_profile'))
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        # Re-login the user with new password
        login_user(current_user)
        
        flash('Password changed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while changing your password: {str(e)}', 'error')
    
    return redirect(url_for('admin_profile'))

# Add a route to handle comment deletion by admin
@app.route('/admin/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        
        # Get the room_id before deleting the comment for recalculating average rating
        booking = Booking.query.get(comment.booking_id)
        room_id = booking.room_id if booking else None
        
        # Delete the comment
        db.session.delete(comment)
        db.session.commit()
        
        # If we have the room_id, recalculate average rating
        if room_id:
            # Get all comments for this room through bookings
            room_comments = Comment.query.join(Booking).filter(Booking.room_id == room_id).all()
            # Calculate new average rating
            avg_rating = sum(c.rating for c in room_comments) / len(room_comments) if room_comments else 0
            
        return jsonify({
            'success': True,
            'message': 'Comment deleted successfully',
            'new_avg_rating': round(avg_rating, 1) if room_id else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/admin/comments')
@login_required
@admin_required
def admin_comments():
    """Admin comments management view"""
    try:
        # Get all comments with related data
        comments = (Comment.query
            .join(User, Comment.user_id == User.id)
            .join(Booking, Comment.booking_id == Booking.id)
            .join(Room, Booking.room_id == Room.id)
            .join(RoomType, Room.room_type_id == RoomType.id)
            .options(
                db.joinedload(Comment.author),
                db.joinedload(Comment.booking).joinedload(Booking.room).joinedload(Room.room_type)
            )
            .order_by(Comment.created_at.desc())
            .all())
        
        return render_template('admin/comments.html', comments=comments)
    except Exception as e:
        print(f"Error loading comments: {str(e)}")
        flash('Error loading comments', 'error')
        return redirect(url_for('admin_dashboard'))

# Print available routes
print("Available routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")


@app.after_request
def add_cache_control_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response 

def send_verification_email(email, code):
    try:
        msg = Message(
            subject='Password Reset Verification Code - FAWNA Hotel',
            recipients=[email],
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        msg.html = render_template('auth/email/reset_password_code.html', code=code)
        
        # Use async email sending to prevent timeouts
        from utils.email_utils import send_email_async
        send_email_async(mail, msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def handle_expired_bookings():
    """Check and update status of expired bookings"""
    try:
        current_date = datetime.now().date()
        # Find all approved bookings that have passed their check-out date
        expired_bookings = Booking.query.filter(
            Booking.status == 'approved',
            Booking.check_out_date < current_date
        ).all()
        
        for booking in expired_bookings:
            booking.status = 'completed'
            # Make the room available again
            if booking.room:
                booking.room.is_available = True
        
        if expired_bookings:
            db.session.commit()
            print(f"Updated {len(expired_bookings)} expired bookings to completed status")
    except Exception as e:
        print(f"Error handling expired bookings: {e}")
        db.session.rollback()

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/notifications-page')
@login_required
def notifications_page():
    """Render the notifications page"""
    return render_template('notifications.html')

@app.route('/notifications')
@login_required
def get_notifications():
    """Get user's notifications with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    
    notifications = get_user_notifications(current_user.id, limit=per_page, offset=offset)
    unread_count = get_unread_notifications_count(current_user.id)
    
    return jsonify({
        'notifications': notifications,
        'unread_count': unread_count
    })

@app.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    success = mark_notification_as_read(notification_id, current_user.id)
    return jsonify({'success': success})

@app.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read for the current user"""
    success = mark_all_notifications_as_read(current_user.id)
    return jsonify({'success': success})

@app.route('/notifications/unread-count')
@login_required
def get_unread_count():
    """Get the count of unread notifications"""
    count = get_unread_notifications_count(current_user.id)
    return jsonify({'count': count})

@app.route('/notifications/clear-all', methods=['POST'])
@login_required
def clear_all_notifications():
    """Clear all notifications for the current user"""
    try:
        Notification.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/bookings/create', methods=['POST'])
@login_required
def create_booking():
    try:
        # Get form data
        room_id = request.form.get('room_id')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        num_guests = request.form.get('num_guests', 1, type=int)
        payment_method = request.form.get('payment_method')
        total_price = request.form.get('total_price', type=float)
        selected_amenity_ids = request.form.getlist('amenities')

        # Prevent duplicate/overlapping bookings for the same user, room, and date range
        overlapping = Booking.query.filter(
            Booking.user_id == current_user.id,
            Booking.room_id == room_id,
            Booking.status.in_(['pending', 'approved']),
            Booking.check_in_date < datetime.strptime(check_out, '%Y-%m-%d').date(),
            Booking.check_out_date > datetime.strptime(check_in, '%Y-%m-%d').date()
        ).first()
        if overlapping:
            return jsonify({'error': 'You already have a pending or approved booking for this room and date range.'}), 400

        # Validate required fields
        if not all([room_id, check_in, check_out, payment_method, total_price]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Create booking object
        booking = Booking(
            user_id=current_user.id,
            room_id=room_id,
            check_in_date=datetime.strptime(check_in, '%Y-%m-%d').date(),
            check_out_date=datetime.strptime(check_out, '%Y-%m-%d').date(),
            num_guests=num_guests,
            total_price=total_price,
            payment_method=payment_method
        )

        # Add selected amenities
        if selected_amenity_ids:
            for amenity_id in selected_amenity_ids:
                amenity = Amenity.query.get(int(amenity_id))
                if amenity:
                    booking.selected_amenities.append(amenity)

        # Handle payment methods with proof (GCash, PayMaya or general QR payment)
        if payment_method in ['gcash', 'paymaya', 'qr_payment']:
            # Get payment app type and details
            payment_app = request.form.get('payment_app', payment_method)
            reference = request.form.get('payment_reference')
            screenshot = request.files.get('payment_screenshot')
            
            if not reference or not screenshot:
                return jsonify({'error': 'Payment reference number and screenshot are required'}), 400
            
            if screenshot and allowed_file(screenshot.filename):
                # Create payment screenshots directory if it doesn't exist
                screenshots_dir = os.path.join(app.root_path, 'static', 'payment_screenshots')
                os.makedirs(screenshots_dir, exist_ok=True)
                
                # Save screenshot with unique filename
                filename = secure_filename(f"payment_{current_user.id}_{int(time.time())}_{screenshot.filename}")
                screenshot.save(os.path.join(screenshots_dir, filename))
                booking.payment_screenshot = f"payment_screenshots/{filename}"
                booking.payment_reference = reference
                
                # Set payment method based on the app selected
                if payment_app and payment_method == 'qr_payment':
                    booking.payment_method = payment_app
            else:
                return jsonify({'error': 'Invalid file format. Please upload an image file (png, jpg, jpeg, gif)'}), 400

        # Save booking
        try:
            db.session.add(booking)
            db.session.commit()
            
            # Create notification
            create_booking_notification(booking, 'created')
            
            return jsonify({
                'success': True,
                'message': 'Booking created successfully',
                'redirect': url_for('dashboard')
            })
        except Exception as e:
            db.session.rollback()
            # Clean up uploaded file if database commit fails
            if booking.payment_screenshot:
                try:
                    os.remove(os.path.join(app.root_path, 'static', booking.payment_screenshot))
                except:
                    pass
            return jsonify({'error': 'Database error occurred'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/booking-history')
@login_required
def booking_history():
    """Display user's booking history"""
    try:
        # Get all bookings for the current user with proper joins
        bookings = (Booking.query
            .filter_by(user_id=current_user.id)
            .join(Room, Booking.room_id == Room.id)
            .join(RoomType, Room.room_type_id == RoomType.id)
            .options(
                db.joinedload(Booking.room).joinedload(Room.room_type),
                db.joinedload(Booking.comments)
            )
            .order_by(Booking.created_at.desc())
            .all()
        )
        
        return render_template('booking_history.html', bookings=bookings)
    except Exception as e:
        print(f"Error loading booking history: {e}")
        flash("Error loading your booking history. Please try again later.", "error")
        return redirect(url_for('dashboard'))

# Add this new API endpoint to get booking info
@app.route('/api/booking-info/<string:room_number>')
@login_required
def get_booking_info(room_number):
    """Get booking information by room number for notifications"""
    try:
        # Find the room with this room number
        room = Room.query.filter_by(room_number=room_number).first()
        
        if not room:
            return jsonify({'success': False, 'error': 'Room not found'}), 404
            
        # Get the most recent booking for this room
        booking = Booking.query.filter_by(room_id=room.id)\
            .order_by(Booking.created_at.desc())\
            .first()
            
        if not booking:
            return jsonify({'success': False, 'error': 'No booking found for this room'}), 404
            
        return jsonify({
            'success': True,
            'booking_id': booking.id,
            'status': booking.status,
            'check_in': booking.check_in_date.strftime('%Y-%m-%d'),
            'check_out': booking.check_out_date.strftime('%Y-%m-%d')
        })
    except Exception as e:
        print(f"Error getting booking info: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/bookings/<int:booking_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_booking(booking_id):
    """Delete a booking from the admin interface"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Allow deletion of completed, cancelled, approved, and rejected bookings
        if booking.status not in ['completed', 'cancelled', 'approved', 'rejected']:
            return jsonify({
                'success': False, 
                'message': 'Only completed, cancelled, approved, or rejected bookings can be deleted'
            }), 400
        
        # Store necessary information before deleting
        user_id = booking.user_id
        room_number = booking.room.room_number
            
        # Delete associated comments first
        Comment.query.filter_by(booking_id=booking.id).delete()
        
        # Delete the booking
        db.session.delete(booking)
        db.session.commit()
        
        # Create notification for the user
        create_notification(
            user_id=user_id,
            title='Booking Deleted',
            message=f'Your booking for Room {room_number} has been deleted by an administrator.',
            type='booking'
        )
        
        return jsonify({
            'success': True,
            'message': 'Booking deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete booking: {str(e)}'
        }), 500

@app.route('/admin/bookings/<int:booking_id>/details')
@login_required
@admin_required
def get_booking_details(booking_id):
    """Get booking details as JSON for AJAX requests"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Create a JSON-friendly dictionary
        booking_data = {
            'id': booking.id,
            'guest_name': booking.user.name,
            'num_guests': booking.num_guests,
            'room_number': booking.room.room_number,
            'room_type': booking.room.room_type.name,
            'check_in_date': booking.check_in_date.strftime('%Y-%m-%d'),
            'check_out_date': booking.check_out_date.strftime('%Y-%m-%d'),
            'total_price': float(booking.total_price),
            'payment_method': booking.payment_method,
            'status': booking.status
        }
        
        return jsonify({
            'success': True,
            'booking': booking_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to load booking details: {str(e)}'
        }), 500

# User-facing booking details (includes cancel/reject reasons)
@app.route('/bookings/<int:booking_id>/details')
@login_required
def get_booking_details_user(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        # Ensure current user owns this booking unless admin
        if booking.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
            return jsonify({ 'success': False, 'message': 'Unauthorized' }), 403

        data = {
            'id': booking.id,
            'status': booking.status,
            'cancellation_reason': booking.cancellation_reason,
            'cancelled_at': booking.cancelled_at.strftime('%Y-%m-%d %H:%M:%S') if booking.cancelled_at else None,
            'rejection_reason': getattr(booking, 'rejection_reason', None),
            'rejected_at': booking.rejected_at.strftime('%Y-%m-%d %H:%M:%S') if booking.rejected_at else None,
        }
        return jsonify({ 'success': True, **data })
    except Exception as e:
        return jsonify({ 'success': False, 'message': f'Failed to load booking details: {str(e)}' }), 500

@app.route('/bookings/<int:booking_id>/receipt')
@login_required
def generate_receipt(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    # Allow access if the user is the booking owner or is an admin
    if (booking.status not in ['approved', 'completed']) or (booking.user_id != current_user.id and not getattr(current_user, 'is_admin', False)):
        flash('Receipt not available for this booking.', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculate nights and totals (room + amenities)
    nights = (booking.check_out_date - booking.check_in_date).days
    price_per_night = booking.room.room_type.price_per_night
    room_total = nights * price_per_night
    amenities_total = 0.0
    try:
        for amenity in getattr(booking, 'selected_amenities', []) or []:
            if amenity and getattr(amenity, 'additional_cost', 0):
                amenities_total += float(amenity.additional_cost) * nights
    except Exception:
        amenities_total = 0.0
    grand_total = room_total + amenities_total
    
    # Format dates
    check_in = booking.check_in_date.strftime('%B %d, %Y')
    check_out = booking.check_out_date.strftime('%B %d, %Y')
    booking_date = booking.created_at.strftime('%B %d, %Y')
    approval_date = booking.approved_at.strftime('%B %d, %Y')
    
    return render_template('receipt.html',
                         booking=booking,
                         nights=nights,
                         price_per_night=price_per_night,
                         total_price=grand_total,
                         room_total=room_total,
                         amenities_total=amenities_total,
                         check_in=check_in,
                         check_out=check_out,
                         booking_date=booking_date,
                         approval_date=approval_date)

@app.route('/admin/homepage-images', methods=['GET'])
@login_required
@admin_required
def admin_homepage_images():
    homepage_images = HomePageImage.query.order_by(HomePageImage.order, HomePageImage.created_at.desc()).all()
    settings = HomePageSettings.get_settings()
    return render_template('admin/homepage_images.html', homepage_images=homepage_images, carousel_interval=settings.carousel_interval)

@app.route('/admin/homepage-images/add', methods=['POST'])
@login_required
@admin_required
def admin_add_homepage_image():
    file = request.files.get('image')
    order = request.form.get('order', 0, type=int)
    if not file or not allowed_file(file.filename):
        flash('Invalid image file.', 'danger')
        return redirect(url_for('admin_homepage_images'))
    filename = secure_filename(file.filename)
    filename = f"{int(time.time())}_{filename}"
    os.makedirs(HOMEPAGE_UPLOAD_FOLDER, exist_ok=True)
    file.save(os.path.join(HOMEPAGE_UPLOAD_FOLDER, filename))
    img = HomePageImage(filename=filename, order=order)
    db.session.add(img)
    db.session.commit()
    flash('Homepage image added.', 'success')
    return redirect(url_for('admin_homepage_images'))

@app.route('/admin/homepage-images/<int:image_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_homepage_image(image_id):
    img = HomePageImage.query.get_or_404(image_id)
    # Update order if present
    if 'order' in request.form:
        img.order = request.form.get('order', 0, type=int)
    # Replace image if file uploaded
    if 'image' in request.files and request.files['image'].filename:
        file = request.files['image']
        if allowed_file(file.filename):
            # Delete old file
            old_path = os.path.join(HOMEPAGE_UPLOAD_FOLDER, img.filename)
            if os.path.exists(old_path):
                os.remove(old_path)
            filename = secure_filename(file.filename)
            filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(HOMEPAGE_UPLOAD_FOLDER, filename))
            img.filename = filename
    db.session.commit()
    flash('Homepage image updated.', 'success')
    return redirect(url_for('admin_homepage_images'))

@app.route('/admin/homepage-images/<int:image_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_homepage_image(image_id):
    img = HomePageImage.query.get_or_404(image_id)
    # Delete file
    file_path = os.path.join(HOMEPAGE_UPLOAD_FOLDER, img.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(img)
    db.session.commit()
    flash('Homepage image deleted.', 'success')
    return redirect(url_for('admin_homepage_images'))

HOMEPAGE_UPLOAD_FOLDER = os.path.join('static', 'images', 'homepage')

@app.route('/admin/homepage-settings', methods=['POST'])
@login_required
@admin_required
def admin_update_homepage_settings():
    interval = request.form.get('carousel_interval', type=int)
    settings = HomePageSettings.get_settings()
    if interval and interval > 0:
        settings.carousel_interval = interval
        db.session.commit()
        flash('Carousel interval updated.', 'success')
    else:
        flash('Invalid interval value.', 'danger')
    return redirect(url_for('admin_homepage_images'))

# Helper function to send emails asynchronously
def send_email_async(msg):
    try:
        from utils.email_utils import send_email_async as improved_send_email_async
        improved_send_email_async(mail, msg)
    except Exception as e:
        print(f"Error sending email: {str(e)}")

@app.route('/admin/users/approve/<int:user_id>')
@login_required
@admin_required
def approve_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if user.is_admin:
            return jsonify({'success': False, 'message': 'Cannot modify admin users'}), 400
            
        user.registration_status = 'approved'
        db.session.commit()
        
        # Create notification for user
        create_notification(
            user.id,
            'Account Approved',
            'Your account has been approved by the administrator.',
            'system'
        )

        # Send approval email asynchronously
        msg = Message(
            'FAWNA Hotel - Account Verified',
            recipients=[user.email]
        )
        msg.html = render_template(
            'auth/email/account_verified.html',
            user=user,
            login_url=url_for('user_login', _external=True)
        )
        
        # Send email in a background thread
        threading.Thread(target=send_email_async, args=(msg,)).start()
        
        return jsonify({'success': True, 'message': 'User approved successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error approving user: {str(e)}")
        return jsonify({'success': False, 'message': 'Error approving user'}), 500

@app.route('/admin/users/reject/<int:user_id>')
@login_required
@admin_required
def reject_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if user.is_admin:
            return jsonify({'success': False, 'message': 'Cannot modify admin users'}), 400
            
        user.registration_status = 'rejected'
        db.session.commit()
        
        # Create notification for user
        create_notification(
            user.id,
            'Account Rejected',
            'Your account registration has been rejected by the administrator.',
            'system'
        )

        # Send rejection email asynchronously
        msg = Message(
            'FAWNA Hotel - Account Registration Update',
            recipients=[user.email]
        )
        msg.html = render_template(
            'auth/email/account_rejected.html',
            user=user
        )
        
        # Send email in a background thread
        threading.Thread(target=send_email_async, args=(msg,)).start()
        
        return jsonify({'success': True, 'message': 'User rejected successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error rejecting user: {str(e)}")
        return jsonify({'success': False, 'message': 'Error rejecting user'}), 500

@app.route('/admin/promos')
@login_required
@admin_required
def admin_promos():
    promos = Promo.query.order_by(Promo.start_date.desc()).all()
    return render_template('admin/promos.html', promos=promos)

@app.route('/admin/promos/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_promo():
    from models import Room
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            is_active = 'is_active' in request.form
            discount_percentage = float(request.form.get('discount_percentage', 0))
            image = request.files.get('image')
            image_path = None
            if image and image.filename:
                filename = secure_filename(f"promo_{int(time.time())}_{image.filename}")
                upload_folder = os.path.join(app.static_folder, 'promos')
                os.makedirs(upload_folder, exist_ok=True)
                image.save(os.path.join(upload_folder, filename))
                image_path = f'promos/{filename}'
            room_ids = request.form.getlist('room_ids')
            rooms = Room.query.filter(Room.id.in_(room_ids)).all() if room_ids else []
            promo = Promo(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                is_active=is_active,
                discount_percentage=discount_percentage,
                image=image_path
            )
            promo.rooms = rooms
            db.session.add(promo)
            db.session.commit()
            flash('Promo added successfully!', 'success')
            return redirect(url_for('admin_promos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding promo: {str(e)}', 'danger')
    from models import Room
    all_rooms = Room.query.all()
    return render_template('admin/edit_promo.html', promo=None, all_rooms=all_rooms, selected_room_ids=[])

@app.route('/admin/promos/<int:promo_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_promo(promo_id):
    from models import Room
    promo = Promo.query.get_or_404(promo_id)
    if request.method == 'POST':
        try:
            promo.title = request.form['title']
            promo.description = request.form['description']
            promo.start_date = request.form['start_date']
            promo.end_date = request.form['end_date']
            promo.is_active = 'is_active' in request.form
            promo.discount_percentage = float(request.form.get('discount_percentage', 0))
            image = request.files.get('image')
            if image and image.filename:
                filename = secure_filename(f"promo_{int(time.time())}_{image.filename}")
                upload_folder = os.path.join(app.static_folder, 'promos')
                os.makedirs(upload_folder, exist_ok=True)
                image.save(os.path.join(upload_folder, filename))
                promo.image = f'promos/{filename}'
            room_ids = request.form.getlist('room_ids')
            promo.rooms = Room.query.filter(Room.id.in_(room_ids)).all() if room_ids else []
            db.session.commit()
            flash('Promo updated successfully!', 'success')
            return redirect(url_for('admin_promos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating promo: {str(e)}', 'danger')
    from models import Room
    all_rooms = Room.query.all()
    selected_room_ids = [room.id for room in promo.rooms]
    return render_template('admin/edit_promo.html', promo=promo, all_rooms=all_rooms, selected_room_ids=selected_room_ids)

@app.route('/admin/promos/<int:promo_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_promo(promo_id):
    promo = Promo.query.get_or_404(promo_id)
    try:
        db.session.delete(promo)
        db.session.commit()
        flash('Promo deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting promo: {str(e)}', 'danger')
    return redirect(url_for('admin_promos'))

@app.route('/promo/<int:promo_id>')
def promo_detail(promo_id):
    promo = Promo.query.get_or_404(promo_id)
    rooms = promo.rooms  # Only rooms this promo applies to
    return render_template('promo_detail.html', promo=promo, rooms=rooms)

@app.route('/api/health-check', methods=['HEAD', 'GET'])
def health_check():
    """Health check endpoint for connectivity testing"""
    return '', 200

@app.route('/api/food-menu', methods=['GET'])
def food_menu():
    menu = get_food_menu()
    return jsonify(menu)

@app.route('/api/order-food', methods=['POST'])
@login_required
def order_food():
    data = request.get_json()
    def get_value(val, fallback):
        return val if val and str(val).strip() else fallback
    full_name = get_value(data.get('full_name'), current_user.name)
    phone = get_value(data.get('phone'), current_user.phone)
    delivery_address = data.get('delivery_address')
    payment_method = data.get('payment_method')
    notes = data.get('notes', '')
    delivery_notes = data.get('delivery_notes', '')
    subtotal = data.get('subtotal')
    delivery_fee = data.get('delivery_fee')
    total_amount = data.get('total_amount')
    user_id = data.get('user_id') or current_user.id
    items = data.get('items')  # <-- Accept items from frontend

    from utils.food_service_api import send_order_to_checkout_php
    # Forward all required fields to the PHP API
    print('Order fields:', {
        'user_id': user_id,
        'full_name': full_name,
        'phone': phone,
        'delivery_address': delivery_address,
        'payment_method': payment_method,
        'notes': notes,
        'delivery_notes': delivery_notes,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total_amount': total_amount,
        'items': items  # <-- Log items for debugging
    })
    resp = send_order_to_checkout_php(
        user_id=user_id,
        full_name=full_name,
        phone=phone,
        delivery_address=delivery_address,
        payment_method=payment_method,
        notes=notes,
        delivery_notes=delivery_notes,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        items=items  # <-- Pass items to PHP
    )
    print('Order API response:', resp)  # Log for debugging
    if resp.get('success') and resp.get('order_id'):
        php_ip = current_app.config.get('FOOD_SERVICE_IPV4')
        redirect_url = f"http://{php_ip}/online-food-ordering/checkout.php?order_id={resp['order_id']}"
        return jsonify({'success': True, 'redirect_url': redirect_url})
    else:
        return jsonify({'success': False, 'message': resp.get('message', 'Order failed.')}), 400

@app.route('/api/user/approved-bookings')
@login_required
def get_user_approved_bookings():
    """Get approved bookings for the current user"""
    try:
        # Get approved bookings for the current user with room and room type info
        approved_bookings = (Booking.query
            .filter_by(user_id=current_user.id, status='approved')
            .join(Room, Booking.room_id == Room.id)
            .join(RoomType, Room.room_type_id == RoomType.id)
            .options(
                db.joinedload(Booking.room).joinedload(Room.room_type)
            )
            .all()
        )
        
        # Format the data for JSON response
        bookings_data = []
        for booking in approved_bookings:
            bookings_data.append({
                'id': booking.id,
                'room_number': booking.room.room_number,
                'room_type': booking.room.room_type.name
            })
        
        return jsonify({
            'success': True,
            'bookings': bookings_data
        })
        
    except Exception as e:
        print(f"Error fetching approved bookings: {e}")
        return jsonify({
            'success': False,
            'message': 'Error fetching approved bookings'
        }), 500

@app.route('/api/food-order-history')
@login_required
def food_order_history():
    user_id = current_user.id
    result = get_food_order_history(user_id)
    # Add has_rating and rating_id for each order
    if result and 'orders' in result:
        for order in result['orders']:
            rating_row = None
            with db.engine.connect() as conn:
                res = conn.execute("SELECT id FROM eatnrun_rating WHERE order_id = %s", (order['id'],))
                rating_row = res.fetchone()
            if rating_row:
                order['has_rating'] = True
                order['rating_id'] = rating_row[0]
            else:
                order['has_rating'] = False
                order['rating_id'] = None
    return jsonify(result)

@app.route('/api/cancel-food-order/<int:order_id>', methods=['POST'])
@login_required
def api_cancel_food_order(order_id):
    data = request.get_json()
    cancellation_reason = data.get('cancellation_reason') if data else None
    result = cancel_food_order(order_id, cancellation_reason)
    return jsonify(result)

@app.route('/api/delete-food-order/<int:order_id>', methods=['DELETE'])
@login_required
def api_delete_food_order(order_id):
    result = delete_food_order(order_id)
    return jsonify(result)

ratings_bp = Blueprint('food_ratings', __name__)



@app.route('/api/eatnrun-rating', methods=['GET'])
def get_eatnrun_rating():
    rating_id = request.args.get('id')
    if not rating_id:
        return jsonify({'success': False, 'error': 'Missing id'}), 400
    sql = "SELECT id, rating, comment FROM eatnrun_rating WHERE id = %s"
    result = None
    with db.engine.connect() as conn:
        res = conn.execute(sql, (rating_id,))
        row = res.fetchone()
        if row:
            result = {'id': row[0], 'rating': row[1], 'comment': row[2]}
    if result:
        return jsonify({'success': True, 'rating': result})
    else:
        return jsonify({'success': False, 'error': 'Not found'}), 404

@app.route('/api/eatnrun-rating', methods=['POST', 'PUT'])
def save_eatnrun_rating():
    data = request.json
    rating = data.get('rating')
    comment = data.get('comment')
    rating_id = data.get('id')
    order_id = data.get('order_id')
    if request.method == 'POST':
        sql = "INSERT INTO eatnrun_rating (order_id, rating, comment) VALUES (%s, %s, %s)"
        with db.engine.connect() as conn:
            conn.execute(sql, (order_id, rating, comment))
        return jsonify({'success': True, 'message': 'Rating added'})
    elif request.method == 'PUT':
        if not rating_id:
            return jsonify({'success': False, 'error': 'Missing id'}), 400
        sql = "UPDATE eatnrun_rating SET rating = %s, comment = %s WHERE id = %s"
        with db.engine.connect() as conn:
            conn.execute(sql, (rating, comment, rating_id))
        return jsonify({'success': True, 'message': 'Rating updated'})
    