import os, hashlib

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Check for environment variable
DATABASE_URL = 'postgres://lfmoyqcmuvfoqn:c57be9c5cdd24c0fbe274db8c6626346f1ed8c47b3d8ec0317f73eae8d258337@ec2-50-19-249-121.compute-1.amazonaws.com:5432/d83lec9qlit9jv'
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template('layout.html')


@app.route('/registration')
def show_registration_form():
    return render_template('registration.html')


@app.route('/registration/register', methods=['POST'])
def register():
    # TODO: Read data from form
    salt = 'CS50W_project1'
    registration_data = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
    }
    assert len(registration_data['username']) > 0, 'No username'
    assert len(registration_data['email']) > 0, 'No email'
    password = hashlib.sha256(salt.encode() + request.form.get('password').encode()).hexdigest()
    assert len(password) > 0, 'No password hash'

    # TODO: Check availability for registration data
    for key in registration_data.keys():
        if db.execute("SELECT :key FROM users WHERE :key = :value",
                   {'key': key, 'value': registration_data[key]}).rowcount != 0:
            return render_template('error.html', message='User with this {} already exists.'.format(key))

    # TODO: Update database
    if password:
        db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
                   {'username': registration_data['username'],
                    'email': registration_data['email'],
                    'password': password,
                    })
        db.commit()
    else:
        return render_template('error.html', message='Please enter a password.')

    # TODO: Respond to the user
    return redirect('/', code=422)

@app.route('/login', methods=['GET', 'POST'])
def login():
    salt='CS50W_project1'

    # TODO: Collect login data
    login_data = {
        'username': request.form.get('username'),
        'password': hashlib.sha256(salt.encode() + request.form.get('password').encode()).hexdigest(),
    }
    print(login_data['password'])
    # TODO: Check user data in database
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
               {'username': login_data['username'],
                'password': login_data['password'],
                }).rowcount == 1:
        return render_template('login.html', message='Success!')