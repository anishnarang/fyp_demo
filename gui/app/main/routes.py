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

count = 0
questions_dict = eval(open('app/main/test_questions.txt').read())

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
	# q = train_test.test('other')
	#print os.popen("pwd")
	img_annotations = eval(open('app/main/annotations.txt').read())
	global questions_dict
	# q = os.popen("python app/main/code/RNN/enc_dec/train_test.py multiple other clothing").read()
	# print q
	#choices_list = ["Option1;Option2;Option3;Option4" for i in range(9)]
	choices_list = []
	answer_choices=["Option1","Option2","Option3","Option4"]
	image_list = getRandomImages(9)
	question_list = []
	ans_list = []
	for img in image_list:
		# question_list.append(os.popen("python app/main/code/RNN/enc_dec/train_test.py single " + img_annotations[img.split(".")[0]][0][0]).read())
		question_list.append(questions_dict[img_annotations[img.split(".")[0]][0][0]])
		ans_list.append(img_annotations[img.split(".")[0]][0][1])
		choices_list.append(img_annotations[img.split(".")[0]][0][1])
		
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

	answer_choices=["Option1","Option2","Option3","Option4"]
	image_list = getRandomImages(4)
	question = "This is a longer Sample Question to see if it fits."
	name = make_composite(*image_list)

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
