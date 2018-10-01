import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from carpool.db1 import connector


#count1 =0
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/')
def index():
    if 'username' in session:
        return 'You are logged in as ' + session['username']
    return render_template('auth/login.html')

@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        db,conn1 = connector()
        users = db.users
        login_user = users.find_one({'name' : request.form['username']})
        if login_user:
            password=request.form['password']
            if check_password_hash(login_user['password'], password):
                session['username'] = request.form['username']
                return redirect(url_for('auth.index'))
            return 'Invalid username/password combination'

    return render_template('auth/login.html')
@bp.route('/home')
def auth():
    return render_template('auth/home.html')

@bp.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        email = request.form['email']
        phnumber = request.form['Phno']
        confpass = request.form['conpassword']
        car_plate=request.form['plate']
        licence_number=request.form['license']
        car_model=request.form['model']

        if not request.form.get('owncar'):
            car_plate=None
            licence_number=None
            car_model=None
        db,conn1 = connector()
        count1=db.users.count()
        count1+=1
        userinfo = {
            "name":username,
            "mailid":email,
            "password":generate_password_hash( password),
            "phno":phnumber,
            "car_details":[
            {
                    "model":car_model,
                    "plate":car_plate,
                    "license":licence_number
            }
            ]
        }
        checkduplicate=db.users.find_one(
            {"name":username})

        error = None
        if not username:
            return('1')
        elif not password:
            return('2')
        elif not email:
            return('3')
        elif not phnumber:
            return('4')
        elif confpass != password or  not password :
            return('5')
        elif checkduplicate is not None:
             return('User {} is already registered.'.format(username))

        if error is None:
            user= db.users
            user.insert_one(userinfo)
            return ("okay")
        flash(error)

    return render_template('auth/signup.html')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
