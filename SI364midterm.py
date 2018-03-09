###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
import requests
import json

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField# Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required # Here, too
from flask_sqlalchemy import SQLAlchemy


## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecurebutitsok'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/si364midterm_test"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


## Statements for db setup (and manager setup if using Manager)
manager = Manager(app)

db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################





##################
##### MODELS #####
##################

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)

class HogwartsStudents(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    house = db.Column(db.Integer,db.ForeignKey("houses.id"))
    patronus = db.Column(db.String(64))
    actor = db.Column(db.String(64))

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
    actor = db.Column(db.String(64))

class NewHouses(db.Model):
    __tablename__ = "newhouses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))


###################
###### FORMS ######
###################

class NameForm(FlaskForm):
    name = StringField("Please enter your name.",validators=[Required()])
    submit = SubmitField()

class HogwartsStudentForm(FlaskForm):
    name = StringField("Enter the name of a Hogwarts Student: ",validators=[Required()])
    def validate_name(form, field):
        if " " not in field:
            raise ValidationError("Please enter the first and last name separated by a space")
    house = StringField("Enter the Hogwarts house of the student above: ", validators=[Required()])
    submit = SubmitField()

class NewForm(FlaskForm):
    name = StringField("Enter a name of a new Hogwarts Student: ",validators=[Required()])
    def validate_name(form, field):
        if " " not in field:
            raise ValidationError("Please enter a first and last name separated by a space")
    house = StringField("Enter a Hogwarts House for this student: ", validators=[Required()])
    patronus = StringField("Enter an animal for their patronus: ", validators=[Required()])
    actor = StringField("Enter an actor to play this student in a movie adaption: ",validators=[Required()])
    submit = SubmitField()


#######################
###### VIEW FXNS ######
#######################

@app.route('/',methods=["GET","POST"])
def home():
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        name = form.name.data
        newname = Name(name)
        db.session.add(newname)
        db.session.commit()
        return redirect(url_for('all_names'))
    return render_template('base.html',form=form)

@app.route('/names')
def all_names():
    names = Name.query.all()
    return render_template('name_example.html',names=names)

@app.route('/hogwarts')
def hogwarts():
    form = HogwartsStudentForm()
    if form.validate_on_submit():
        student_name = form.name.data
        student_house = form.house.data

        base_url = "https://www.potterapi.com/v1/"
        hp_api_key = "$2a$10$XPnZrHnIYgf.R9etCbM/8eHqwCnygF9MlSVbcVA4wDlPsIZpwsZa2"

        params = {"key":hp_api_key,"name": "Harry Potter"}
        response = requests.get(base_url+"characters", params=params)
        hp_list = json.loads(response.text)

        # get or create HogwartsStudent

        # pass too template --> if list, for each student in list


    return hp_list[0]["house"]

    #return render_template('home.html',form=form)




## Code to run the application...
if __name__ == '__main__':
    db.create_all()
    manager.run()

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
