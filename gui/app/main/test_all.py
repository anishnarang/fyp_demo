from code.RNN.enc_dec import train_test

ques={}
d=eval(open("app/main/annotations.txt").read())
for k in d.keys():
	for v in d[k]:
        	if v[0][0] in ques.keys():
			ques[v[0][0]].append(train_test.test(v[0][0]))
		else:                                                  
			ques[v[0][0]]=[]
			ques[v[0][0]].append(train_test.test(v[0][0]))
print len(ques.keys())
open("all_results.txt","w").write(str(ques))
