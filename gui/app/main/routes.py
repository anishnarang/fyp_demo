from flask import render_template, redirect, url_for, request
from . import main
import os
import random
from .. import app
from PIL import Image
import datetime
from forms import *
import time
from app.main.code.RNN.enc_dec import train_test
from random import shuffle

count = 0
questions_dict = eval(open('app/main/test_questions.txt').read())
class_obj = eval(open('app/main/class_obj.txt').read())
img_annotations = eval(open('app/main/annotations.txt').read())
ALL_TUPLES = eval(open('app/main/code/flickr30k/all_tuples.txt').read())

def create_single_options(cls,obj_list):
	#obj_list is a list of 2 tuple annotations
	obj = [o[1].title() for o in obj_list]
	all_obj = class_obj[cls]
	shuffle(all_obj)
	ops = list(set(all_obj) - set(obj_list))
	shuffle(ops)
	res = ops[:3]

	return res

def create_multiple_options(all_obj):
	# ALL_TUPLES is a list of all possible tuples in the dataset
	# ALL_OBJ is a list of all possible objects in the dataset
	ALL_OBJ = list(zip(ALL_TUPLES))

	# Set difference between all possible objects and objects of the classes of the selected images
	ops = list(set(ALL_OBJ) - set(all_obj))

	# Shuffle them and return 4
	shuffle(ops)
	res = [r[0][1].title() for r in random.sample(ops,2)]

	return res

def make_composite(img1,img2,img3,img4):
	global count
	pic1 = Image.open("app/static/"+str(img1))
	pic2 = Image.open("app/static/"+str(img2))
	pic3 = Image.open("app/static/"+str(img3))
	pic4 = Image.open("app/static/"+str(img4))

	pic1 = pic1.resize((360, 300), Image.ANTIALIAS)
	pic2 = pic2.resize((360, 300), Image.ANTIALIAS)
	pic3 = pic3.resize((360, 300), Image.ANTIALIAS)
	pic4 = pic4.resize((360, 300), Image.ANTIALIAS)

	w1, h1 = pic1.size
	w2, h2 = pic2.size
	w3, h3 = pic3.size
	w4, h4 = pic4.size

	w = max(w1+w2,w3+w4)
	h = max(h1+h3,h2+h3)
	op_image = Image.new('RGB', (w, h))

	op_image.paste(pic1, (0,0))
	op_image.paste(pic2, (w1,0))
	op_image.paste(pic3, (0,h3))
	op_image.paste(pic4, (w1,h3))	

	count += 1
	op_image.save("app/static/multiple"+str(count)+".jpg")
	return "multiple"+str(count)+".jpg"

def getRandomImages(num):
	images = []
	l = eval(app.open_resource('static/images.txt').read())
	for i in range(num):
		r = random.randint(0,len(l)-1)
		images.append(l[r])
	return images

@main.route("/single",methods=['GET','POST'])
def index():
	global questions_dict,img_annotations

	choices_list = []
	image_list = getRandomImages(9)
	question_list = []
	ans_list = []
	for img in image_list:
		question_list.append(questions_dict[img_annotations[img.split(".")[0]][0][0]])
		ans_list.append(img_annotations[img.split(".")[0]][0][1].title())
		choices = [img_annotations[img.split(".")[0]][0][1].title()]
		choices.extend(create_single_options(img_annotations[img.split(".")[0]][0][0],img_annotations[img.split(".")[0]]))
		
		to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or "]
		new_choices = []
		for ch in choices:
			for word in to_be_removed:
				if word in ch:
					ch = ch.replace(word,"")
			new_choices.append(ch)
		choices = new_choices
		shuffle(choices)
		choices_list.append(";".join(choices))

		new_ans_list = []
		for ans in ans_list:
			for word in to_be_removed:
				if word in ans:
					ans = ans.replace(word,"")
			new_ans_list.append(ans)
		ans_list = new_ans_list
	print "Answers:",str(ans_list)
		
	if request.method=='POST' and request.form['submit']:
		for ch in dict(request.form).keys():
			if ch in choices_list:
				print "Selected Option:",ch
				return render_template("index.html",choices_list=choices_list,question_list=question_list,image_list=image_list,alert_message="Captcha question answered correctly. Try another one.",alert_type='info')
		else:
			return render_template("index.html",choices_list=choices_list,image_list=image_list,question_list=question_list,alert_message="Captcha question was not answered correctly. Try another one.",alert_type='danger')
	return render_template("index.html",choices_list=choices_list,image_list=image_list,question_list=question_list)

@main.route("/multiple",methods=['GET','POST'])
def multiple():
	form = MainForm()
	recaptcha = Recaptcha()

	answer_choices = []
	image_list = getRandomImages(4)


	selected_images = random.sample(image_list,2)
	img1_tuples = img_annotations[selected_images[0].split(".")[0]]
	img2_tuples = img_annotations[selected_images[1].split(".")[0]]

	img1_chosen = random.sample(img1_tuples,1)
	img2_chosen = random.sample(img2_tuples,1)

	print "Classes:",img1_chosen[0][0]+ " " + img2_chosen[0][0]
	cmd = "python app/main/code/RNN/enc_dec/train_test.py multiple "+img1_chosen[0][0]+ " " + img2_chosen[0][0]
	question = os.popen(cmd).read().split("\n")[2]
	print question
	name = make_composite(*image_list)

	## Forming the options

	# Getting all (class,obj) pairs for all 4 images
	all_tuples = []
	all_tuples.extend(img_annotations[image_list[0].split(".")[0]])
	all_tuples.extend(img_annotations[image_list[1].split(".")[0]])
	all_tuples.extend(img_annotations[image_list[2].split(".")[0]])
	all_tuples.extend(img_annotations[image_list[3].split(".")[0]])
	all_tuples = list(set(all_tuples))

	# Select the tuple from all_tuples if the class matches the classes of the 2 selected images
	all_obj = [t for t in all_tuples if t[0] == img1_chosen[0][0] or t[0] == img2_chosen[0][0]]
	
	# Pass this to the function
	answer_choices.extend(create_multiple_options(all_obj))

	# Append the correct answer to the answer_choices
	answer_choices.append(img1_chosen[0][1].title())
	answer_choices.append(img2_chosen[0][1].title())
	
	correct_answers = [img1_chosen[0][1].title(),img2_chosen[0][1].title()]

	shuffle(answer_choices)
	print "Correct Answers:",correct_answers

	if form.submit.data:
		flag = False
		for ch in answer_choices:
			if ch in dict(request.form).keys():
				# Correct answer
				flag = True
		if flag:
			return render_template("multiple.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form,success=True,alert_message="Captcha question answered correctly. Try another one.",alert_type='info')
		else:
			# Wrong answer
			return render_template("multiple.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form,wrong=True,alert_message="Captcha question was not answered correctly. Try another one.",alert_type='danger')
	
	return render_template("multiple.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form)
