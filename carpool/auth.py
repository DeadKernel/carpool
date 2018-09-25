import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from carpool.db1 import connector

#count1 =0
bp = Blueprint('auth', __name__, url_prefix='/auth')
@bp.route('/signup', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        email = request.form['email']
        phnumber = request.form['phno']
        confpass = request.form['conpassword']
        db,conn1 = connector()
        count1=db.users.count()
        count1+=1
        userinfo = {
            "_id":count1,
            "name":username,
            "mailid":email,
            "password":generate_password_hash( password),
            "phno":phnumber
        }
        checkduplicate=db.users.find_one(
            {"name":username}
      )

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
            print("Toshal")
        flash(error)

    return render_template('auth/signup.html')
