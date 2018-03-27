###############################
####### SETUP (OVERALL) #######
###############################

## Import statements

import os
import requests
import json

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import ValidationError
from wtforms.validators import Required # Here, too
from flask_sqlalchemy import SQLAlchemy


## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY'] = 'wingardiumleviOsa'
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL') or "postgresql://localhost/si364midterm"
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/si364midterm"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['HEROKU_ON'] = os.environ.get('HEROKU')


## Statements for db setup (and manager setup if using Manager)
manager = Manager(app)

db = SQLAlchemy(app)

######################################
######## HELPER FXNS (If any) ########
######################################

def get_or_create_house(db_session, house_name):
    house = db_session.query(HogwartsHouses).filter_by(name=house_name).first()
    if house:
        return house
    else:
        house = HogwartsHouses(name=house_name)
        db_session.add(house)
        db_session.commit()
        return house

def get_or_create_student(db_session, student_name, student_house, student_patronus):
    student = db_session.query(HogwartsStudents).filter_by(name=student_name).first()
    if student:
        return student
    else:
        house = get_or_create_house(db_session, student_house)
        student = HogwartsStudents(name=student_name, house=house.id, patronus=student_patronus)
        db_session.add(student)
        db_session.commit()
        return student

def get_or_create_new_house(db_session, house_name):
    house = db_session.query(NewHouses).filter_by(name=house_name).first()
    if house:
        return house
    else:
        house = NewHouses(name=house_name)
        db_session.add(house)
        db_session.commit()
        return house

def get_or_create_new_student(db_session, student_name, student_house, student_patronus):
    new_student = db_session.query(NewStudents).filter_by(name=student_name).first()
    if new_student:
        return new_student
    else:
        house = get_or_create_new_house(db_session, student_house)
        new_student = NewStudents(name=student_name, house=house.id, patronus=student_patronus)
        db_session.add(new_student)
        db_session.commit()
        return new_student

##################
##### MODELS #####
##################

# class Name(db.Model):
#     __tablename__ = "names"
#     id = db.Column(db.Integer,primary_key=True)
#     name = db.Column(db.String(64))

#     def __repr__(self):
#         return "{} (ID: {})".format(self.name, self.id)

class HogwartsStudents(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    house = db.Column(db.Integer,db.ForeignKey("houses.id"))
    patronus = db.Column(db.String(64))
    #actor = db.Column(db.String(64))

    def __repr__(self):
        return "{} - {} - {}".format(self.name, self.house, self.patronus)

class HogwartsHouses(db.Model):
    __tablename__ = "houses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

class NewStudents(db.Model):
    __tablename__ = "newstudents"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    house = db.Column(db.Integer,db.ForeignKey("newhouses.id"))
    patronus = db.Column(db.String(64))
    #actor = db.Column(db.String(64))

    def __repr__(self):
        return "{} - {} - {}".format(self.name, self.house, self.patronus)

class NewHouses(db.Model):
    __tablename__ = "newhouses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

###################
###### FORMS ######
###################

# class NameForm(FlaskForm):
#     name = StringField("Please enter your name.",validators=[Required()])
#     submit = SubmitField()

class HogwartsStudentForm(FlaskForm):
    name = StringField("Enter the name of a Hogwarts Student: ",validators=[Required()])
    def validate_name(form, field):
        if " " not in field.data:
            raise ValidationError("Please enter the first and last name separated by a space")
    house = StringField("Enter the Hogwarts house of the student above: ", validators=[Required()])
    submit = SubmitField()

class NewStudentForm(FlaskForm):
    name = StringField("Enter a name of a new Hogwarts Student: ",validators=[Required()])
    def validate_name(form, field):
        if " " not in field.data:
            raise ValidationError("Please enter a first and last name separated by a space")
    house = StringField("Enter a Hogwarts House for this student: ", validators=[Required()])
    patronus = StringField("Enter an animal for their patronus: ", validators=[Required()])
    #actor = StringField("Enter an actor to play this student in a movie adaption: ",validators=[Required()])
    submit = SubmitField()


#######################
###### VIEW FXNS ######
#######################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# @app.route('/',methods=["GET","POST"])
# def home():
#     form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
#     if form.validate_on_submit():
#         name = form.name.data
#         newname = Name(name)
#         db.session.add(newname)
#         db.session.commit()
#         return redirect(url_for('all_names'))
#     return render_template('base.html',form=form)

# @app.route('/names')
# def all_names():
#     names = Name.query.all()
#     return render_template('name_example.html',names=names)

@app.route('/',methods=["GET","POST"])
def hogwarts():
    form = HogwartsStudentForm()
    students_list = []
    if form.validate_on_submit():
        form_name = form.name.data
        form_house = form.house.data

        base_url = "https://www.potterapi.com/v1/"
        hp_api_key = "$2a$10$XPnZrHnIYgf.R9etCbM/8eHqwCnygF9MlSVbcVA4wDlPsIZpwsZa2"

        params = {"key":hp_api_key,"name": form_name,"house":form_house}
        response = requests.get(base_url+"characters", params=params)
        hp_list = json.loads(response.text) # list of dictonaries (should only be one for each character)

        student_name = hp_list[0]["name"]
        student_house = form_house
        if "patronus" in hp_list[0]:
            student_patronus = hp_list[0]["patronus"]
        else:
            student_patronus = "No known patronus"

        # get or create HogwartsStudent
        student = get_or_create_student(db.session, student_name=student_name, student_house=student_house, student_patronus=student_patronus)
        student_tup = (student, student_house)

        # pass to template
        return render_template('home.html',form=form, student=student_tup)

    flash(form.errors)
    return render_template('home.html',form=form, students=students_list)

@app.route('/show_hogwarts_students')
def show_hogwarts_students(): 
    students = HogwartsStudents.query.all()
    student_tups = []
    for s in students:
        house = HogwartsHouses.query.filter_by(id=s.house).first()
        student_tups.append((s, house))


    return render_template('show_students.html',students=student_tups)

@app.route('/add_student')
def add_new_student():
    form = NewStudentForm()
    flash(form.errors)
    return render_template('add_student.html',form=form)

@app.route('/new_students',methods=["GET"])
def new_students():
    if request.method == "GET":
        result_str = ""
        for k in request.args:
            result_str += "{} - {}<br><br>".format(k, request.args.get(k,"")) # get the key, value from args

        # PULL OUT NAME, HOUSE, PATRONUS FROM requests.args
        student_name = request.args.get("name","")
        student_house = request.args.get("house","")
        student_patronus = request.args.get("patronus","")

        # PASS TO get_or_create_new_stduent --> WRITE get_or_create_new_student/get_or_create_new_house
        student = get_or_create_new_student(db.session,student_name=student_name, student_house=student_house, student_patronus=student_patronus)

        # MAKE A REQUEST TO SHOW ALL NEW STUDENTS ADDED
        students_list = NewStudents.query.all()
        student_tups = []
        for s in students_list:
            house = HogwartsHouses.query.filter_by(id=s.house).first()
            student_tups.append((s, house))
        # MAYBE ADD A NEW PAGE THAT SHOWS ALL NEW STUDENTS WITHOUT HAVING TO MAKE A NEW STUDENT

        #return render_template(args = )
        return render_template('new_students.html',student=student,students=student_tups)

@app.route('/show_new_students')
def show_new_students():
    students = NewStudents.query.all()

    student_tups = []
    for s in students:
        house = NewHouses.query.filter_by(id=s.house).first()
        student_tups.append((s, house))

    return render_template('show_new_students.html',students=student_tups)

## Code to run the application...
if __name__ == '__main__':
    db.create_all()
    manager.run()

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
