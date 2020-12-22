import os
from werkzeug.security import generate_password_hash
import sqlite3
basedir = os.path.abspath(os.path.dirname(__file__))

USERS_DB_STRING = basedir + "/users.db"  # remove#
user_conn = sqlite3.connect(USERS_DB_STRING, check_same_thread=False)
user_c = user_conn.cursor()

user = raw_input('What is your username? ')
user_sql = (user,)
user_check = user_c.execute('select count(*) from user where username = ?',user_sql)

for row in user_check:
    test_value = row[0]

if test_value >= 1:
    remove_y_n = raw_input("Would you like to delete this user? y/n ").lower()
    if remove_y_n == 'y':
        user_c.execute('delete from user where username = ?', user_sql)
    else:
        y_n = raw_input("Would you like to update the user's info? y/n ").lower()
        if y_n == 'y':
            password = raw_input('What is your password? ')
            email = raw_input('What is your email_address? ')
            pass_hash = generate_password_hash(password)
            null = None
            user_row = (null, user, pass_hash, email)
            user_c.execute('delete from user where username = ?', user_sql)
            user_c.execute('insert into user values(?,?,?,?)', user_row)
            print "Values have been replaced for user %s" % user
        else:
            print "Okay, no changes have been made"
else:
    password = raw_input('What is your password? ')
    email = raw_input('What is your email_address? ')
    pass_hash = generate_password_hash(password)
    null = None
    user_row = (null, user, pass_hash, email)
    user_c.execute('insert into user values(?,?,?,?)',user_row)
    print "%s has been added as a user" % user

user_conn.commit()
user_conn.close()