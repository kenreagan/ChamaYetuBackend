from functools import wraps
from flask import (
    request,
    make_response,
    current_app
)
import jwt
from src.contextmanager import DatabaseContextManager
from src.models import User


def verify_authentication_headers(function):
    @wraps(function)
    def wrapper_verifier(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[-1]
            try:
                user_id = jwt.decode(
                    token,
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )

                with DatabaseContextManager() as context:
                    current_user = context.session.query(User).filter_by(uuid=user_id['sub']).first()
            except:
                return {
                    'error': "Unexpected token decoding"
                }
        else:
            make_response({
                'Error': 'Missing Token ...'
            }, 401)
        return function(current_user, *args, **kwargs)
    return wrapper_verifier


class GroupTracker:
    pass