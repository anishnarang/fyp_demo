from flask import render_template, redirect, url_for, request
from . import main

# from forms import CategoryForm,TaskForm
# from .. import Category,Task
import os
import random
from .. import app

def getRandomImages():
	images = []
	l = eval(app.open_resource('static/images.txt').read())
	for i in range(9):
		r = random.randint(0,len(l)-1)
		images.append(l[r])
	return images

@main.route("/",methods=['GET','POST'])
def index():
	# q = train_test.test('other')
	#print os.popen("pwd")
	img_annotations = eval(open('app/main/annotations.txt').read())
	q = os.popen("python app/main/code/RNN/enc_dec/train_test.py multiple other clothing").read()
	print q
	#choices_list = ["Option1;Option2;Option3;Option4" for i in range(9)]
	choices_list = []
	answer_choices=["Option1","Option2","Option3","Option4"]
	image_list = getRandomImages()
	question_list = []
	ans_list = []
	for img in image_list:
		question_list.append(os.popen("python app/main/code/RNN/enc_dec/train_test.py single " + img_annotations[img.split(".")[0]][0][0]).read())
		ans_list.append(img_annotations[img.split(".")[0]][0][1])
		choices_list.append(img_annotations[img.split(".")[0]][0][1])
		
	print question_list
	if request.method=='POST' and request.form['submit']:
		for ch in answer_choices:
			if ch in dict(request.form).keys():
				print "Selected Option:",ch
				return render_template("index.html",choices_list=choices_list,question_list=question_list,image_list=image_list,alert_message="That is the correct answer!",alert_type='info')
		else:
			return render_template("index.html",choices_list=choices_list,image_list=image_list,question_list=question_list,alert_message="That is the wrong answer!",alert_type='danger')
	return render_template("index.html",choices_list=choices_list,image_list=image_list,question_list=question_list)

# @main.route("/add_category",methods=['GET','POST'])
# def add_category():
# 	form = CategoryForm()
# 	name = None
# 	if form.validate_on_submit():
# 		name = form.name.data
# 		form.name.data = ''
# 		db.session.add(Category(name=name))
# 		db.session.commit()
# 	return render_template('category_form.html', form=form, name=name)

# @main.route("/add_task",methods=['GET','POST'])
# def add_task():
# 	name = None
# 	category = None
# 	priority = None
# 	form = TaskForm()
# 	form.getChoices()

# 	if form.validate_on_submit():
# 		name = form.name.data
# 		category = form.category.data
# 		priority = form.priority.data
# 		if priority == "p1":
# 			priority_name = "HIGH"
# 		elif priority == "p2":
# 			priority_name = "NORMAL"
# 		else:
# 			priority_name = "LOW"

# 		form.name.data = ''
# 		db.session.add(Task(category=category, name=name, priority=priority_name))
# 		db.session.commit()
# 	return render_template('task_form.html', form=form, name=name, priority=priority, category=category)

# @main.route("/view_tasks",methods=['GET','POST'])
# def view_tasks():
# 	tasks = {"Task1":{"Category":"c2","Priority":"Low"}, "Task2":{"Category":"c1","Priority":"High"}, "Task3":{"Category":"c3","Priority":"Medium"}}
# 	res = Task.query.all()
# 	tasks = {}
# 	for item in res:
# 		tasks[item.name] = {"Category":item.category, "Priority":item.priority}
# 	new = False
# 	if len(tasks) == 0:
# 		new = True
# 	return render_template('view_tasks.html', tasks=tasks, new=new)