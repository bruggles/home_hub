import os, yaml, sqlite3, subprocess
from twilio.rest import Client
from dotenv import load_dotenv

app_contents = os.path.abspath(os.path.dirname(__file__))
repo_dir = os.path.abspath(os.path.join(app_contents, '../..'))

load_dotenv(os.path.join(repo_dir,'vars.env'))

with open(os.path.join(app_contents, 'queries.yml'), 'r') as file:
        queries = yaml.load(file, Loader=yaml.FullLoader)
DB_STRING = os.path.join(app_contents,'home_hub.db')

def db_data(yaml_query, vars=None, rows=True):
    conn = sqlite3.connect(DB_STRING, check_same_thread=False)
    if rows:
        conn.row_factory = sqlite3.Row # this powers some of the row functionality
    c = conn.cursor()
    if vars == None:
        data = c.execute(queries[yaml_query])
    else:
        data = c.execute(queries[yaml_query], vars)
    #c.close()
    #conn.close()
    return data

def db_submit(yaml_query, vars=None):
    conn = sqlite3.connect(DB_STRING, check_same_thread=False)
    c = conn.cursor()
    if vars == None:
        c.execute(queries[yaml_query])
    else:
        c.execute(queries[yaml_query], vars)
    conn.commit()
    c.close()
    conn.close()

def db_list(yaml_query, vars=None, tuples=False):
    data = db_data(yaml_query, vars)
    rows = data.fetchall()
    list = [] 
    if tuples:
        for row in rows:
            first = tuple(row)[0]
            second = tuple(row)[0].replace("_"," ").title()
            list.append(tuple((first,second)))
    else:
        for row in rows:
            list.append(tuple(row)[0])
    return list

def text_send(body, to):
    account_sid = os.environ.get('TWILIO_SID')
    auth_token = os.environ.get('TWILIO_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE')
    client = Client(account_sid, auth_token)
    message = client.messages.create(body=body, from_=from_number, to=to)
    return message.sid

# links to bue used anywhere
def std_link(path, value, category, month):
    link = '<a href="%s/%s">%s</a>' % (path,value,value.capitalize())
    return link
def num_link(path, value, category, month):
    link = '<a href="%s/%s">%s</a>' % (path,value,value)
    return link
def mnth_cat_link(path, value, category, month):
    link = '<a href="%s/%s/%s">%s</a>' % (path,value,category,value)
    return link
def cat_mnth_link(path, value, category, month):
    link = '<a href="%s/%s/%s">%s</a>' % (path,month,value,value)
    return link

def html_table(table_attrs):
    q = table_attrs['data']
    title = table_attrs.get('title')
    link_col = table_attrs.get('link_col')
    link_func = table_attrs.get('link_func',std_link)
    link_path = table_attrs.get('link_path')
    cat = table_attrs.get('category')
    mnth = table_attrs.get('month')
    rows = q.fetchall()
    try:
        columns = rows[0].keys()
    except:
        columns = ['no data']

    if title:
        title = "<h2>" + title + "</h2>"
        headers = title + "<table><tr>"
    else:
        headers = "<table><tr>"

    if link_col:
        for n, col in enumerate(columns):
            if col == link_col:
                link_col_num = n
    else:
         link_col_num = -1

    for column in columns:
        header = "<th>" + column.replace("_"," ").title() + "</th>"
        headers = headers + header
    headers = headers + "</tr>"
    html_rows = ""

    for row in rows:
        html_row = "<tr>"
        for n, cell in enumerate(tuple(row)):
            if n == link_col_num:
                cell = link_func(path=link_path, value=cell, category=cat, month=mnth)
            html_row = html_row + "<td>%s</td>" % cell
        html_row = html_row + "</tr>"
        html_rows = html_rows + html_row
    html_table = headers + html_rows + "</table>"
    return html_table

def link_list(link_list_attrs):
    q = link_list_attrs['data']
    title = link_list_attrs.get('title')
    #link_col = link_list_attrs.get('link_col')
    link_func = link_list_attrs.get('link_func',std_link)
    link_path = link_list_attrs.get('link_path')
    cat = link_list_attrs.get('category')
    mnth = link_list_attrs.get('month')
    rows = q.fetchall()
    #columns = rows[0].keys()

    if title:
        title = "<h2>%s</h2>" % title
        list_rows = title + "<ul>"
    else:
        list_rows = "<ul>"

    for row in rows:
        cell = link_func(path=link_path, value=tuple(row)[0], category=cat, month=mnth)
        list_row = "<li>%s</li>" % cell
        list_rows = list_rows + list_row
    list = list_rows + "</ul>"
    return list

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def delimited_table(data, delimiter = ': '):
    rows = data.fetchall()
    try:
        columns = rows[0].keys()
    except:
        columns = ['no data']
    headers = ''
    for column in columns:
        header = column.replace("_"," ").title() + delimiter
        headers = headers + header
    headers = rreplace(headers, delimiter, '', 1) + "\n"
    sms_rows = headers
    for row in rows:
        sms_row = ''
        for cell in tuple(row):
            sms_row = sms_row + "%s%s" % (cell, delimiter)
        sms_row = rreplace(sms_row, delimiter, '', 1) + "\n"
        sms_rows = sms_rows + sms_row
    return sms_rows

def sms_report(category = None, app_group = None):
    if app_group == None:
        sms_report = 'No App Group'
    else:
        if category == None:
            c = db_data('remaining_budget_by_category',vars=(app_group,app_group))
            l = db_data('sms_last',vars=(app_group,))
            title = 'Budget Report\n'
        else:
            category = category.lower()
            c = db_data('remaining_category_budget', vars=(app_group,app_group,category))
            l = db_data('sms_category_last', vars=(category,app_group))
            title = '%s Report\n' % category.capitalize()

        category_report = delimited_table(data=c)

        last_report = delimited_table(data=l)

        sms_report = '%s%s\n%s' % (title, category_report, last_report)
    return sms_report

def db_setup():
    db_submit('machine_schema')
    db_submit('maintenance_schema')
    db_submit('spent_schema')
    db_submit('budget_sum_schema')
    db_submit('budget_amt_schema')
    db_submit('maintenance_schedule_schema')
    db_submit('recurring_income_schema')
    db_submit('monthly_income_schema')
    db_submit('account_schema')
    db_submit('recurring_expenses_schema')
    db_submit('monthly_expenses_schema')
    db_submit('monthly_account_balances_schema')
    db_submit('monthly_budget_left_schema')
    db_submit('monthly_expense_count_schema')
    db_submit('monthly_income_count_schema')

db_setup()

def remote(server, command, action=None, location=None, file=None):
    if server == 'garage':
        server_addr = os.environ.get('GARAGE_ADDR')
    elif server == 'main':
        server_addr = os.environ.get('MAIN_ADDR')
    if location == None:
        location = "/home/pi/repos/home_hub/remote"
    if file == None:
        value = "No File Specified :-("
    else:
        if command == 'read':
            sub_list = ['ssh',server_addr,'cat',os.path.join(location,file)]
            value = subprocess.run(sub_list, stdout=subprocess.PIPE).stdout.decode('utf-8')
        elif command == 'run':
            sub_list = ['ssh',server_addr,'python3', os.path.join(location,file),action]
            subprocess.run(sub_list)
            value = 'success'
        elif command == 'run_read':
            sub_list = ['ssh',server_addr,'python3', os.path.join(location,file),action]
            value = subprocess.run(sub_list, stdout=subprocess.PIPE).stdout.decode('utf-8')
    return value
