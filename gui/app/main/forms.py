from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import Required, Length
# from wtforms.ext.sqlalchemy.fields import *
from . import main

# class CategoryForm(Form):
# 	name = StringField("Category Name",validators=[Required()])
# 	submit = SubmitField("CREATE")

class MainForm(Form):
	submit = SubmitField("SUBMIT")
	try_another = SubmitField("Try Another")
	

class Recaptcha(Form):
	recaptcha = SubmitField("ReCaptcha")

# class TaskForm(Form):
# 	name = StringField("Task Name",validators=[Required()])
# 	category = SelectField("Select Category",choices=[])
# 	priority = SelectField("Select Priority",choices=[('p1','High'), ('p2','Normal'), ('p3','Low')])
# 	submit = SubmitField("CREATE")

# 	def getChoices(self):
# 		l = Category.query.all()
# 		l = [(str(item.name),item.name) for item in l]
# 		self.category.choices = l
