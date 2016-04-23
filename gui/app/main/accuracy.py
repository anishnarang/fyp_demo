import os
import random
import datetime
import sys
import time

def single(n):
	imgs = os.listdir("../static")
	imgs = [i.split(".")[0] for i in imgs if "jpg" in i]
	img_annotations = eval(open('annotations.txt').read())
	curdir = os.popen("pwd").read().strip()
	os.chdir("../..")
	c = 0
	for i in range(n):
		cmd = "python app/main/code/RNN/enc_dec/train_test.py single "+img_annotations[imgs[i]][0][0]
		question = os.popen(cmd).read()
		print question
		if 'What animals are shown in the picture ' in question and img_annotations[imgs[i]][0][0] == 'animals':
			c+=1
		elif img_annotations[imgs[i]][0][0] == 'vehicles' and 'Which type of vehicle(s) are present in the image ' in question:
			c+=1
		elif img_annotations[imgs[i]][0][0] == 'people' and 'Choose the option that best describes the people in the image ?' in question:
			c+=1
		elif img_annotations[imgs[i]][0][0] == 'clothing' and 'Identify the type of clothing depicted in the image ?' in question:
			c+=1
		elif img_annotations[imgs[i]][0][0] == 'other' and 'Which of the following is present in the image ?' in question:
			c+=1
		elif img_annotations[imgs[i]][0][0] == 'bodyparts' and 'Identify the bodypart present in the image ?' in question:
			c+=1
		elif img_annotations[imgs[i]][0][0] == 'scene' and 'Choose the option that best describes the scene ?' in question:
			c+=1
		elif img_annotations[imgs[i]][0][0] == 'instruments' and 'Select the instruments shown in the image ?' in question: 
			c+=1
	os.chdir(curdir)
	print 'Accuracy: '+str((float(c)/n)*100)

def multiple(n):
	imgs = os.listdir("../static")
	imgs = [i.split(".")[0] for i in imgs if "jpg" in i]
	img_annotations = eval(open('annotations.txt').read())
	curdir = os.popen("pwd").read().strip()
	os.chdir("../..")
	class_ques_lookup = eval(open("app/main/data/class_ques_lookup_pair.txt").read())
	c = 0.0
	for i in range(n+1):
		cmd = "python app/main/code/RNN/enc_dec/train_test.py multiple "+img_annotations[imgs[i]][0][0] + " " + img_annotations[imgs[i+1]][0][0]
		question = os.popen(cmd).read().split("\n")[2]
		print question

		if(class_ques_lookup[img_annotations[imgs[i]][0][0]][0] in question):
			c+=0.5
		if(class_ques_lookup[img_annotations[imgs[i+1]][0][0]][0] in question):
			c+=0.5
			
	print 'Accuracy: '+str((float(c)/n)*100)
	os.chdir(curdir)


n = int(sys.argv[2])
if(sys.argv[1] == "single"):
	single(n)
else:
	multiple(n)