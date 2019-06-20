from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow, Schema, fields

app = Flask(__name__)
api = Api(app)

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

ma = Marshmallow(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#####
# MODELS
#####
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    lastname = db.Column(db.String(80))
    reward = db.relationship('Reward', backref='user', lazy=True)

    def __init__(self, username, lastname, reward):
        self.username = username
        self.lastname = lastname
        self.reward = reward

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_all_users(cls):
        return cls.query.all()    

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
   
   
class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_all_rewards(cls):
        return cls.query.all()    

#####
# SCHEMA
#####
class RewardSchema(ma.Schema):
    class Meta:
        model: Reward
        fields = ('name',)
        ordered = True

class UserSchema(ma.Schema):
    reward = ma.Nested('RewardSchema', only='name', many=True)
    class Meta:
        model: User
        fields = ('id', 'username', 'lastname', 'reward',)    


############################
### Marshmallow Schema init
############################
user_schema = UserSchema()
user_schema_list = UserSchema(many=True)

#####
# REST
#####
class UserApi(Resource):
    def get(self):
        search_item = request.get_json(silent=True)

        user = User.find_by_username(search_item["username"])

        if user:
            return {'message': user.user_json()}, 200   
        return {'message': 'no user was found'}, 500

    def post(self):
        data = request.get_json(silent=True)

        user_data = user_schema.load(data) 

        #user_data.save_to_db()
        return {'message': user_schema.dump(user_data)}, 200
        # try:
        #     new_user = User(**data)
        #     new_user.save_to_db()
        # except:
        #     return {'message': 'user with this name already exist'}, 500   

        # return {'message': new_user.user_json()}, 200


class getAllUsers(Resource):
    def get(self):
        return {'message': user_schema_list.dump(User.query.all())}, 200


class RewardApi(Resource):
    def get(self):
        search_item = request.get_json(silent=True)
        
        reward = Reward.find_by_username(search_item["username"])

        if reward:
            return {'message': reward.reward_json()}, 200   
        return {'message': 'no user was found'}, 400

    def post(self):
        data = request.get_json(silent=True)

        new_reward = Reward(**data)
        new_reward.save_to_db()

        return {'message': 'reward angelegt'}, 200


class getAllRewards(Resource):
    def get(self):
        return {'message': [reward.reward_json() for reward in Reward.find_all_rewards()]}

# User Api
api.add_resource(UserApi, '/user')
api.add_resource(getAllUsers, '/users')
# Reward Api
api.add_resource(RewardApi, '/reward')
api.add_resource(getAllRewards, '/rewards')

if __name__ == '__main__':
    app.run(debug=True)