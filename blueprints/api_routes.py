# api_routes.py
from flask import Blueprint, jsonify, request
from models import User, Room, Booking, db
from werkzeug.security import check_password_hash

api = Blueprint('api', __name__, url_prefix='/api')

# ✅ Login
@api.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful", "user_id": user.id})
    return jsonify({"message": "Invalid credentials"}), 401

# ✅ Get all rooms
@api.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    result = [
        {"id": r.id, "room_number": r.room_number, "floor": r.floor,
         "price": r.room_type.price_per_night, "is_available": r.is_available}
        for r in rooms
    ]
    return jsonify(result)

# ✅ Create booking
@api.route('/book', methods=['POST'])
def book():
    data = request.json
    booking = Booking(
        user_id=data['user_id'],
        room_id=data['room_id'],
        check_in_date=data['check_in_date'],
        check_out_date=data['check_out_date'],
        num_guests=data['num_guests'],
        total_price=data['total_price'],
        payment_method=data['payment_method']
    )
    db.session.add(booking)
    db.session.commit()
    return jsonify({"message": "Booking successful"})
