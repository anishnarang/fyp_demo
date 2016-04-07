import train_test

images = eval(open("../../../../static/images.txt").read())

ques={}
c = 0
d=eval(open("annotations.txt").read())
for i in images:
	c +=1
	print c
	for v in d[i.split(".")[0]]:
		if v[0] in ques.keys():
			q = train_test.test(v[0])
			ques[v[0]].append(q)
		else:                                                  
			ques[v[0]]=[]
			q = train_test.test(v[0])
			ques[v[0]].append(q)
print len(ques.keys())
open("all_results_new.txt","w").write(str(ques))
