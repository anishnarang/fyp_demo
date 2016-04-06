import random
import pickle

def gen_options(ans,others):
	s = set()
	for i in ans[:4]:
		if i != '':
			s.add(i)
	for i in others[:3]:
		if i != '':
			s.add(i)
	s = list(s)
	random.shuffle(s)
	for i in range(len(s)):
		print "(" + str(i+1) + ") " + s[i]
	print "Ans : "
	for i in ans[:4]:
		if i != '':
			print "(" ,(s.index(i)+1), ") " , i,


img_set = set()
d = pickle.load(open("../data/dataset.pickle","r"))

while(len(img_set)<5):
	img_set.add(d.keys()[random.randrange(len(d.keys()))])

for i in img_set:
	print str(i)+" : "+str(d[i])


count_dict = dict()
obj_dict = dict()
class_set = set()
other_objs_l = d[d.keys()[random.randrange(len(d.keys()))]]
other_objs = set()
for i in other_objs_l:
	other_objs.add(i[0][1])
for i in img_set:
	for j in d[i]:
		class_set.add(j[0][1])
		if(j[0][0] in count_dict.keys()):
			count_dict[j[0][0]] +=1
		else:
			count_dict[j[0][0]] = 1
		if(j[0][0] in obj_dict.keys()):
			l = obj_dict[j[0][0]]
			l.append(j[0][1])
			obj_dict[j[0][0]] =  l
		else:
			l = []
			l.append(j[0][1])
			obj_dict[j[0][0]] = l

del count_dict["other"]
del count_dict["scene"]
class_set = list(class_set)
obj_class = count_dict.keys()[random.randrange(len(count_dict.keys()))]
obj_count = count_dict[obj_class]
other_objs = list(other_objs)

c = 0
for obj in obj_dict[obj_class]:
	if obj != '':
		c += 1
if c != 0:
	print "How many " + str(obj_class) + " are there in the images?"
	print "Ans: " + str(obj_count)
	print [obj for obj in obj_dict[obj_class] if obj != '']

print "Which of the following are present in the images?"
print "Options: "
gen_options(class_set,other_objs)

# print "Ans: " + str(class_set)

if obj_count > 1:
	print "\nWhich of the following " + str(obj_class) + " are there in the images?"
	print "Options: "
	gen_options(class_set,other_objs)
	# print "Ans: " + str(obj_dict[obj_class])

	print "\nIdentify all the " + str(obj_class) + " in the images."
	print "Options: "
	gen_options(class_set,other_objs)
	# print "Ans: " + str(obj_dict[obj_class])