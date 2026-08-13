from datetime import datetime
from functools import wraps
from flask import abort
from flask_login import current_user

def parsiraj_datum(vrijednost):
    if vrijednost:
        return datetime.strptime(vrijednost, "%Y-%m-%d").date()
    return None

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.je_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper