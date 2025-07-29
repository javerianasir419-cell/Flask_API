from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"

user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String
}

class Users(Resource):
    @marshal_with(resource_fields)
    def get(self):
        users = UserModel.query.all()
        return users, 201
    
    @marshal_with(resource_fields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(name=args["name"], email=args["email"])
        db.session.add(user)
        db.session.commit()
        return user, 201

class User(Resource):
    @marshal_with(resource_fields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        return user 

    @marshal_with(resource_fields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        user.name = args["name"]
        user.email = args["email"]
        db.session.commit()
        return user      

    @marshal_with(resource_fields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        db.session.delete(user)    
        db.session.commit()
        users = UserModel.query.all()
        return users

api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')

@app.route("/")
def home():
    return redirect(url_for("list_users"))

with app.app_context():
    db.create_all()

from flask import render_template, request, redirect, url_for

# Show all users
@app.route("/users")
def list_users():
    users = UserModel.query.all()
    return render_template("index.html", users=users)

# Create user form
@app.route("/users/create", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        new_user = UserModel(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("list_users"))
    return render_template("create.html")

# Update user
@app.route("/users/update/<int:id>", methods=["GET", "POST"])
def update_user(id):
    user = UserModel.query.get_or_404(id)
    if request.method == "POST":
        user.name = request.form["name"]
        user.email = request.form["email"]
        db.session.commit()
        return redirect(url_for("list_users"))
    return render_template("update.html", user=user)

# Delete user
@app.route("/users/delete/<int:id>")
def delete_user(id):
    user = UserModel.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("list_users"))

if __name__ == "__main__":
    app.run(debug=True)
