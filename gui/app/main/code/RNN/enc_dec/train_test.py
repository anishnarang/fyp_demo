import encoder_decoder
import pickle
import sys
import time
from enc_dec_gru_sutskever_vinyals import EncoderDecoderRnn as ecr
from itertools import permutations,combinations
import numpy as np

def train(model_file):
	enc_dec = encoder_decoder(len(first_word_to_ix.keys()), len(ix_to_class_obj.keys()), 100, len(vocab_to_ix.keys()), 30, 100)
	enc_dec.train(inputs, targets, 2, vocab_to_ix, first_word_to_ix, model_q)
	enc_dec.save('../../../data/' + model_file)

def test(class_test,model_file='single.p'):
	inputs = pickle.load(open('../../../data/enc_dec_inputs.pickle'))
	targets = pickle.load(open('../../../data/enc_dec_targets.pickle'))
	ix_to_first_word = pickle.load(open('../../../data/ix_to_first_word.pickle'))
	first_word_to_ix = pickle.load(open('../../../data/first_word_to_ix.pickle'))
	vocab_to_ix = pickle.load(open('../../../data/vocab_to_ix.pickle'))
	ix_to_vocab = pickle.load(open('../../../data/ix_to_vocab.pickle'))
	ix_to_class_obj = pickle.load(open('../../../data/ix_to_class_obj.pickle'))
	class_obj_to_ix = pickle.load(open('../../../data/class_obj_to_ix.pickle'))
	model_q = pickle.load(open('../../../data/questions.pickle'))
	model_cls = pickle.load(open('../../../data/classes_obj.pickle'))
	#enc_dec = pickle.load(open('../../../data/demo/' + model_file))
	enc_dec = pickle.load(open('../../../code/RNN/enc_dec/'+model_file))
	classes = open('../../../code/RNN/create_dataset/classes_obj.txt').read().split(';')
	# del classes[classes.index('other')]
	# del classes[classes.index('people')]
	obj = eval(open("../../../code/RNN/create_dataset/objects.txt").read())
	# for i in range(len(classes)):
	#     print 'Class : ', classes[i] #eval(open('ques.txt').read()).values()[500]
	#     print 'Object : ', obj[i]
	ques = enc_dec.predict_question([class_obj_to_ix[class_test]], ix_to_first_word, ix_to_vocab, model_q)
	#print "Class:",class_test
	# if classes[i] == 'clothing' and ques == 'What is the person in the image wearing ?':
	#     c += 1
	# elif classes[i] in ques.split(' '):
	#     c += 1
	# elif classes[i] == "vehicles" and "vehicle(s)" in ques.split(' '):
	#      c+=1
	# elif classes[i] == "instruments" and "instrument(s)" in ques.split(' '):
	#     c+=1
	# elif classes[i] == 'other' and ques == 'Which of the following is present in the image ?':
	#     c += 1
	# print  c
	# print 'Accuracy : ', (c/float(len(classes))) * 100
	return ques


def train_gru(inputs,targets):
	inputs = pickle.load(open('../../../data/enc_dec_inputs_pair.pickle'))
	targets = pickle.load(open('../../../data/enc_dec_targets_pair.pickle'))
	ix_to_first_word = pickle.load(open('../../../data/ix_to_first_word_pair.pickle'))
	first_word_to_ix = pickle.load(open('../../../data/first_word_to_ix_pair.pickle'))
	vocab_to_ix = pickle.load(open('../../../data/vocab_to_ix_pair.pickle'))
	ix_to_vocab = pickle.load(open('../../../data/ix_to_vocab_pair.pickle'))
	ix_to_class_obj = pickle.load(open('../../../data/ix_to_class_obj_pair.pickle'))
	class_obj_to_ix = pickle.load(open('../../../data/class_obj_to_ix_pair.pickle'))
	model_q = pickle.load(open('../../../data/questions_pair.pickle'))
	model_cls = pickle.load(open('../../../data/classes_obj_pair.pickle'))
	enc_dec = ecr([len(ix_to_class_obj.keys()),100,len(ix_to_first_word.keys())], [len(ix_to_vocab.keys()),100,len(ix_to_vocab.keys())], output_layer=None)
	
	#ei = [np.zeros((len(ix_to_first_word.keys()),1)) for i in inputs]
	ei = []
	#pdb.set_trace()
	for i in inputs:
		temp = []
		for j in i:
			inp = np.zeros((len(ix_to_class_obj.keys()),))
			inp[j] = 1
			temp.append(inp)
		ei.append(np.array(temp))
	#pdb.set_trace()
	eo = []
	for t in targets:
		out = np.zeros((len(ix_to_first_word.keys()),))
		out[first_word_to_ix[t.split(' ')[0]]] = 1
		eo.append(np.array([out]))
	#pdb.set_trace()
#    di = [np.array([model_q[k] for k in i.split(' ')[:-1]]) for i in targets]
#    do = [np.array([model_q[k] for k in i.split(' ')[1:]]) for i in targets]
	di = []
	for t in targets:
		temp = []
		for ti in t.split(' ')[:-1]:
			out = np.zeros((len(ix_to_vocab.keys()),))
			out[vocab_to_ix[ti]] = 1
			temp.append(out)
		di.append(np.array(temp))
	do = []
	for t in targets:
		temp = []
		for ti in t.split(' ')[1:]:
			out = np.zeros((len(ix_to_vocab.keys()),))
			out[vocab_to_ix[ti]] = 1
			temp.append(out)
		do.append(np.array(temp))
	
	#do = [[vocab_to_ix[k] for k in i.split(' ')[1:]] for i in targets]
	enc_dec.train(ei,eo,di,do,max_iter=10)
	enc_dec.save('trained_multiple_10ep_30k.p')
	
	enc_dec = pickle.load(open('../../../code/RNN/enc_dec/trained_multiple_10ep_30k.p'))
	classes = open('../../../code/RNN/create_dataset/classes_obj_pair.txt').read().split(';')
	# del classes[classes.index('other')]
	# del classes[classes.index('people')]
	obj = eval(open("../../../code/RNN/create_dataset/objects.txt").read())
	c = 0
	#pdb.set_trace()
	class_ques = eval(open("../../../data/class_ques_lookup.txt").read())
	class_combinations = list(combinations(class_ques.keys(),2))
	print len(class_combinations)
	for i in class_combinations:
		print 'Class : ', i #eval(open('ques.txt').read()).values()[500]
		#print 'Object : ', obj[i]
		input_cls = []
		for j in i:
			inp = np.zeros((len(ix_to_class_obj.keys()),))
			inp[class_obj_to_ix[j]] = 1
			input_cls.append(inp)
		val = enc_dec.test_predict(np.array([input_cls]), ix_to_first_word, vocab_to_ix, ix_to_vocab)
		# pdb.set_trace()
		ques = ix_to_first_word[val[0][0][1].tolist().index(max(val[0][0][1]))] + ' '
		for l in val[1][0][1:]:
			ques += ix_to_vocab[l.tolist().index(max(l))] + ' '
		print ques
		print '-'*100
		#time.sleep(2)
		#pdb.set_trace()
		x = 0
		other_flag = 0
		for k in class_ques[i[0]]:
			if(k in ques):
				x+=1
				if (i[0] == 'other'):
					other_flag = 1
		for k in class_ques[i[1]]:
			if(k in ques):
				x+=1
				if (i[0] == 'other'):
					other_flag = 1
		#pdb.set_trace()
		if(x==2):
			print "correct"
			c+=1
		# elif(x==1 and class_ques['other'][0] in ques and not other_flag):
		# #     c+=0.5
		#     c+=1

		# if classes[i] == 'clothing' and ques == 'What is the person in the image wearing ? ':
		#     c += 1
		# if classes[i] in ques.split(' '):
		#     c += 1
		# if classes[i] == "vehicles" and "vehicle(s)" in ques.split(' '):
		#     c+=1
		# if classes[i] == "instruments" and "instruments" in ques.split(' '):
		#     c+=1
		# if classes[i] == 'other' and ques == 'Which of the following is present in the image ? ':
		#     c += 1
	print  c
	print 'Accuracy : ', (c/float(len(class_combinations))) * 100
	'''
	val = enc_dec.test_predict(np.array([ei[0]]),ix_to_first_word, vocab_to_ix, ix_to_vocab)
	print ix_to_first_word[val[0][0][0].tolist().index(max(val[0][0][0]))], ' ',
	for i in val[1][0][1:]:
		print ix_to_vocab[i.tolist().index(max(i))], ' ',
	print 
	'''

def test_gru(class_pair):
	enc_dec = pickle.load(open('../../../code/RNN/enc_dec/trained_multiple_10ep_30k.p'))
	inputs = pickle.load(open('../../../data/enc_dec_inputs_pair.pickle'))
	targets = pickle.load(open('../../../data/enc_dec_targets_pair.pickle'))
	ix_to_first_word = pickle.load(open('../../../data/ix_to_first_word_pair.pickle'))
	first_word_to_ix = pickle.load(open('../../../data/first_word_to_ix_pair.pickle'))
	vocab_to_ix = pickle.load(open('../../../data/vocab_to_ix_pair.pickle'))
	ix_to_vocab = pickle.load(open('../../../data/ix_to_vocab_pair.pickle'))
	ix_to_class_obj = pickle.load(open('../../../data/ix_to_class_obj_pair.pickle'))
	class_obj_to_ix = pickle.load(open('../../../data/class_obj_to_ix_pair.pickle'))
	model_q = pickle.load(open('../../../data/questions_pair.pickle'))
	model_cls = pickle.load(open('../../../data/classes_obj_pair.pickle'))
	classes = open('../../../code/RNN/create_dataset/classes_obj_pair.txt').read().split(';')
	# del classes[classes.index('other')]
	# del classes[classes.index('people')]
	obj = eval(open("../../../code/RNN/create_dataset/objects.txt").read())
	c = 0

	#class_ques = eval(open("../../../data/class_ques_lookup.txt").read())
	#class_combinations = list(combinations(class_ques.keys(),2))
	#print len(class_combinations)
	#for i in class_combinations:
	#print 'Class : ', class_pair #eval(open('ques.txt').read()).values()[500]
	#print 'Object : ', obj[i]
	input_cls = []
	for j in class_pair:
		inp = np.zeros((len(ix_to_class_obj.keys()),))
		inp[class_obj_to_ix[j]] = 1
		input_cls.append(inp)
	val = enc_dec.test_predict(np.array([input_cls]), ix_to_first_word, vocab_to_ix, ix_to_vocab)
	# pdb.set_trace()
	ques = ix_to_first_word[val[0][0][1].tolist().index(max(val[0][0][1]))] + ' '
	for l in val[1][0][1:]:
		ques += ix_to_vocab[l.tolist().index(max(l))] + ' '
	print ques
	#print '-'*100

if __name__ == "__main__":
	
	# if len(sys.argv) < 3:
	#     print "Run script as : "
	#     print "[1] python train_test.py train model_file"
	#     print "[2] python train_test.py test model_file"
	#     #exit()
	
	inputs = pickle.load(open('../../../data/enc_dec_inputs.pickle'))
	targets = pickle.load(open('../../../data/enc_dec_targets.pickle'))
	# ix_to_first_word = pickle.load(open('../../../data/ix_to_first_word.pickle'))
	# first_word_to_ix = pickle.load(open('../../../data/first_word_to_ix.pickle'))
	# vocab_to_ix = pickle.load(open('../../../data/vocab_to_ix.pickle'))
	# ix_to_vocab = pickle.load(open('../../../data/ix_to_vocab.pickle'))
	# ix_to_class_obj = pickle.load(open('../../../data/ix_to_class_obj.pickle'))
	# class_obj_to_ix = pickle.load(open('../../../data/class_obj_to_ix.pickle'))
	# model_q = pickle.load(open('../../../data/questions.pickle'))
	# model_cls = pickle.load(open('../../../data/classes_obj.pickle'))
	if(sys.argv[1] == "single"):
		test(sys.argv[2])
	else:
		train_gru(inputs,targets)
		test_gru((sys.argv[2],sys.argv[3]))
		
	#test_gru([('other','clothing')])
	#train_gru(inputs,targets)
	
	# if sys.argv[1] == "train":
	#     train(sys.argv[2])
	# if sys.argv[1] == "test":
	#     test(sys.argv[2])
	
