import train_test

ques={}
c = 0
d=eval(open("annotations.txt").read())
for k in d.keys():
	c +=1
	print c
	for v in d[k]:
		if v[0] in ques.keys():
			ques[v[0]].append(train_test.test(v[0]))
		else:    
			ques[v[0]]=[]
			ques[v[0]].append(train_test.test(v[0]))
	if len(ques.keys()) == 8:
		break
res = {}
for k in ques.keys():
	res[k] = list(set(ques[k]))
open("all_results.txt","w").write(str(res))
