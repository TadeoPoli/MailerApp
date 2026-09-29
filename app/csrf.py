import hmac
import secrets

from flask import abort, request, session


def csrf_token():
    token = session.get('_csrf_token')
    if token is None:
        token = secrets.token_urlsafe(32)
        session['_csrf_token'] = token
    return token


def validate_csrf_token():
    submitted_token = request.form.get('csrf_token')
    session_token = session.get('_csrf_token')
    if not submitted_token or not session_token:
        abort(400)
    if not hmac.compare_digest(session_token, submitted_token):
        abort(400)
