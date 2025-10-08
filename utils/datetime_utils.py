from datetime import datetime
import pytz
from flask import current_app

def get_local_timezone():
    """Get the configured local timezone"""
    return pytz.timezone(current_app.config.get('TIMEZONE', 'Asia/Manila'))

def utc_to_local(utc_dt):
    """Convert UTC datetime to local timezone"""
    if utc_dt is None:
        return None
    
    # If the datetime is naive (no timezone info), assume it's UTC
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    
    # Convert to local timezone
    local_tz = get_local_timezone()
    return utc_dt.astimezone(local_tz)

def local_to_utc(local_dt):
    """Convert local datetime to UTC"""
    if local_dt is None:
        return None
    
    # If the datetime is naive (no timezone info), assume it's in local timezone
    if local_dt.tzinfo is None:
        local_tz = get_local_timezone()
        local_dt = local_tz.localize(local_dt)
    
    # Convert to UTC
    return local_dt.astimezone(pytz.utc)

def get_current_local_time():
    """Get current time in local timezone"""
    return utc_to_local(datetime.utcnow())

def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """Format datetime object to string in local timezone"""
    if dt is None:
        return ''
    
    local_dt = utc_to_local(dt)
    return local_dt.strftime(format_str) 