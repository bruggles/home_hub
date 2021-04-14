#! /usr/bin/python3

from flask import render_template, flash, redirect, url_for, request, session
from app_contents import db, app
from app_contents.forms import LoginForm, RegistrationForm, BudAddMod, Move, Update, Delete, Search, New, Machine, Maint, MaintenanceSchedule
from flask_login import current_user, login_user, logout_user, login_required
from app_contents.models import User
import os, sqlite3, calendar
from werkzeug.urls import url_parse
import os
import app_contents.config as config
from flask_wtf.csrf import CSRFProtect
import yaml
from app_contents.functions import db_list, sms_report, text_send, html_table, link_list, std_link, num_link, mnth_cat_link, cat_mnth_link, db_submit, db_data, remote
from datetime import date
from twilio import twiml
import re
from dotenv import load_dotenv
from random import randint
import requests

app_contents = os.path.abspath(os.path.dirname(__file__))
repo_dir = os.path.abspath(os.path.join(app_contents, '../..'))
flask_dir = os.path.abspath(os.path.join(app_contents, '..'))
remote_dir = os.path.abspath(os.path.join(repo_dir, 'remote'))

load_dotenv(os.path.join(repo_dir,'vars.env'))

zero = 0
one = 1
null = None

url_string = os.environ.get('URL_PROD')

with open(os.path.join(app_contents, 'queries.yml'), 'r') as file:
        queries = yaml.load(file, Loader=yaml.FullLoader)
DB_STRING = os.path.join(app_contents,'home_hub.db')
conn = sqlite3.connect(DB_STRING, check_same_thread=False)
conn.row_factory = sqlite3.Row # this powers some of the row functionality
c = conn.cursor()

@app.route('/login', methods=['GET', 'POST'])
def login():
    print('login')
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    print('pre_validate')
    if form.validate_on_submit():
        print('validated')
        user = User.query.filter_by(username=form.username.data).first()
        app.logger.debug(f"user:{user.username}")
        app.logger.debug(f"pw:{user.check_password(form.password.data)}")
        session['user'] = user.username
        session['app_group'] = user.app_group
        session['garage_access'] = user.garage_access
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        app.logger.debug(f"remember:{form.remember_me.data}")
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        keys = os.environ.get('ACCESS_KEYS').split(',')
        garage_phones = os.environ.get('GARAGE_NUMS').split(',')
        if form.access_key.data in keys:
            phone_num = "+1"+re.sub("[^0-9] ", "", form.phone_num.data)
            if phone_num in garage_phones:
                garage_access = 1
            else:
                garage_access = 0
            user = User(username=form.username.data, email=form.email.data, phone_num = phone_num, 
                        app_group = form.app_group.data, garage_access=garage_access)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        else:
            flash('Sorry wrong Access Key')
            return render_template('auto_form.html', title='Register', form=form)
    return render_template('auto_form.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/")
@app.route('/index')
@login_required
def index():
    #user = session['user']
    return render_template('home.html', **locals())

@app.route('/sms', methods=['POST'])
def sms():
    today = date.today()
    today2 = today.strftime('%Y-%m-%d')
    number = request.form['From']
    message_body = request.form['Body']
    message_split =  message_body.lower().split()
    signal = message_split[0]
    try:
        r = requests.get('https://icanhazdadjoke.com', headers={"Accept":"text/plain"})
        dad_joke = ' ' + r.text
    except:
        dad_joke = ''
    #message = 'Hello {}, you said: {}'.format(number, message_body)
    bud_signal = ['bud', 'budget', 'bad', 'bird']
    mod_signal = ['mod', 'modify']
    add_signal = ['add', 'ad']
    move_signal = ['move', 'mv']
    rep_signal = ['rep', 'report']
    upd_signal = ['upd', 'update']
    del_signal = ['del', 'delete']
    summary_signal = ['sum', 'summary']
    man_signal = ['man', 'manual','instructions']
    maint_signal = ['maintenance', 'maint']
    garage_nums = os.environ.get('GARAGE_NUMS').split(',')
    garage_signal = ['garage','garages','open','close']
    garages = ['a','b']
    joke_signal = ['joke','jokes','dadjoke','dad','funny','laugh']

    #need to dynamically create these lists
    phone_numbers = {}
    for instance in db.session.query(User):
        phone_numbers[instance.phone_num] = instance.app_group
    success = True
    love_nums = os.environ.get('LOVE_NUMS').split(',')
    today_note = "Happy %s, I hope today is amazing. " % today.strftime('%A')
    if number in love_nums:
        love_notes = ['You sure are looking good today. ',
                      'The creator of this app loves you. ', 
                      'I sure hope you are having a good day. ', 
                      'Thanks for all of your help today. ', 
                      'Your family loves you. ',
                      'I hope you know that your husband - Brandon loves you! ',
                      'Hey babums. ',
                       today_note]
        love_note = love_notes[randint(0,len(love_notes)-1)]
    else:
        love_note = ''

    if number in phone_numbers:
        app_group = phone_numbers[number]
        bud_categories_up = db_list(yaml_query='categories', vars=(app_group,))
        bud_categories = []
        for category in bud_categories_up:
            bud_categories.append(category.lower())
        if signal in bud_signal or signal in bud_categories or signal in rep_signal or signal in add_signal or signal in mod_signal:
            if (len(message_split) == 1 and signal in bud_categories) or signal in rep_signal:
                if len(message_split) == 1:
                    category = signal
                else:
                    category = message_split[1]
                message = sms_report(category = category, app_group = app_group)
                #build category report
                #message = 'send a budget category report'
            elif (len(message_split) > 1 and signal in bud_categories) or signal in bud_signal or signal in add_signal or signal in mod_signal:
                if signal in bud_categories:
                    try:
                        category = signal
                        amount = message_split[1]
                        notes_list = message_split[2:]
                        signal = 'bud'
                        float(amount)
                    except:
                        success = False
                        message = 'Budget entries should be formated like category amount notes ie home 50.25 door knob - if it is a new category start out with bud'
                else:
                    try:
                        category = message_split[1]
                        amount = message_split[2]
                        notes_list = message_split[3:]
                        float(amount)
                    except:
                        success = False
                        message = '%s entries should be formated like %s category amount notes ie %s home 50.25 door knob' % (signal.title(), signal, signal)
                if success:
                    notes = ' '.join(notes_list)
                    sql_amount = int(float(amount)*100)
                    if signal in bud_signal:
                        #make a budget entry
                        db_submit('bud',(today2,category,sql_amount,notes,app_group))
                        message = 'Got it, I put in an entry for $%s in %s with these notes: %s' % (amount, category, notes)
                    elif signal in add_signal:
                        #make a budget addition
                        db_submit('add',(today2,category,sql_amount,notes,app_group))
                        message = 'okey dokey, I added $%s to %s with these notes: %s' % (amount, category, notes)
                    elif signal in mod_signal:
                        #modify a budget allocation
                        db_submit('mod1',(category,app_group))
                        db_submit('mod2',(today2,category,sql_amount,notes,1,app_group))
                        message = '%s has been modified to get $%s allocated to its budget each month' % (category.title(), amount)
        elif signal in move_signal:
            try:
                amount = message_split[1]
                sql_amount = int(float(amount)*100)
                from_category = message_split[2]
                to_category = message_split[3]
                if from_category in bud_categories and to_category in bud_categories:
                    sql_amount_neg = 0-sql_amount
                    rem_notes = 'moved to ' + to_category
                    db_submit('move',(today2,from_category,sql_amount_neg,rem_notes,app_group))
                    add_notes = 'moved from ' + from_category
                    db_submit('move',(today2,to_category,sql_amount,add_notes,app_group))
                    message = 'Moved %s from %s to %s' % (amount, from_category, to_category)
                else:
                    message = 'It looks like the message was formatted correctly or close, but the one or both of the categories are wrong. It should be "move amount from_category to_category"'
            except:
                message = 'Move requests should be formatted like "move amount from_category to_category"'
        elif signal in upd_signal:
            try:
                from_category = message_split[1]
                to_category = message_split[2]
                if to_category in bud_categories:
                    db_submit('upd',(to_category, from_category, app_group))
                    db_submit('upd2',(to_category, from_category, app_group))
                    db_submit('upd3',(to_category, from_category, app_group))
                    message = "You updated everything in %s to %s" % (from_category, to_category)
                else:
                    message = "It looks like the message was formatted properly, but the category that you tried to move to doesn't exist. The format should be 'update from_category to_category'"
            except:
                message = "To update categories the message should be like 'update from_category to_category'"
        elif signal in del_signal:
            try:
                id = int(message_split[1])
                db_submit('del', (id,))
                message = "You deleted the entry with id number %s" % id
            except:
                message = "It looks like you didn't put in an id number after the del or delete command"
        elif signal in summary_signal:
            message = sms_report(app_group = app_group)
        elif signal in man_signal:
            message = 'Check out the manual online at http://www.brandonruggles.com%s' % url_for('manual')
        elif signal in maint_signal:
            try:
                machine = message_split[1]
                miles = int(message_split[2])
                notes = notes = ' '.join(message_split[3:])
                category = 'unknown'
                service = 'unknown'
                db_submit('maint', (today2, machine.lower(), miles, notes, category, service, app_group))
                message = 'You logged maintenance on %s with %s as notes at %s miles' % (machine, notes, miles)
            except:
                message = "To log maintenance use this format 'maintenance machine miles notes' ie. 'maintenance lexus 110000 oil change'"
        elif signal in garage_signal:
            if number in garage_nums:
                garage_state_names = {0:'closed',1:'open'}
                #get the garage states
                with open(os.path.join(remote_dir, 'garage_state.txt'), 'r') as file:
                    garage_states_list = file.readline().split(',')
                garage_states = []
                for garage_state in garage_states_list:
                    try:
                        garage_states.append(int(garage_state))
                    except:
                        pass
                #garage_states = [0,1]
                if signal == 'open':
                    for i, garage in enumerate(garages):
                        if message_split[1] == garage:
                            if garage_states[i] == 0:
                                #open garage door
                                remote(server="garage",command='run', file='garage_open.py',action=garage)
                                message = "Opening garage door %s" % garage.upper()
                            else:
                                message = "Garage door %s is already open" % garage.upper()
                elif signal == 'close':
                    for i, garage in enumerate(garages):
                        if message_split[1] == garage:
                            if garage_states[i] == 1:
                                #close garage door 
                                remote(server="garage",command='run', file='garage_open.py',action=garage)
                                message = "Closing garage door %s" % garage.upper()
                            else:
                                message = "Garage door %s is already closed" % garage.upper()
                else:
                    message = ""
                    for i, garage in enumerate(garages):
                        message = "%sGarage %s is %s\n" % (message, garage.upper(), garage_state_names[garage_states[i]])
            else:
                message = "You don't have access to control or look at the garage doors"
        elif signal in joke_signal:
            message = ""
        else:
            message = "Something went wrong\nif you believe you got it right but aren't sure of the category respond with 'sum' to get a report with the categories.\nIf you would like general instructions type 'manual'"
    else:
        message = 'Access denied'
    message = love_note + message + dad_joke
    text_send(body=message, to=number)
    return str(message)

@app.route('/manual')
def manual():
    return(render_template('manual.html'))


@app.route('/category')
@app.route('/category/<category_sql>')
@login_required
def category(category_sql = None):
    title = 'Budget Categories'
    if category_sql == None:
        cat = c.execute(queries['categories'],(session['app_group'],))
        link_list_attrs = {'data' : cat,
                            'title' : 'Available Categories',
                            'link_func' : std_link,
                            'link_path' : url_for('category')}
        category_links = link_list(link_list_attrs)
        return render_template('category_links.html', **locals())
    else:
        title = '%s Report' % category_sql.capitalize()
        data = c.execute(queries['category_report'], (category_sql,session['app_group']))
        table_attrs = {'data' : data,
                        'title' : 'Last items entered in %s budget' % category_sql.capitalize()}
        category_table = html_table(table_attrs=table_attrs)

        # left in budget
        remaining = c.execute(queries['remaining_category_budget'], (session['app_group'], session['app_group'], category_sql))
        remaining_budget = []
        for thing in remaining:
            remaining_budget = thing[1]

        #spent by month
        m = c.execute(queries['category_spend_per_month'], (category_sql,session['app_group']))
        #need link /mnths/<mnth_num>/<category>
        table_attrs = {'data' : m,
                        'title' : 'Spend by Month in %s' % category_sql.capitalize(),
                        'link_col' : 'spend_month',
                        'link_func' : mnth_cat_link,
                        'link_path' : url_for('mnths'),
                        'category' : category_sql}
        mnth_table = html_table(table_attrs=table_attrs)

        # Allocation_one_category
        aloc = c.execute(queries['allocation_one_category'], (category_sql,session['app_group']))
        table_attrs = {'data' : aloc,
                        'title' : 'Monthly Allocations'}
        aloc_table = html_table(table_attrs=table_attrs)

        return render_template('category.html', **locals())

@app.route('/mnths')
@app.route('/mnths/<mnth>')
@app.route('/mnths/<mnth>/<category>')
@login_required
def mnths(mnth=None, category=None):
        if mnth == None:
            recent_month = c.execute(queries['recent_month'],(session['app_group'],))
            for thing in recent_month:
                mnth = thing[0]

            #mnth = today.strftime("%Y%m")
        mnth = int(mnth)
        month_display = str(calendar.month_name[int(str(mnth)[4:6])]) + " " + str(mnth)[0:4]
        if category == None:
            title = "%s Report" % month_display
            spent = c.execute(queries['spent_in_month'], (mnth,session['app_group']))
            for thing in spent:
                month_spent = thing[0]

            #individual transactions recorded for month
            r = c.execute(queries['monthly_expenses'], (mnth,session['app_group']))
            table_attrs = {'data' : r,
                            'title' : 'Items entered in in %s' % month_display}
            mnth_table = html_table(table_attrs=table_attrs)
            # spent per category in month
            m = c.execute(queries['spent_per_category_in_month'], (mnth,session['app_group']))
            table_attrs = {'data' : m,
                            'title' : 'Spent in %s' % month_display,
                            'link_col' : 'category',
                            'link_func' : cat_mnth_link,
                            'link_path' : url_for('mnths'),
                            'month': mnth}
            cat_mnth_table = html_table(table_attrs=table_attrs)

            mnths = c.execute(queries['mnths'], (session['app_group'],))
            link_list_attrs = {'data' : mnths,
                            'title' : 'Available Months',
                            'link_func' : num_link,
                            'link_path' : url_for('mnths')}
            mnth_list = link_list(link_list_attrs)
            return render_template('mnth.html', **locals())
        else:
            spent = c.execute(queries['spent_in_month_category'], (mnth, category, session['app_group']))
            for thing in spent:
                month_spent = thing[0]
            r = c.execute(queries['monthly_expenses_category'], (mnth, session['app_group'], category))
            table_attrs = {'data' : r,
                'title' : 'Items entered in %s in %s' % (category, month_display)}
            expense_table = html_table(table_attrs=table_attrs)
            return render_template('mnth_category.html', **locals())

@app.route('/reconcile')
@app.route('/reconcile/<mnth>')
@login_required
def reconcile(mnth=None):
        today = date.today()
        if mnth == None:
            if today.month == 1:
                last_month = 12
                last_month_year = today.year -1
            else:
                last_month = today.month -1
                last_month_year = today.year
            mnth = last_month_year*100+last_month
        mnth = int(mnth)
        month_display = str(calendar.month_name[int(str(mnth)[4:6])]) + " " + str(mnth)[0:4]
        title = "%s Report" % month_display

        #spent
        spent = c.execute(queries['spent_in_month'], (mnth, session['app_group']))
        table_attrs = {'data' : spent,
                        'title' : 'Money spent in %s' % month_display}
        month_spent = html_table(table_attrs=table_attrs)

        #remaining money in budget
        rm = c.execute(queries['remaining_budget_month'], (mnth, session['app_group'], mnth, session['app_group']))
        table_attrs = {'data' : rm,
                        'title' : 'Money left at the end of %s' % month_display}
        budget_money = html_table(table_attrs=table_attrs)

        #rogue budgets
        rb = c.execute(queries['rogue_spend_month'], (mnth,session['app_group']))
        table_attrs = {'data' : rb,
                        'title' : 'Rogue budgets for %s' % month_display}
        rogue = html_table(table_attrs=table_attrs)

        #budgets remaining
        br = c.execute(queries['remaining_budget_by_category_month'], (mnth, session['app_group'], mnth, session['app_group']))
        table_attrs = {'data' : br,
                        'title' : 'Money left in each category for %s' % month_display}
        category_budget_remaining = html_table(table_attrs=table_attrs)

        #individual transactions recorded for month
        r = c.execute(queries['monthly_expenses'], (mnth,session['app_group']))
        table_attrs = {'data' : r,
                        'title' : 'Items entered in in %s' % month_display}
        mnth_table = html_table(table_attrs=table_attrs)

        # spent per category in month
        m = c.execute(queries['spent_per_category_in_month'], (mnth,session['app_group']))
        table_attrs = {'data' : m,
                        'title' : 'Spent in %s' % month_display,
                        'link_col' : 'category',
                        'link_func' : cat_mnth_link,
                        'link_path' : url_for('mnths'),
                        'month': mnth}
        cat_mnth_table = html_table(table_attrs=table_attrs)

        mnths = c.execute(queries['mnths'],(session['app_group'],))
        link_list_attrs = {'data' : mnths,
                        'title' : 'Available Months',
                        'link_func' : num_link,
                        'link_path' : url_for('reconcile')}
        mnth_list = link_list(link_list_attrs)
        return render_template('reconcile.html', **locals())

@app.route("/budget/summary")
@login_required
def budget_sum():

    r1 = c.execute(queries['remaining_budget'], (session['app_group'], session['app_group']))
    table_attrs = {'data' : r1,
                   'title' : 'Budget Remaining'}
    rem_table = html_table(table_attrs=table_attrs)

    r = c.execute(queries['remaining_budget_by_category'], (session['app_group'],session['app_group']))
    table_attrs = {'data' : r,
                   'title' : 'Budget Remaining per Cateogy',
                   'link_col' : 'category',
                   'link_func' : std_link,
                   'link_path' : url_for('category')}
    bud_table = html_table(table_attrs=table_attrs)

    a = c.execute(queries['allocations_by_category'], (session['app_group'],))
    table_attrs = {'data' : a,
                   'title' : 'Monthly Allocations by Category',
                   'link_col' : 'category',
                   'link_func' : std_link,
                   'link_path' : url_for('category')}
    aloc_table = html_table(table_attrs=table_attrs)

    m = c.execute(queries['spend_per_month'], (session['app_group'],))
    table_attrs = {'data' : m,
                   'title' : 'Spent per Month',
                   'link_col' : 'spend_month',
                   'link_func' : num_link,
                   'link_path' : url_for('mnths')}
    month_table = html_table(table_attrs=table_attrs)

    return render_template(
        'budget_sum.html',**locals())

@app.route("/garage")
@app.route("/garage/<string:gdoor>")
@login_required
def garage_action(gdoor=None):
    garage_door_names = {'a':0,'b':1}
    garage_state_names = {0:'closed',1:'open'}
    garage_state_opposites = {0:'open',1:'close'}
    #get the garage states
    with open(os.path.join(remote_dir, 'garage_state.txt'), 'r') as file:
        garage_states_list = file.readline().split(',')
        garage_states = []
    for garage_state in garage_states_list:
        try:
            garage_states.append(int(garage_state))
        except:
            pass
    if gdoor == None:
        gdoor_a_state = garage_state_names[garage_states[0]].title()
        gdoor_a_action = garage_state_opposites[garage_states[0]].title()
        gdoor_b_state = garage_state_names[garage_states[1]].title()
        gdoor_b_action = garage_state_opposites[garage_states[1]].title()
        return render_template('garage.html',**locals())
    #open/close garage door
    elif gdoor.lower() in('a','b'):
        if session['garage_access'] == 1:
            if garage_states[garage_door_names[gdoor.lower()]] == 0:
                garage_action_text = "Opening garage door %s" % gdoor.upper()
            else:
                garage_action_text = "Closing garage door %s" % gdoor.upper()
            remote(server="garage",command='run', file='garage_open.py',action=gdoor.lower())
        else:
            garage_action_text = "Sorry, you don't have access to control the garage doors"
        return render_template('garage_act.html',**locals())

@app.route('/budget/search', methods=['GET', 'POST'])
@login_required
def search():
    form = Search()
    if form.validate_on_submit():
        p = '%'
        search_string = '%s%s%s' % (p,form.search_string.data,p)
        s = db_data('search', (search_string, search_string, session['app_group']))
        table_attrs = {'data' : s,
                   'title' : 'Budget Entries matching serarch term "%s"' % form.search_string.data}
        search_table = html_table(table_attrs=table_attrs)
        return render_template('search.html', **locals())
    return render_template('auto_form.html', title = 'Search for Budget Entries', form=form)

@app.route("/budget/action/bud", methods=['GET', 'POST'])
@login_required
def bud():
    today = date.today()
    today2 = today.strftime('%Y-%m-%d')
    categories = db_list(yaml_query='categories', vars=(session.get('app_group'),), tuples=True)
    form = BudAddMod()
    form.category.choices=categories
    if form.validate_on_submit():
        amount = form.amount.data*100
        db_submit('bud',(today2,form.category.data.lower(),amount,form.notes.data,session['app_group']))
        flash_text = "You submited an expense for %s to %s totaling %s" % (form.notes.data, form.category.data, form.amount.data)
        flash(flash_text)
        return redirect(url_for('actions'))
    return render_template('auto_form.html', title='Budget Entry', form=form)

@app.route("/budget/action/add", methods=['GET', 'POST'])
@login_required
def add():
    today = date.today()
    today2 = today.strftime('%Y-%m-%d')
    categories = db_list(yaml_query='categories', vars=(session.get('app_group'),), tuples=True)
    form = BudAddMod()
    form.category.choices=categories
    if form.validate_on_submit():
        amount = form.amount.data*100
        db_submit('add',(today2,form.category.data.lower(),amount,form.notes.data,session['app_group']))
        flash_text = "You added $%s into %s with these notes: %s" % (form.amount.data, form.category.data, form.notes.data)
        flash(flash_text)
        return redirect(url_for('actions'))
    return render_template('auto_form.html', title='Add Money to Budget', form=form)

@app.route("/budget/action/mod", methods=['GET', 'POST'])
@login_required
def mod():
    today = date.today()
    today2 = today.strftime('%Y-%m-%d')
    categories = db_list(yaml_query='categories', vars=(session.get('app_group'),), tuples=True)
    form = BudAddMod()
    form.category.choices=categories
    if form.validate_on_submit():
        amount = form.amount.data*100
        db_submit('mod1',(form.category.data.lower(),session['app_group']))
        db_submit('mod2',(today2,form.category.data.lower(),amount,form.notes.data,1,session['app_group']))
        flash_text = "You modified the monthly allocation for %s to $%s per month with thest notes: %s" % (form.category.data, form.amount.data, form.notes.data)
        flash(flash_text)
        return redirect(url_for('actions'))
    return render_template('auto_form.html', title='Monthly Allocation Adjustment', form=form)

@app.route("/budget/action/move", methods=['GET', 'POST'])
@login_required
def move():
    today = date.today()
    today2 = today.strftime('%Y-%m-%d')
    categories = db_list(yaml_query='categories', vars=(session.get('app_group'),), tuples=True)
    form = Move()
    form.from_category.choices=categories
    form.to_category.choices=categories
    if form.validate_on_submit():
        amount = form.amount.data*100
        amount_neg = 0-amount
        rem_notes = 'moved to ' + form.to_category.data
        db_submit('move',(today2,form.from_category.data.lower(),amount_neg,rem_notes,session['app_group']))
        add_notes = 'moved from ' + form.from_category.data
        db_submit('move',(today2,form.to_category.data.lower(),amount,add_notes,session['app_group']))
        flash_text = "You moved $%s from %s to %s" % (form.amount.data, form.from_category.data, form.to_category.data)
        flash(flash_text)
        return redirect(url_for('actions'))
    return render_template('auto_form.html', title='Move Money from one Budget to Anothert', form=form)

@app.route("/budget/action/update", methods=['GET', 'POST'])
@login_required
def upd():
    categories = db_list(yaml_query='categories', vars=(session.get('app_group'),), tuples=True)
    #rogue = db_list(yaml_query='rogue', vars=(session.get('app_group'),), tuples=True)
    form = Update()
    #form.from_category.choices = rogue
    form.from_category.choices = categories
    form.to_category.choices = categories
    if form.validate_on_submit():
        db_submit('upd',(form.to_category.data.lower(), form.from_category.data,session.get('app_group')))
        db_submit('upd2',(form.to_category.data.lower(), form.from_category.data,session.get('app_group')))
        db_submit('upd3',(form.to_category.data.lower(), form.from_category.data,session.get('app_group')))
        flash_text = "You updated everything in %s to %s" % (form.from_category.data, form.to_category.data)
        flash(flash_text)
        return redirect(url_for('actions'))
    return render_template('auto_form.html', title='Move all items in a Category to Another Category', form=form)

@app.route("/budget/action/delete", methods=['GET', 'POST'])
@login_required
def delete():
    form = Delete()
    if form.validate_on_submit():
        db_submit('del', (form.id.data,))
        flash_text = "You deleted the entry with id number %s" % form.id.data
        flash(flash_text)
        return redirect(url_for('actions'))
    return render_template('auto_form.html', title='Delete Budget Entry', form=form)

@app.route("/budget/action/new", methods=['GET', 'POST'])
@login_required
def new():
    today = date.today()
    today2 = today.strftime('%Y-%m-%d')
    form = New()
    if form.validate_on_submit():
        notes = 'category added'
        amount = 0
        db_submit('bud', (today2,form.category.data.lower(),amount,notes,session.get('app_group')))
        db_submit('add', (today2,form.category.data.lower(),amount,notes,session.get('app_group')))
        flash_text = "You created a new category called %s" % form.category.data
        flash(flash_text)
        return redirect(url_for('actions'))
    return render_template('auto_form.html', title='Create New Budget Category', form=form)


@app.route("/budget/action")
@login_required
def actions():
    return render_template('actions.html', title="Available Budget Actions")

@app.route("/maintenance/action")
@login_required
def maint_actions():
    return render_template('maint_actions.html', title="Available Maintenance Actions")

@app.route("/maintenance/machine", methods=['GET', 'POST'])
@login_required
def machine():
    today = date.today()
    today2 = today.strftime('%Y-%m-%d')
    form = Machine()
    if form.validate_on_submit():
        db_submit('machine', (today2, form.machine.data.lower(), form.machine_type.data, form.purchase_date.data, int(form.miles_applicable.data), form.avg_miles_year.data, form.miles.data, 1, session.get('app_group')))
        flash_text = 'you added a new machine to your fleet called %s' % form.machine.data
        flash(flash_text)
        return render_template('maint_actions.html', title="Available Maintenance Actions")
    return render_template('auto_form.html', title='Add a New Machine to Maintain', form=form)

@app.route("/maintenance/maintenance", methods=['GET', 'POST'])
@login_required
def maintenance():
    today = date.today()
    today2 = today.strftime('%Y-%m-%d')
    machines = db_list(yaml_query='machines', vars=(session.get('app_group'),), tuples=True)
    form = Maint()
    form.machine.choices = machines
    if form.validate_on_submit():
        service = 'unknown'
        category = 'unknown'
        db_submit('maint', (today2, form.machine.data.lower(), form.miles.data, form.notes.data, category, service, session.get('app_group')))
        flash_text = 'you added a maintenance record for %s' % form.machine.data
        flash(flash_text)
        return render_template('maint_actions.html', title="Available Maintenance Actions")
    return render_template('auto_form.html', title='Log Maintenance', form=form)

@app.route("/maintenance/maint_schedule", methods=['GET', 'POST'])
@login_required
def maint_schedule():
    today = date.today()
    today2 = today.strftime('%Y-%m-%d')
    machines = db_list(yaml_query='machines', vars=(session.get('app_group'),), tuples=True)
    category = [('sched_maint','Scheduled Maintenance'),('fix','Fix')]
    service = [('oil_change','Oil Change'),('trans_drain','Transmission Drain and Fill')]
    form = MaintenanceSchedule()
    form.machine.choices = machines
    form.category.choices = category
    form.service.choices = service
    if form.validate_on_submit():
        service = 'unknown'
        category = 'unknown'
        db_submit('maint_schedule', (form.machine.data.lower(), form.category.data.lower(), form.service.data, form.frequency_type.data, form.frequency.data, 1,  session.get('app_group')))
        flash_text = 'you added a maintenance schedule record'
        flash(flash_text)
        return render_template('maint_actions.html', title="Available Maintenance Actions")
    return render_template('auto_form.html', title='Add Maintenance Schedule', form=form)
