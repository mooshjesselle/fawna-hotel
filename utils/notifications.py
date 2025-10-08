from models import Notification, User
from utils.extensions import db
from datetime import datetime
from utils.datetime_utils import get_current_local_time

def create_notification(user_id, title, message, type='system'):
    """
    Create a new notification for a user.
    
    Args:
        user_id (int): The ID of the user to notify
        title (str): The notification title
        message (str): The notification message
        type (str): The type of notification (default: 'system')
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        created_at=datetime.utcnow()  # We store in UTC but will convert when displaying
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def create_booking_notification(booking, action):
    """
    Create notifications for both the user and admin when a booking action occurs.
    
    Args:
        booking (Booking): The booking object
        action (str): The action that occurred ('created', 'approved', 'rejected', 'cancelled')
    """
    # Get all admin users
    admin_users = User.query.filter_by(is_admin=True).all()
    
    # Create notification for the user
    guest_message = {
        'created': f'Your booking for Room {booking.room.room_number} has been submitted and is pending approval. (Booking ID: {booking.id})',
        'approved': f'Your booking for Room {booking.room.room_number} has been approved! (Booking ID: {booking.id})',
        'rejected': f'Your booking for Room {booking.room.room_number} has been rejected. (Booking ID: {booking.id})',
        'cancelled': f'Your booking for Room {booking.room.room_number} has been cancelled. (Booking ID: {booking.id})'
    }
    
    create_notification(
        user_id=booking.user_id,
        title=f'Booking {action.title()}',
        message=guest_message.get(action, f'Booking status updated (Booking ID: {booking.id})'),
        type='booking'
    )
    
    # Create notification for all admins
    admin_message = {
        'created': f'New booking request for Room {booking.room.room_number} from {booking.user.name}. (Booking ID: {booking.id})',
        'approved': f'Booking for Room {booking.room.room_number} has been approved by {booking.approved_by_user.name if booking.approved_by_user else "an admin"}. (Booking ID: {booking.id})',
        'rejected': f'Booking for Room {booking.room.room_number} has been rejected by {booking.rejected_by_user.name if booking.rejected_by_user else "an admin"}. (Booking ID: {booking.id})',
        'cancelled': f'Booking for Room {booking.room.room_number} has been cancelled by {booking.user.name}. (Booking ID: {booking.id})'
    }
    
    for admin in admin_users:
        create_notification(
            user_id=admin.id,
            title=f'Booking {action.title()}',
            message=admin_message.get(action, f'Booking status updated (Booking ID: {booking.id})'),
            type='booking'
        )

def mark_notification_as_read(notification_id, user_id):
    """
    Mark a notification as read.
    
    Args:
        notification_id (int): The ID of the notification
        user_id (int): The ID of the user who owns the notification
    """
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=user_id
    ).first()
    
    if notification:
        notification.is_read = True
        db.session.commit()
        return True
    return False

def mark_all_notifications_as_read(user_id):
    """
    Mark all notifications as read for a user.
    
    Args:
        user_id (int): The ID of the user
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error marking all notifications as read: {e}")
        return False

def get_unread_notifications_count(user_id):
    """
    Get the count of unread notifications for a user.
    
    Args:
        user_id (int): The ID of the user
    
    Returns:
        int: The number of unread notifications
    """
    return Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).count()

def get_user_notifications(user_id, limit=10, offset=0):
    """
    Get notifications for a user with pagination.
    
    Args:
        user_id (int): The ID of the user
        limit (int): Maximum number of notifications to return
        offset (int): Number of notifications to skip
    
    Returns:
        list: List of notification dictionaries
    """
    notifications = Notification.query.filter_by(user_id=user_id)\
        .order_by(Notification.created_at.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    return [notification.to_dict() for notification in notifications] 