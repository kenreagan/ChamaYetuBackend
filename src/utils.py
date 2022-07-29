from functools import wraps
from flask import (
    request,
    make_response,
    current_app
)
import requests
from requests.auth import HTTPBasicAuth
import jwt
from src.contextmanager import DatabaseContextManager
from src.models import User
import os
import datetime
import base64
from typing import Dict


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


class PaymentService:
    def __init__(self, consumer_key, consumer_secret) -> None:
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
    
    def generate_token(self):
        body = requests.get(
            "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials", 
            auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        )
        return body
    
    def start_validation(self) -> Dict[str, str]:
        payment_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        passkey: str = os.environ.get('PASSCODE')
        data_to_encode = str(os.environ.get('BUSINESS_CODE')) + passkey + payment_time
        online_password = base64.b64encode(data_to_encode.encode())
        decode_password = online_password.decode('utf-8')
        my_dict = {
            "password": decode_password,
            "payment_time": payment_time
        }
        return my_dict
    
    def prompt_payment_for_service(self, customer_phone, customer_amount, description):
        access_token = self.generate_token()
        if access_token.status_code != 200:
            return {
                'errors': [
                    'Invalid token'
                ]
            }
        token = access_token.json()["access_token"]
        request_body = {
                "BusinessShortCode": os.environ.get('BUSINESS_CODE'),
                "Password": self.start_validation()['password'],
                "Timestamp": self.start_validation()['payment_time'],
                "TransactionType": "CustomerPayBillOnline",
                "Amount": customer_amount,
                "PartyA": customer_phone,
                "PartyB": os.environ.get('SHORT_CODE'),
                "PhoneNumber": customer_phone,
                "CallBackURL": os.environ.get('CALLBACK_URL'),
                "AccountReference": os.environ.get('MYCOMPANY'),
                "TransactionDesc": description 
            }
        
        headers = {
            "Authorization": "Bearer %s" %token
        }
        response = requests.post('https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest', request_body, headers=headers)
        return response.json()
    
    def check_status_payment(self, RequestCheckoutID):
        return