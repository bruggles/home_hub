from flask import session
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, FloatField, StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import Regexp, ValidationError, DataRequired, Email, EqualTo, Optional, NumberRange, Length
from app_contents.models import User
from app_contents.functions import db_list
import phonenumbers

def Phone(form, field):
    if len(field.data) > 14:
        raise ValidationError('Invalid phone number.')
    try:
        input_number = phonenumbers.parse(field.data)
        raise ValidationError('Leave the +1 off the phone number')
    except:
        input_number = phonenumbers.parse("+1"+field.data)
        if not (phonenumbers.is_valid_number(input_number)):
            raise ValidationError('Invalid phone number.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    app_groups = [('manderson','Mark Anderson'),('bruggles','Brandon Ruggles')]
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_num = StringField('Phone Number', validators=[DataRequired(), Phone])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    app_group = SelectField('Application Group', choices = app_groups, validators=[DataRequired()])
    access_key = StringField('Access Key', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class Search(FlaskForm):
    search_string = StringField('Search String', validators=[DataRequired()])
    submit = SubmitField('Search')

class BudAddMod(FlaskForm):
    #categories = db_list(yaml_query='categories', vars=(session.get('app_group'),), tuples=True)
    category = SelectField('Budget', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    notes = StringField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Move(FlaskForm):
    #categories = db_list(yaml_query='categories', vars=(session.get('app_group'),), tuples=True)
    amount = FloatField('Amount', validators=[DataRequired()])
    from_category = SelectField('From Category',  validators=[DataRequired()])
    to_category = SelectField('To Category',  validators=[DataRequired()])
    submit = SubmitField('Move Money')

class Update(FlaskForm):
    #categories = db_list(yaml_query='categories', vars=(session.get('app_group'),), tuples=True)
    #rogue = db_list(yaml_query='rogue', vars=(session.get('app_group'),session.get('app_group')), tuples=True)
    from_category = SelectField('From Category', validators=[DataRequired()])
    to_category = SelectField('To Category', validators=[DataRequired()])
    submit = SubmitField('Update Budget Allocation')

class Delete(FlaskForm):
    id = IntegerField('ID to Delete', validators=[DataRequired()])
    submit = SubmitField('Delete Entry')

class New(FlaskForm):
    category = StringField('New Category', validators=[DataRequired(),Regexp(r'^[\w-]+$')])
    submit = SubmitField('Create New Category')

class Income(FlaskForm):
    description = StringField('Income Description  (brief ie. Brandon Work)', validators=[DataRequired()])
    account = SelectField('Account income goes to', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    income_type = SelectField('Income Type', choices = [('static','Static Income'),('variable_amt','Variable Amount'),('variable_cnt','Variable Count')],validators=[DataRequired()])
    income_tax = SelectField('Tax Applied', choices = [('pre_tax','Pre-Tax'),('post_tax','Post-Tax'),('tax_refund','Tax Refund')],validators=[DataRequired()])
    notes = StringField('Notes', validators=[DataRequired()])

class RecurringExpenses(FlaskForm):
    description = StringField('Expense Description', validators=[DataRequired()])
    account = SelectField('Account expense comes from', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    percentage = FloatField('Percentage (only if expense type is a percent type otherwise 0)', validators=[DataRequired()])
    expense_type = SelectField('Expense Type', choices = [('static','Static Expense'),('variable_amt','Variable Expense'),('variable_cnt','Variable Count'),('post_tax_percent','Post Tax Income Percent'),('pre_tax_percent','Pre Tax Income Percent')],validators=[DataRequired()])
    notes = StringField('Notes', validators=[DataRequired()])


class Account(FlaskForm):
    account = StringField('Account income goes to', validators=[DataRequired()])
    account_type = SelectField('Account Type', choices = [('working_savings','Working Savings'),('checking','Checking'),('credit_card','Credit Card')],validators=[DataRequired()])
    min_amount = FloatField('Minimum Amount', validators=[DataRequired()])


class Machine(FlaskForm):
    machine = StringField('Machine', validators=[DataRequired()])
    machine_type = SelectField('Machine Type', choices = [('home','Home'),('car','Car'),('yard_equipment','Yard Equipment')],validators=[DataRequired()])
    miles_applicable = SelectField('Miles Applicable', choices = [('1','Yes'),('0','No')], validators=[DataRequired()])
    miles = IntegerField('Miles When Purchased', validators=[Optional()])
    avg_miles_year = IntegerField('Average Miles per Year', validators=[Optional()])
    purchase_date = DateField('Purchase Date', format='%m/%d/%Y', validators=[DataRequired()])
    submit = SubmitField('Add new Machine')

class Maint(FlaskForm):
    machine = SelectField('Machine', validators=[DataRequired()])
    miles = IntegerField('Miles', validators=[Optional()])
    notes = StringField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit Maintenance Record')

class MaintenanceSchedule(FlaskForm):
    machine = SelectField('Machine', validators=[DataRequired()])
    category = SelectField('Category', validators=[DataRequired()])
    service = SelectField('Service', validators=[DataRequired()])
    frequency_type = SelectField('Frequency Type', validators=[DataRequired()], choices = [('miles','Miles'),('months','Months')])
    frequency = IntegerField('Frequency', validators=[DataRequired()])
    submit = SubmitField('Add item to Maintenance Schedule')

