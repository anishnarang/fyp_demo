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


correct_answers = []
final_images = eval(open("finalimages/final_images.txt").read())


@main.route("/multiple",methods=['POST'])	
def multiple_answers():
	form = MainForm()
	recaptcha = Recaptcha()
	global correct_answers,final_images

	if form.submit.data:
		count = 0
		answers= []

		for ch in dict(request.form).keys():
			if ch != 'submit':
				answers.append(ch)
				# count+=1 #Correct answer
		
		if sorted(answers) == sorted(correct_answers) :
			# Correct answer 
			key = random.sample(final_images.keys(), 1)
			name = key[0]
			question = final_images[name]["question"]
			answer_choices = final_images[name]["answer_choices"]
			correct_answers = final_images[name]["correct_answers"]
			print "Correct Answers:",correct_answers
			return render_template("multiple.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form,success=True,alert_message="Captcha question answered correctly. Try another one.",alert_type='info')
		else:
			# Wrong answer
			form = MainForm()
			recaptcha = Recaptcha()

			key = random.sample(final_images.keys(), 1)

			name = key[0]
			question = final_images[name]["question"]
			answer_choices = final_images[name]["answer_choices"]
			correct_answers = final_images[name]["correct_answers"]

			print "Correct Answers:",correct_answers
			return render_template("multiple.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form,wrong=True,alert_message="Captcha question was not answered correctly. Try another one.",alert_type='danger')
	
@main.route("/multiple",methods=['GET'])
def multiple_final():
	global correct_answers,final_images
	form = MainForm()
	recaptcha = Recaptcha()

	key = random.sample(final_images.keys(), 1)

	name = key[0]
	question = final_images[name]["question"]
	answer_choices = final_images[name]["answer_choices"]
	correct_answers = final_images[name]["correct_answers"]


	return render_template("multiple.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form)
