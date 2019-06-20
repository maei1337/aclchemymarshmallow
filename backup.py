from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate

app = Flask(__name__)
api = Api(app)

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#####
# MODELS
#####

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    lastname = db.Column(db.String(80))

    def __init__(self, username, lastname):
        self.username = username
        self.lastname = lastname

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_all_users(cls):
        return cls.query.all()    

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def user_json(self):
        return {
            'username': self.username,
            'lastname': self.lastname
        }

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    
    def __init__(self, name):
        self.name = name

    def reward_json(self):
        return {
            'reward': self.name
        }
#####
# SCHEMA11
#####






#####
# REST
#####
class UserApi(Resource):
    def get(self):
        search_item = request.get_json(silent=True)

        user = User.find_by_username(search_item["username"])

        if user:
            return {'message': user.user_json()}, 200   
        return {'message': 'no user was found'}, 400

    def post(self):
        data = request.get_json(silent=True)
        try:
            new_user = User(**data)
            new_user.save_to_db()
        except:
            return {'message': 'user with this name already exist'}, 500   

        return {'message': new_user.user_json()}, 200


class getAllUsers(Resource):
    def get(self):
        return {'message': [user.user_json() for user in User.find_all_users()]}


class RewardApi(Resource):
    def get(self):
        search_item = request.get_json(silent=True)
        
        user = User.find_by_username(search_item["username"])

        if user:
            return {'message': user.user_json()}, 200   
        return {'message': 'no user was found'}, 400

    def post(self):
        data = request.get_json(silent=True)

        new_user = User(**data)
        new_user.save_to_db()

        return {'message': new_user.user_json()}


class getAllRewards(Resource):
    def get(self):
        return {'message': [reward.reward_json() for reward in Reward.find_all_users()]}

# User Api
api.add_resource(UserApi, '/user')
api.add_resource(getAllUsers, '/users')
# Reward Api
api.add_resource(RewardApi, '/reward')
api.add_resource(getAllRewards, '/rewards')

if __name__ == '__main__':
    app.run(debug=True)