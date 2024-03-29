from flask import abort, request
from flask_smorest import Blueprint
from flask.views import MethodView
from src.contextmanager import DatabaseContextManager
from src.schema import (
    UserCreateSchema,
    EmploymentInfoSchema,
    GuarantorsSchema,
    ContributionFrequencySchema,
    UserListDisplay,
    LoginSchema,
    UserDisplaySchema,
    PersonalInfoSchema,
    AddUserChama,
    ChamaSchema,
    ChamaDisburseSchema,
    CallbackSchema
)
import uuid
import threading
from src.models import (
    User,
    Guarantors,
    Transaction,
    Chama
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import (
    insert,
    update,
    select,
    and_
)
from src.utils import (
    verify_authentication_headers,
    PaymentService
)
import datetime
import os

users_router = Blueprint('users', __name__)


mpesa = PaymentService(os.environ.get('CONSUMER_KEY'), os.environ.get('CONSUMER_SECRET'))


@users_router.route('/')
class UserManager(MethodView):
    @users_router.response(schema=UserListDisplay, status_code=200)
    def get(self):
        with DatabaseContextManager() as context:
            users = context.session.query(User).all()
        return {
            'subscribers': [
                client.to_json() for client in users
            ]
        }

    # step one
    @users_router.arguments(schema=UserCreateSchema)
    @users_router.response(schema=UserCreateSchema, status_code=201)
    def post(self, payload):
        payload['password'] = generate_password_hash(payload['password'])
        payload['uuid'] = uuid.uuid4().hex
        with DatabaseContextManager() as context:
            statement = insert(
                User
            ).values(
                **payload
            )
            context.session.execute(statement)
            context.session.commit()
        return payload

    def put(self, payload):
        pass

    def update(self, payload):
        pass

    def delete(self, payload):
        pass


@users_router.route('/get/details/<userid>')
@users_router.response(schema=PersonalInfoSchema, status_code=200)
def get_details(userid):
    with DatabaseContextManager() as context:
        user = context.session.query(
            User
        ).filter(
            User.uuid == userid
        ).first()
        guarantors = context.session.query(
            Guarantors
        ).filter(
            Guarantors.user_id == userid
        ).all()
    payload = user.to_json()
    payload['guarantors'] = []
    for results in guarantors:
        payload['guarantors'].append(results.to_json())
    return payload


# Step two -> Employment Status
@users_router.route('/add/employmentinfo', methods=['POST'])
@users_router.arguments(schema=EmploymentInfoSchema)
@users_router.response(schema=UserDisplaySchema, status_code=201)
@verify_authentication_headers
def add_employment_info(current_user, payload):
    statement = update(User).values(
        payload
    ).where(
        User.uuid == current_user.uuid
    )
    with DatabaseContextManager() as context:
        context.session.execute(statement)
        context.session.commit()
    return current_user.to_json()


# Step three -> guarantors
@users_router.route('/add/guarantors', methods=['POST'])
@users_router.arguments(schema=GuarantorsSchema)
@users_router.response(schema=GuarantorsSchema, status_code=201)
@verify_authentication_headers
def add_guarantors(current_user, payload):
    payload['user_id'] = current_user.uuid
    statement = insert(Guarantors).values(
        **payload
    )
    with DatabaseContextManager() as context:
        context.session.execute(statement)
        context.session.commit()
    return payload


# Login endpoint
@users_router.route('/login', methods=['POST'])
@users_router.arguments(schema=LoginSchema)
def login(payload):
    with DatabaseContextManager() as context:
        user = context.session.query(User).filter(
            User.email == payload['email']
        ).first()
        if user:
            if check_password_hash(user.password, payload['password']):
                return {
                    "auth": user.generate_token(user.uuid)
                }
            return {
                "Error": "Wrong password"
            }
        return {
            "Error": "user does not exist"
        }

# Step 4 -> Contribution Frequency


@users_router.route('/add/contribution/frequency', methods=['POST'])
@users_router.arguments(schema=ContributionFrequencySchema)
@users_router.response(schema=UserDisplaySchema, status_code=201)
@verify_authentication_headers
def add_contribution_frequency(current_user, payload):
    statement = update(User).values(
        **payload
    ).where(
        User.uuid == current_user.uuid
    )
    with DatabaseContextManager() as context:
        context.session.execute(statement)
        context.session.commit()
    return current_user.to_json()


# add admin priviledges to add members to groups
@users_router.route('/join/chama', methods=['POST'])
@users_router.arguments(schema=AddUserChama)
@verify_authentication_headers
def join_chama(current_user, payload):
    with DatabaseContextManager() as context:
        user = context.session.query(User).filter(
            User.uuid == payload['userid']
        ).first()

        if user:
            if user.contribution_frequency:
                # pay to be added to chama
                req = mpesa.prompt_payment_for_service(
				    user.phone,
                    user.contribution_frequency,
					"Join One Chama in Chamayettu"
				)
                
                response = req.json()
                
                if req.status_code != 200:
                    out_ = {
                        'errors': [
                            response['errorMessage']
                        ]
                    }
                    return out_
                out_ = {
                    'Response': {
                        'Message': response['CustomerMessage'],
                        'Code': response['ResponseCode'],
                        'Description': response['ResponseDescription'],
                        'MerchantID': response['MerchantRequestID'],
                        'CustomerID': response['CheckoutRequestID']
                    }
                }
                
                return out_
                
                # while not user.is_assigned_chama:
                #     chama = context.session.query(
                #         Chama
                #     ).filter(
                #         and_(
                #             Chama.member_count < 3,
                #             Chama.status == "pending",
                #             Chama.contribution_amount == user.contribution_frequency
                #         )
                #     ).first()

                #     if chama:
                #         user.chama_id = chama.chama_id
                #         user.points += 100
                #         user.is_assigned_chama = True
                #         chama.member_count += 1
                #         context.session.commit()
                #         break
                #     else:
                #         cstatement = insert(
                #             Chama
                #         ).values(
                #             **{
                #                 'chama_name': uuid.uuid4().hex,
                #                 'contribution_amount': user.contribution_frequency
                #             }
                #         )

                #         context.session.execute(cstatement)
                #         context.session.commit()
            else:
                return {
                    'Error': 'please add contribution frequency'
                }
        else:
            return {
                    'Error': 'User does not exist'
                }

    return {
        'success': f'User added to Chama {chama.chama_name}'
        }


# Add profile picture
@users_router.route('/add/profile', methods=['POST'])
@verify_authentication_headers
def add_profile():
    pass


# Add mpesarest configurations
@users_router.route('/pay/chama', methods=['POST'])
@verify_authentication_headers
def pay_chama(current_user):
    if current_user.contribution_frequency:
        # mpesarest configuration
        res = mpesa.prompt_payment_for_service(
            current_user.phone,
            current_user.contribution_frequency,
			"Regular payment for Chama in Chamayettu"
        )
        return res
    return {
        'Error': 'Please update your contribution frequency'
    }

# Check if user exists in chama else carryout normal payment


@users_router.route('/payment/callback')
class PaymentCallBackHandler(MethodView):
    @users_router.arguments(schema=CallbackSchema, location='params')
    def get(self, params):
        # checkout transaction status
        if params:
            if params['CheckoutRequestID']:
                response = mpesa.check_lipa_na_mpesa_status(
                    params['CheckoutRequestID']
                )
                return response
        return {
            'Error': 'missing params'
        }

    def post(self):
        payload = request.get_json()
        status = payload['Body']['stkCallback']
        if status['ResultCode'] == 0:
            with DatabaseContextManager() as context:
                user = context.session.query(User).filter(
                    User.phone == status['CallbackMetadata']['Item'][3]['Value']
                ).first()

                if user:        
                    user.points += 100
                    statement = insert(
                        Transaction
                    ).values(
                        **{
                            'amount': status['CallbackMetadata']['Item'][0]['Value'],
                            'transaction_date': status['CallbackMetadata']['Item'][2]['Value'],
                                            'receipt_number': status['CallbackMetadata']['Item'][1]['Value'],
                                            'transaction_code': status['CheckoutRequestID'],
                                            'user_id': user.uuid
                            }
                        )

                    context.session.execute(statement)
                    context.session.commit()

                    if user.is_assigned_chama:
                        # Assume Normal Monthly payment
                        user.last_payment = status['CallbackMetadata']['Item'][2]['Value']

                    # add user to chama database table
                    while not user.is_assigned_chama:
                        chama = context.session.query(Chama).filter(
                            and_(
                                Chama.member_count < 3,
                                Chama.status == 'pending',
                                Chama.contribution_amount == User.contribution_frequency
                            )
                        ).first()

                        if chama:
                            user.chama_id = chama.chama_id
                            user.is_assigned_chama = True
                            chama.member_count += 1
                            context.session.commit()
                        else:
                            cstatement = insert(
                                Chama
                            ).values(
                                **{
                                    'chama_name': uuid.uuid4().hex,
                                    'contribution_amount': User.contribution_frequency
                                }
                            )

                            context.session.execute(cstatement)
                            context.session.commit()
        else:
            return {
                'error': payload['ResultDesc']
            }


@users_router.route('/distribute/funds/chama/', methods=['POST'])
@users_router.arguments(schema=ChamaDisburseSchema)
@verify_authentication_headers
def distribute_chama(current_user, payload):
    if current_user.is_admin:
        thirty_days_count = datetime.datetime.timedelta(days=30)
        with DatabaseContextManager() as context:
            chama = context.session.query(
                Chama
            ).filter_by(
                chamaname=payload['chamaname']
            ).first()
            while not chama.funds_disbursed:
                end_date = chama.date_created + thirty_days_count
                if end_date.day >= datetime.datetime.today().day:
                    users = context.session.query(User).filter(
                        and_(
                            User.chama_id == chama.id
                            )
                    ).all()
                    for user in users:
                        # if the user in this chama is already paid funds are disbursed to the next user
                        if not user.last_payment:
                            # pay person
                            mpesa.initialize_business_to_client(
                                    clientphonenumber=user.phone,
                                    Amount=chama.contribution_amount,
                                    Remarks=ChamaDisburseSchema['Remarks']
                                )
                            chama.funds_disbursed = True
                            break
                        else:
                            pass
        return abort(403)

# Business to Client


@users_router.route('/diburse/funds/chama/chamamember/<uuid>', methods=['POST'])
@verify_authentication_headers
def disburse_funds(userid, uuid):
    pass
