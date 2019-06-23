from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow, Schema, fields
from marshmallow import Schema, fields

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
    hobby = db.relationship('Hobby', backref='user', lazy=True)    

    def __init__(self, username, lastname, reward, hobby):
        self.username = username
        self.lastname = lastname
        self.reward = reward
        self.hobby = hobby        

    @classmethod
    def find_by_userid(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all_users(cls):
        return cls.query.all()    

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
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
  

class Hobby(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hobby = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, hobby, user_id):
        self.hobby = hobby
        self.user_id = user_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit() 

#####
# SCHEMA
#####
class RewardSchema(ma.ModelSchema):
    class Meta:
        model = Reward
        fields = ('name',)
        ordered = True


class HobbySchema(ma.ModelSchema):
    class Meta:
        model = Hobby
        fields = ('hobby',)
        ordered = True        


class UserSchema(ma.ModelSchema):
    reward = fields.Pluck('RewardSchema', 'name', many=True)
    hobby = fields.Pluck('HobbySchema', 'hobby', many=True)    
    class Meta:
        model = User
        fields = ('id', 'username', 'lastname', 'reward', 'hobby',)


############################
### Marshmallow Schema init
############################
user_schema = UserSchema()
user_schema_list = UserSchema(many=True)

reward_schema = RewardSchema()
reward_schema_list = RewardSchema(many=True)

hobby_schema = HobbySchema()
hobby_schema_list = HobbySchema(many=True)

#####
# REST
#####
class UserApi(Resource):
    def get(self):
        data = request.get_json(silent=True)

        try:
            user = User.find_by_userid(data["id"])

            if user:
                return {'message': user_schema.dump(user)}, 200   
            return {'message': 'no user was found'}, 500
        
        except:
            return {'message': 'sth went wrong'}, 500

    def post(self):
        data = request.get_json(silent=True)

        new_user = {
            "username": data["username"],
            "lastname": data["lastname"],
            "reward": [],
            "hobby": []
            }

        try:
            # create a new User Object
            user = user_schema.load(new_user)
            user.save_to_db()        

            # Read all List items and create new Reward Object and store it to DB
            [Reward(name=item, user_id=user.id).save_to_db() for item in data["reward"]]

            [Hobby(hobby=item, user_id=user.id).save_to_db() for item in data["hobby"]]
        
        except:
            return {'message': 'sth went wrong'}, 500
        
        return {'message': user_schema.dump(user)}, 200     

    def delete(self):
        try:
            data = request.get_json(silent=True)

            user = User.find_by_userid(data["id"])
            user.delete_from_db()
        
        except:
            return {'message': 'sth went wrong'}, 500

        return {'message': "user gelöscht"}, 200            


class getAllUsers(Resource):
    def get(self):
        return {'message': user_schema_list.dump(User.query.all())}, 200


class getAllRewards(Resource):
    def get(self):
        return {'message': reward_schema_list.dump(Reward.query.all())}


class getAllHobbies(Resource):
    def get(self):
        return {'message': hobby_schema_list.dump(Hobby.query.all())}        

# User Api
api.add_resource(UserApi, '/user')
api.add_resource(getAllUsers, '/users')
# Reward Api
api.add_resource(getAllRewards, '/rewards')
# Hobby Api
api.add_resource(getAllHobbies, '/hobbies')

if __name__ == '__main__':
    app.run(debug=True)