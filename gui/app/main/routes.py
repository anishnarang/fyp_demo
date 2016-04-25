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
live_class_obj = eval(open('app/main/live_class_obj.txt').read())
live_img_annotations = eval(open('app/main/live_annotations.txt').read())
LIVE_TUPLES = eval(open('app/main/code/flickr30k/live_all_tuples.txt').read())

def create_single_options(cls,obj_list):
    #obj_list is a list of 2 tuple annotations
    obj = [o[1].title() for o in obj_list]
    all_obj = class_obj[cls]
    shuffle(all_obj)
    ops = list(set(all_obj) - set(obj_list))
    shuffle(ops)
    res = ops[:2]

    for k in class_obj.keys():
        if k != cls:
            res.extend(random.sample(class_obj[k],1))
            break

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
    
    
def live_create_multiple_options(all_obj):
    # ALL_TUPLES is a list of all possible tuples in the dataset
    # ALL_OBJ is a list of all possible objects in the dataset
    ALL_OBJ = list(zip(LIVE_TUPLES))

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

def getLiveImages(num):
    images = []
    l = eval(app.open_resource('static/live_images.txt').read())
    for i in range(num):
        r = random.randint(0,len(l)-1)
        images.append(l[r])
    return images
    
ans_list = []
choices_list = []
question_list = []
ans_list = []

@main.route("/single_backup",methods=['POST'])
def single_answers():
    global choices_list,image_list,question_list,ans_list ,image_list
    # print ans_list
    if request.method=='POST' and request.form['submit']:
        for ch in dict(request.form).keys():
            if ch in ans_list:
                print "Selected Option:",ch
                ans_list = []
                choices_list = []
                image_list = getRandomImages(9)
                print "Image List: ",image_list
                question_list = []
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
                print "=====================================================================\nAnswers:",str(ans_list)
                return render_template("single_backup.html",choices_list=choices_list,question_list=question_list,image_list=image_list,alert_message="Captcha question answered correctly. Try another one.",alert_type='info')
        else:
            print "Selected Option:",ch
            ans_list = []
            choices_list = []
            image_list = getRandomImages(9)
            print "Image List: ",image_list
            question_list = []
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
            return render_template("single_backup.html",choices_list=choices_list,image_list=image_list,question_list=question_list,alert_message="Captcha question was not answered correctly. Try another one.",alert_type='danger')

    return render_template("single_backup.html",choices_list=choices_list,image_list=image_list,question_list=question_list)


@main.route("/single_backup",methods=['GET'])
def index():
    global questions_dict,img_annotations
    global choices_list,image_list,question_list,ans_list 
    ans_list = []
    choices_list = []
    image_list = getRandomImages(9)
    print "Image List: ",image_list
    question_list = []
    for img in image_list:
        question_list.append(questions_dict[img_annotations[img.split(".")[0]][0][0]])
        ans_list.append(img_annotations[img.split(".")[0]][0][1].title())
        choices = [img_annotations[img.split(".")[0]][0][1].title()]
        choices.extend(create_single_options(img_annotations[img.split(".")[0]][0][0],img_annotations[img.split(".")[0]]))
        
        to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
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
    
    return render_template("single_backup.html",choices_list=choices_list,image_list=image_list,question_list=question_list)


correct_answers = []
    
@main.route("/multiple_backup",methods=['POST'])    
def multiple_backup_answers():
    form = MainForm()
    recaptcha = Recaptcha()
    global correct_answers

    if form.submit.data:
        count = 0
        answers= []

        for ch in dict(request.form).keys():
            if ch != 'submit':
                answers.append(ch)
                # count+=1 #Correct answer
        
        if sorted(answers) == sorted(correct_answers) :
            # Correct answer 
            answer_choices = []
            image_list = getRandomImages(4)


            selected_images = random.sample(image_list,2)
            img1_tuples = img_annotations[selected_images[0].split(".")[0]]
            img2_tuples = img_annotations[selected_images[1].split(".")[0]]

            img1_chosen = random.sample(img1_tuples,1)
            img2_chosen = random.sample(img2_tuples,1)

            while img1_chosen[0][0] ==  img2_chosen[0][0]:
                img2_chosen = random.sample(img2_tuples,1)

            print "Classes:",img1_chosen[0][0]+ " " + img2_chosen[0][0]
            cmd = "python app/main/code/RNN/enc_dec/train_test.py multiple "+img1_chosen[0][0]+ " " + img2_chosen[0][0]
            question = os.popen(cmd).read().split("\n")[2]
            print "Question: ",question
            name = make_composite(*image_list)
            print "Image: ",name

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

            # 2 options of different classes
            other_classes = [k for k in class_obj.keys() if k != img1_chosen[0][0] or k!=img2_chosen[0][0]]
            random_classes = random.sample(other_classes,2)
            answer_choices.extend(random.sample(class_obj[random_classes[0]],1))
            answer_choices.extend(random.sample(class_obj[random_classes[1]],1))
                

            # Append the correct answer to the answer_choices
            answer_choices.append(img1_chosen[0][1].title())
            answer_choices.append(img2_chosen[0][1].title())
            
            correct_answers = [img1_chosen[0][1].title(),img2_chosen[0][1].title()]

            shuffle(answer_choices)

            # Sanitize the choices
            to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
            new_choices = []
            for ch in answer_choices:
                for word in to_be_removed:
                    if word in ch:
                        ch = ch.replace(word,"")
                new_choices.append(ch)
            answer_choices = new_choices

            # Sanitize answers
            to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
            new_choices = []
            for ch in correct_answers:
                for word in to_be_removed:
                    if word in ch:
                        ch = ch.replace(word,"")
                new_choices.append(ch)
            correct_answers = new_choices
            print "Correct Answers:",correct_answers
            return render_template("multiple.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form,success=True,alert_message="Captcha question answered correctly. Try another one.",alert_type='info')
        else:
            # Wrong answer
            form = MainForm()
            recaptcha = Recaptcha()

            answer_choices = []
            image_list = getRandomImages(4)


            selected_images = random.sample(image_list,2)
            img1_tuples = img_annotations[selected_images[0].split(".")[0]]
            img2_tuples = img_annotations[selected_images[1].split(".")[0]]

            img1_chosen = random.sample(img1_tuples,1)
            img2_chosen = random.sample(img2_tuples,1)

            while img1_chosen[0][0] ==  img2_chosen[0][0]:
                img2_chosen = random.sample(img2_tuples,1)

            print "Classes:",img1_chosen[0][0]+ " " + img2_chosen[0][0]
            cmd = "python app/main/code/RNN/enc_dec/train_test.py multiple "+img1_chosen[0][0]+ " " + img2_chosen[0][0]
            question = os.popen(cmd).read().split("\n")[2]
            print "Question: ",question
            name = make_composite(*image_list)
            print "Image: ",name

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

            # 2 options of different classes
            other_classes = [k for k in class_obj.keys() if k != img1_chosen[0][0] or k!=img2_chosen[0][0]]
            random_classes = random.sample(other_classes,2)
            answer_choices.extend(random.sample(class_obj[random_classes[0]],1))
            answer_choices.extend(random.sample(class_obj[random_classes[1]],1))
            
            correct_answers = [img1_chosen[0][1].title(),img2_chosen[0][1].title()]

            shuffle(answer_choices)
            to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
            new_choices = []
            for ch in answer_choices:
                for word in to_be_removed:
                    if word in ch:
                        ch = ch.replace(word,"")
                new_choices.append(ch)
            answer_choices = new_choices

            # Sanitize answers
            to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
            new_choices = []
            for ch in correct_answers:
                for word in to_be_removed:
                    if word in ch:
                        ch = ch.replace(word,"")
                new_choices.append(ch)
            correct_answers = new_choices

            print "Correct Answers:",correct_answers
            return render_template("multiple_backup.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form,wrong=True,alert_message="Captcha question was not answered correctly. Try another one.",alert_type='danger')
    
@main.route("/multiple_backup",methods=['GET'])
def multiple():
    global correct_answers
    form = MainForm()
    recaptcha = Recaptcha()

    answer_choices = []
    image_list = getRandomImages(4)


    selected_images = random.sample(image_list,2)
    img1_tuples = img_annotations[selected_images[0].split(".")[0]]
    img2_tuples = img_annotations[selected_images[1].split(".")[0]]

    img1_chosen = random.sample(img1_tuples,1)
    img2_chosen = random.sample(img2_tuples,1)

    while img1_chosen[0][0] ==  img2_chosen[0][0]:
        img2_chosen = random.sample(img2_tuples,1)

    print "Classes:",img1_chosen[0][0]+ " " + img2_chosen[0][0]
    cmd = "python app/main/code/RNN/enc_dec/train_test.py multiple "+img1_chosen[0][0]+ " " + img2_chosen[0][0]
    question = os.popen(cmd).read().split("\n")[2]
    print "Question: ",question
    name = make_composite(*image_list)
    print "Image: ",name

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

    # 2 options of different classes
    other_classes = [k for k in class_obj.keys() if k != img1_chosen[0][0] or k!=img2_chosen[0][0]]
    random_classes = random.sample(other_classes,2)
    answer_choices.extend(random.sample(class_obj[random_classes[0]],1))
    answer_choices.extend(random.sample(class_obj[random_classes[1]],1))
    
    correct_answers = [img1_chosen[0][1].title(),img2_chosen[0][1].title()]

    shuffle(answer_choices)

    # Sanitize the choices
    to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
    new_choices = []
    for ch in answer_choices:
        for word in to_be_removed:
            if word in ch:
                ch = ch.replace(word,"")
        new_choices.append(ch)
    answer_choices = new_choices

    # Sanitize answers
    to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
    new_choices = []
    for ch in correct_answers:
        for word in to_be_removed:
            if word in ch:
                ch = ch.replace(word,"")
        new_choices.append(ch)
    correct_answers = new_choices

    print "Correct Answers:",correct_answers

    
    return render_template("multiple_backup.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form)




@main.route("/live_single", methods = ['POST'])
def live_single_answers():
    global choices_list,image_list,question_list,ans_list ,image_list
    # print ans_list
    if request.method=='POST' and request.form['submit']:
        for ch in dict(request.form).keys():
            if ch in ans_list:
                print "Selected Option:",ch
                ans_list = []
                choices_list = []
                image_list = getLiveImages(9)
                question_list = []
                for img in image_list:
                    question_list.append(questions_dict[live_img_annotations[img.split(".")[0]][0][0]])
                    ans_list.append(live_img_annotations[img.split(".")[0]][0][1].title())
                    choices = [live_img_annotations[img.split(".")[0]][0][1].title()]
                    choices.extend(create_single_options(live_img_annotations[img.split(".")[0]][0][0],live_img_annotations[img.split(".")[0]]))
                    
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
                print "=====================================================================\nAnswers:",str(ans_list)
                return render_template("index_live.html",choices_list=choices_list,question_list=question_list,image_list=image_list,alert_message="Captcha question answered correctly. Try another one.",alert_type='info')
        else:
            print "Selected Option:",ch
            ans_list = []
            choices_list = []
            image_list = getLiveImages(9)
            question_list = []
            for img in image_list:
                question_list.append(questions_dict[live_img_annotations[img.split(".")[0]][0][0]])
                ans_list.append(live_img_annotations[img.split(".")[0]][0][1].title())
                choices = [live_img_annotations[img.split(".")[0]][0][1].title()]
                choices.extend(create_single_options(live_img_annotations[img.split(".")[0]][0][0],live_img_annotations[img.split(".")[0]]))
                
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
            return render_template("index_live.html",choices_list=choices_list,image_list=image_list,question_list=question_list,alert_message="Captcha question was not answered correctly. Try another one.",alert_type='danger')

    return render_template("index_live.html",choices_list=choices_list,image_list=image_list,question_list=question_list)


@main.route("/live_single",methods=['GET'])
def live_single():
    global questions_dict,live_img_annotations
    global choices_list,image_list,question_list,ans_list 
    ans_list = []
    choices_list = []
    image_list = getLiveImages(9)
    question_list = []
    for img in image_list:
        question_list.append(questions_dict[live_img_annotations[img.split(".")[0]][0][0]])
        ans_list.append(live_img_annotations[img.split(".")[0]][0][1].title())
        choices = [live_img_annotations[img.split(".")[0]][0][1].title()]
        choices.extend(create_single_options(live_img_annotations[img.split(".")[0]][0][0],live_img_annotations[img.split(".")[0]]))
        
        to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
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
    
    return render_template("index_live.html",choices_list=choices_list,image_list=image_list,question_list=question_list)



@main.route("/live_multiple",methods=['POST'])    
def live_multiple_answers():
    form = MainForm()
    recaptcha = Recaptcha()
    global correct_answers

    if form.submit.data:
        count = 0
        answers= []

        for ch in dict(request.form).keys():
            if ch != 'submit':
                answers.append(ch)
                # count+=1 #Correct answer
        
        if sorted(answers) == sorted(correct_answers) :
            # Correct answer 
            answer_choices = []
            image_list = getLiveImages(4)


            selected_images = random.sample(image_list,2)
            img1_tuples = live_img_annotations[selected_images[0].split(".")[0]]
            img2_tuples = live_img_annotations[selected_images[1].split(".")[0]]

            img1_chosen = random.sample(img1_tuples,1)
            img2_chosen = random.sample(img2_tuples,1)

            while img1_chosen[0][0] ==  img2_chosen[0][0]:
                img2_chosen = random.sample(img2_tuples,1)

            print "Classes:",img1_chosen[0][0]+ " " + img2_chosen[0][0]
            cmd = "python app/main/code/RNN/enc_dec/train_test.py multiple "+img1_chosen[0][0]+ " " + img2_chosen[0][0]
            question = os.popen(cmd).read().split("\n")[2]
            print "Question: ",question
            name = make_composite(*image_list)
            print "Image: ",name

            ## Forming the options

            # Getting all (class,obj) pairs for all 4 images
            all_tuples = []
            all_tuples.extend(live_img_annotations[image_list[0].split(".")[0]])
            all_tuples.extend(live_img_annotations[image_list[1].split(".")[0]])
            all_tuples.extend(live_img_annotations[image_list[2].split(".")[0]])
            all_tuples.extend(live_img_annotations[image_list[3].split(".")[0]])
            all_tuples = list(set(all_tuples))

            # Select the tuple from all_tuples if the class matches the classes of the 2 selected images
            all_obj = [t for t in all_tuples if t[0] == img1_chosen[0][0] or t[0] == img2_chosen[0][0]]
            
            # Pass this to the function
            answer_choices.extend(create_multiple_options(all_obj))

            # 2 options of different classes
            other_classes = [k for k in class_obj.keys() if k != img1_chosen[0][0] or k!=img2_chosen[0][0]]
            random_classes = random.sample(other_classes,2)
            answer_choices.extend(random.sample(class_obj[random_classes[0]],1))
            answer_choices.extend(random.sample(class_obj[random_classes[1]],1))
                

            # Append the correct answer to the answer_choices
            answer_choices.append(img1_chosen[0][1].title())
            answer_choices.append(img2_chosen[0][1].title())
            
            correct_answers = [img1_chosen[0][1].title(),img2_chosen[0][1].title()]

            shuffle(answer_choices)

            # Sanitize the choices
            to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
            new_choices = []
            for ch in answer_choices:
                for word in to_be_removed:
                    if word in ch:
                        ch = ch.replace(word,"")
                new_choices.append(ch)
            answer_choices = new_choices

            # Sanitize answers
            to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
            new_choices = []
            for ch in correct_answers:
                for word in to_be_removed:
                    if word in ch:
                        ch = ch.replace(word,"")
                new_choices.append(ch)
            correct_answers = new_choices
            print "Correct Answers:",correct_answers
            return render_template("multiple_live.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form,success=True,alert_message="Captcha question answered correctly. Try another one.",alert_type='info')
        else:
            # Wrong answer
            form = MainForm()
            recaptcha = Recaptcha()

            answer_choices = []
            image_list = getLiveImages(4)


            selected_images = random.sample(image_list,2)
            img1_tuples = live_img_annotations[selected_images[0].split(".")[0]]
            img2_tuples = live_img_annotations[selected_images[1].split(".")[0]]

            img1_chosen = random.sample(img1_tuples,1)
            img2_chosen = random.sample(img2_tuples,1)

            while img1_chosen[0][0] ==  img2_chosen[0][0]:
                img2_chosen = random.sample(img2_tuples,1)

            print "Classes:",img1_chosen[0][0]+ " " + img2_chosen[0][0]
            cmd = "python app/main/code/RNN/enc_dec/train_test.py multiple "+img1_chosen[0][0]+ " " + img2_chosen[0][0]
            question = os.popen(cmd).read().split("\n")[2]
            print "Question: ",question
            name = make_composite(*image_list)
            print "Image: ",name

            ## Forming the options

            # Getting all (class,obj) pairs for all 4 images
            all_tuples = []
            all_tuples.extend(live_img_annotations[image_list[0].split(".")[0]])
            all_tuples.extend(live_img_annotations[image_list[1].split(".")[0]])
            all_tuples.extend(live_img_annotations[image_list[2].split(".")[0]])
            all_tuples.extend(live_img_annotations[image_list[3].split(".")[0]])
            all_tuples = list(set(all_tuples))

            # Select the tuple from all_tuples if the class matches the classes of the 2 selected images
            all_obj = [t for t in all_tuples if t[0] == img1_chosen[0][0] or t[0] == img2_chosen[0][0]]
            
            # Pass this to the function
            answer_choices.extend(create_multiple_options(all_obj))

            # Append the correct answer to the answer_choices
            answer_choices.append(img1_chosen[0][1].title())
            answer_choices.append(img2_chosen[0][1].title())

            # 2 options of different classes
            other_classes = [k for k in class_obj.keys() if k != img1_chosen[0][0] or k!=img2_chosen[0][0]]
            random_classes = random.sample(other_classes,2)
            answer_choices.extend(random.sample(class_obj[random_classes[0]],1))
            answer_choices.extend(random.sample(class_obj[random_classes[1]],1))
            
            correct_answers = [img1_chosen[0][1].title(),img2_chosen[0][1].title()]

            shuffle(answer_choices)
            to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
            new_choices = []
            for ch in answer_choices:
                for word in to_be_removed:
                    if word in ch:
                        ch = ch.replace(word,"")
                new_choices.append(ch)
            answer_choices = new_choices

            # Sanitize answers
            to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
            new_choices = []
            for ch in correct_answers:
                for word in to_be_removed:
                    if word in ch:
                        ch = ch.replace(word,"")
                new_choices.append(ch)
            correct_answers = new_choices

            print "Correct Answers:",correct_answers
            return render_template("multiple_live.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form,wrong=True,alert_message="Captcha question was not answered correctly. Try another one.",alert_type='danger')
    
@main.route("/live_multiple",methods=['GET'])
def live_multiple():
    global correct_answers
    form = MainForm()
    recaptcha = Recaptcha()

    answer_choices = []
    image_list = getLiveImages(4)


    selected_images = random.sample(image_list,2)
    img1_tuples = live_img_annotations[selected_images[0].split(".")[0]]
    img2_tuples = live_img_annotations[selected_images[1].split(".")[0]]

    img1_chosen = random.sample(img1_tuples,1)
    img2_chosen = random.sample(img2_tuples,1)

    while img1_chosen[0][0] ==  img2_chosen[0][0]:
        img2_chosen = random.sample(img2_tuples,1)

    print "Classes:",img1_chosen[0][0]+ " " + img2_chosen[0][0]
    cmd = "python app/main/code/RNN/enc_dec/train_test.py multiple "+img1_chosen[0][0]+ " " + img2_chosen[0][0]
    question = os.popen(cmd).read().split("\n")[2]
    print "Question: ",question
    name = make_composite(*image_list)
    print "Image: ",name

    ## Forming the options

    # Getting all (class,obj) pairs for all 4 images
    all_tuples = []
    all_tuples.extend(live_img_annotations[image_list[0].split(".")[0]])
    all_tuples.extend(live_img_annotations[image_list[1].split(".")[0]])
    all_tuples.extend(live_img_annotations[image_list[2].split(".")[0]])
    all_tuples.extend(live_img_annotations[image_list[3].split(".")[0]])
    all_tuples = list(set(all_tuples))

    # Select the tuple from all_tuples if the class matches the classes of the 2 selected images
    all_obj = [t for t in all_tuples if t[0] == img1_chosen[0][0] or t[0] == img2_chosen[0][0]]
    
    # Pass this to the function
    answer_choices.extend(create_multiple_options(all_obj))

    # Append the correct answer to the answer_choices
    answer_choices.append(img1_chosen[0][1].title())
    answer_choices.append(img2_chosen[0][1].title())

    # 2 options of different classes
    other_classes = [k for k in class_obj.keys() if k != img1_chosen[0][0] or k!=img2_chosen[0][0]]
    random_classes = random.sample(other_classes,2)
    answer_choices.extend(random.sample(class_obj[random_classes[0]],1))
    answer_choices.extend(random.sample(class_obj[random_classes[1]],1))
    
    correct_answers = [img1_chosen[0][1].title(),img2_chosen[0][1].title()]

    shuffle(answer_choices)

    # Sanitize the choices
    to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
    new_choices = []
    for ch in answer_choices:
        for word in to_be_removed:
            if word in ch:
                ch = ch.replace(word,"")
        new_choices.append(ch)
    answer_choices = new_choices

    # Sanitize answers
    to_be_removed = ["","His ","Her ","Hers ","Her's ","Its ","It's ","Other ","Another ","Their ","Or ","Your ","Yours ","These "]
    new_choices = []
    for ch in correct_answers:
        for word in to_be_removed:
            if word in ch:
                ch = ch.replace(word,"")
        new_choices.append(ch)
    correct_answers = new_choices

    print "Correct Answers:",correct_answers

    
    return render_template("multiple_live.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form)


correct_answers = []
final_images = eval(open("finalimages/final_images.txt").read())


@main.route("/multiple",methods=['POST'])   
def multiple_fixed_answers():
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
def multiple_fixed():
    global correct_answers,final_images
    form = MainForm()
    recaptcha = Recaptcha()

    key = random.sample(final_images.keys(), 1)

    name = key[0]
    question = final_images[name]["question"]
    answer_choices = final_images[name]["answer_choices"]
    correct_answers = final_images[name]["correct_answers"]

    print "Correct Answers:",correct_answers
    return render_template("multiple.html",question=question,composite=url_for('static',filename=name),answer_choices=answer_choices,recaptcha=recaptcha,form=form)


@main.route("/single",methods=['POST'])
def single_ans():
    global choices_list,image_list,question_list,ans_list ,image_list
    # print ans_list
    if request.method=='POST' and request.form['submit']:
        for ch in dict(request.form).keys():
            if ch in ans_list:
                print "Selected Option:",ch
                image_list = random.sample(final_images_single.keys(), 9)

                question_list = []
                choices_list = []
                ans_list = []

                for img in image_list:
                    question_list.append(final_images_single[img]["Question"])
                    choices_list.append(";".join(final_images_single[img]["Choices"]))
                    ans_list.append(final_images_single[img]["Answer"])
                print "=====================================================================\nAnswers:",str(ans_list)
                return render_template("single.html",choices_list=choices_list,question_list=question_list,image_list=image_list,alert_message="Captcha question answered correctly. Try another one.",alert_type='info')
        else:
            image_list = random.sample(final_images_single.keys(), 9)

            question_list = []
            choices_list = []
            ans_list = []

            for img in image_list:
                question_list.append(final_images_single[img]["Question"])
                choices_list.append(";".join(final_images_single[img]["Choices"]))
                ans_list.append(final_images_single[img]["Answer"])
            print "=====================================================================\nAnswers:",str(ans_list)
            return render_template("single.html",choices_list=choices_list,image_list=image_list,question_list=question_list,alert_message="Captcha question was not answered correctly. Try another one.",alert_type='danger')

    return render_template("single.html",choices_list=choices_list,image_list=image_list,question_list=question_list)

final_images_single = eval(open("finalimagessingle/final_images_single.txt").read())

@main.route("/single",methods=['GET'])
def single():
    global questions_dict,img_annotations
    global choices_list,image_list,question_list,ans_list 
    
    image_list = random.sample(final_images_single.keys(), 9)

    question_list = []
    choices_list = []
    ans_list = []

    for img in image_list:
        question_list.append(final_images_single[img]["Question"])
        choices_list.append(";".join(final_images_single[img]["Choices"]))
        ans_list.append(final_images_single[img]["Answer"])
    
    print "Answers:",str(ans_list)
    
    return render_template("single.html",choices_list=choices_list,image_list=image_list,question_list=question_list)