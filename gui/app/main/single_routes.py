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


final_images_single = eval(open("finalimagessingle/final_images_single.txt").read())
single_ans_list = []

@main.route("/single",methods=['GET'])
def single():
    global questions_dict,img_annotations
    global choices_list,image_list,question_list,single_ans_list 
    
    image_list = random.sample(final_images_single.keys(), 9)

    question_list = []
    choices_list = []
    single_ans_list  = []

    for img in image_list:
        question_list.append(final_images_single[img]["Question"])
        choices_list.append(";".join(final_images_single[img]["Choices"]))
        single_ans_list .append(final_images_single[img]["Answer"])
    
    print "Answers:",str(single_ans_list )
    
    return render_template("single.html",choices_list=choices_list,image_list=image_list,question_list=question_list)

@main.route("/single",methods=['POST'])
def single_ans():
    global choices_list,image_list,question_list,single_ans_list ,image_list
    # print single_ans_list
    if request.method=='POST' and request.form['submit']:
        for ch in dict(request.form).keys():
            if ch in single_ans_list:
                print "Selected Option:",ch
                image_list = random.sample(final_images_single.keys(), 9)

                question_list = []
                choices_list = []
                single_ans_list = []

                for img in image_list:
                    question_list.append(final_images_single[img]["Question"])
                    choices_list.append(";".join(final_images_single[img]["Choices"]))
                    single_ans_list.append(final_images_single[img]["Answer"])
                print "=====================================================================\nAnswers:",str(single_ans_list)
                return render_template("single.html",choices_list=choices_list,question_list=question_list,image_list=image_list,alert_message="Captcha question answered correctly. Try another one.",alert_type='info')
        else:
            image_list = random.sample(final_images_single.keys(), 9)

            question_list = []
            choices_list = []
            single_ans_list = []

            for img in image_list:
                question_list.append(final_images_single[img]["Question"])
                choices_list.append(";".join(final_images_single[img]["Choices"]))
                single_ans_list.append(final_images_single[img]["Answer"])
            print "=====================================================================\nAnswers:",str(single_ans_list)
            return render_template("single.html",choices_list=choices_list,image_list=image_list,question_list=question_list,alert_message="Captcha question was not answered correctly. Try another one.",alert_type='danger')

    return render_template("single.html",choices_list=choices_list,image_list=image_list,question_list=question_list)

