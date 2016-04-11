from code.RNN.enc_dec import train_test

ques={}
c = 0
d=eval(open("annotations.txt").read())
for k in d.keys():
	c +=1
	print c
	for v in d[k]:
        if v[0][0] in ques.keys():
        	print v[0][0]
			ques[v[0][0]].append(train_test.test(v[0][0]))
		else:                                                  
			ques[v[0][0]]=[]
			ques[v[0][0]].append(train_test.test(v[0][0]))
print len(ques.keys())
open("all_results.txt","w").write(str(ques))
