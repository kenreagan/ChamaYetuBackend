from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Boolean
from sqlalchemy.orm import relationship
import datetime
import jwt
from typing import Dict
from flask import current_app

Base = declarative_base()


class AuthenticationMixin:
    def generate_token(self, userid: int):
        payload: Dict[str, Optional] = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=2, minutes=0),
            "iat": datetime.datetime.utcnow(),
            "sub": userid
        }
        return jwt.encode(payload, key=current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(token, key=current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return {
                "code": 404,
                "status": "ExpiredSignatureError",
                "message": "Expired token",
                "errors": {
                    "": ""
                }
            }
        except jwt.InvalidTokenError:
            return {
                "code": 403,
                "status": "InvalidTokenError",
                "message": "Invalid token used",
                "errors": {
                    "": ""
                }
            }


class User(AuthenticationMixin, Base):
	__tablename__ = 'user'
	uuid = Column(String(300), primary_key=True, nullable=False, unique=True)
	points = Column(Integer, default=0)
	date_joined = Column(DateTime, default=datetime.datetime.utcnow)
	first_name = Column(String(250))
	last_name = Column(String(250))
	middle_name = Column(String(250))
	id_number = Column(Integer)
	gender = Column(String(250))
	date_of_birth = Column(DateTime)
	education_level = Column(String(250))
	residential_status = Column(String(250))
	email = Column(String, unique=True, nullable=False)
	employment = Column(String, default="unemployed")
	password = Column(String)
	monthly_income = Column(String(250))
	phone = Column(Integer, unique=True, nullable=False)
	contribution_frequency = Column(Integer)
	chama_id = Column(Integer, ForeignKey('groups.group_id'))
	profile_picture = Column(String(300))
	marital_status = Column(String(300))
	is_assigned_chama = Column(Boolean, default=False)
	guarantors = relationship('Guarantors', lazy='dynamic', cascade="all, delete-orphan")

	def __repr__(self) -> str:
		return f'{self.__class__.__qualname__}(points={self.points:!r}, name={self.first_name:!r}, email={self.email:!r})'

	def __eq__(self, other) -> bool:
		if self.__class__ == other.__classs:
			return self.points == other.points

	def __gt__(self, other) -> bool:
		if self.__class__ == other.__classs:
			return self.points > other.points

	def __lt__(self, other) -> bool:
		if self.__class__ == other.__classs:
			return self.points < other.points
	
	def __ne__(self, other) -> bool:
		return not self.__eq__(other)

	def to_json(self):
		return {
			'first_name' : self.first_name,
			'last_name': self.last_name,
			'middle_name': self.middle_name,
			'phone': self.phone,
			'contribution_frequency': self.contribution_frequency,
			'residential_status': self.residential_status,
			'email': self.email,
			'points': self.points,
			'educational_level': self.education_level,
			'income': self.monthly_income,
			'id': self.uuid,
			'id_number': self.id_number,
			'joining_date': self.date_joined,
			'date_of_birth': self.date_of_birth,
			'profile': self.profile_picture,
			'chama_status': self.is_assigned_chama
		}

class Guarantors(Base):
	__tablename__ = 'guarantors'
	id = Column(Integer, nullable=False, primary_key=True)
	relationship = Column(String(250))
	name = Column(String(250))
	email = Column(String(250))
	phone = Column(Integer)
	user_id = Column(Integer, ForeignKey('user.uuid'))

	def __repr__(self):
		return f"{self.__class__.__qualname__}(name={self.name:!r}, phone={self.phone:!r})"

	def to_json(self):
		return {
			"name": self.name,
			"relationship": self.relationship,
			'email': self.email,
			'phone': self.phone
		}


class Chama(Base):
	__tablename__ = 'Chama'
	chama_id = Column(String(300), primary_key=True, nullable=False)
	members = Column(Integer)
	contribution_amount = Column(Integer)
	status = Column(String(300), default='pending')

	def __repr__(self):
		return f"{self.__class__.__qualname__}(chama_id={self.chama_id}, contribution={self.contribution_amount}, status={self.status})"
	

	def to_json(self):
		return {
			"members": self.members,
			"contribution": self.contribution_amount
		}

# Split people into 3 groups
class Groups(Base):
	__tablename__ = 'groups'
	group_id = Column(String(300), primary_key=True, nullable=False, unique=True)
	user_id = Column(Integer, unique=True)
	amount = Column(Integer)

	def __repr__(self):
		return f"{self.__class__.__qualname__}(userid={self.user_id:!r}, amount={self.amount:!r})"

	def to_json(self):
		return {
			"userid": self.user_id,
			"amount": self.amount
		}