from encoder_decoder import *
import pickle
import sys
import time
from enc_dec_gru_sutskever_vinyals import EncoderDecoderRnn as ecr

def train(model_file):
    enc_dec = encoder_decoder(len(first_word_to_ix.keys()), len(ix_to_class_obj.keys()), 100, len(vocab_to_ix.keys()), 30, 100)
    enc_dec.train(inputs, targets, 15, vocab_to_ix, first_word_to_ix, model_q)
    enc_dec.save('../../../data/' + model_file)

def test(model_file):
    enc_dec = load('../../../data/' + model_file)
    classes = open('../create_dataset/classes_obj.txt').read().split(';')
    # del classes[classes.index('other')]
    # del classes[classes.index('people')]
    obj = eval(open("../create_dataset/objects.txt").read())
    c = 0
    for i in range(len(classes)):
        print 'Class : ', classes[i] #eval(open('ques.txt').read()).values()[500]
        print 'Object : ', obj[i]
        ques = enc_dec.predict_question([class_obj_to_ix[classes[i]]], ix_to_first_word, ix_to_vocab, model_q)
        print ques
        #time.sleep(2)
        #pdb.set_trace()
        if classes[i] == 'clothing' and ques == 'What is the person in the image wearing ?':
            c += 1
        elif classes[i] in ques.split(' '):
            c += 1
        elif classes[i] == "vehicles" and "vehicle(s)" in ques.split(' '):
             c+=1
        elif classes[i] == "instruments" and "instrument(s)" in ques.split(' '):
            c+=1
        elif classes[i] == 'other' and ques == 'Which of the following is present in the image ?':
            c += 1
    print  c
    print 'Accuracy : ', (c/float(len(classes))) * 100

def test_gru(inputs,targets):
    enc_dec = ecr([len(ix_to_class_obj.keys()),100,len(ix_to_first_word.keys())], [len(ix_to_vocab.keys()),100,len(ix_to_vocab.keys())], output_layer=None)
    
    #ei = [np.zeros((len(ix_to_first_word.keys()),1)) for i in inputs]
    ei = []
    for i in inputs:
        inp = np.zeros((len(ix_to_class_obj.keys()),))
        inp[i] = 1
        ei.append(np.array([inp]))
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
#    enc_dec.train(ei,eo,di,do,max_iter=100)
#    enc_dec.save('trained.p')
    enc_dec = load('trained.p')
    classes = open('../create_dataset/classes_obj.txt').read().split(';')
    # del classes[classes.index('other')]
    # del classes[classes.index('people')]
    obj = eval(open("../create_dataset/objects.txt").read())
    c = 0
    for i in range(len(classes)):
        print 'Class : ', classes[i] #eval(open('ques.txt').read()).values()[500]
        print 'Object : ', obj[i]
        inp = np.zeros((len(ix_to_class_obj.keys()),))
        inp[class_obj_to_ix[classes[i]]] = 1
        val = enc_dec.test_predict(np.array([[inp]]), ix_to_first_word, vocab_to_ix, ix_to_vocab)
        ques = ix_to_first_word[val[0][0][0].tolist().index(max(val[0][0][0]))] + ' '
        for i in val[1][0][1:]:
            ques += ix_to_vocab[i.tolist().index(max(i))] + ' '
        print ques
        #time.sleep(2)
        #pdb.set_trace()
        if classes[i] == 'clothing' and ques == 'What is the person in the image wearing ?':
            c += 1
        elif classes[i] in ques.split(' '):
            c += 1
        elif classes[i] == "vehicles" and "vehicle(s)" in ques.split(' '):
             c+=1
        elif classes[i] == "instruments" and "instrument(s)" in ques.split(' '):
            c+=1
        elif classes[i] == 'other' and ques == 'Which of the following is present in the image ?':
            c += 1
    print  c
    print 'Accuracy : ', (c/float(len(classes))) * 100
    '''
    val = enc_dec.test_predict(np.array([ei[0]]),ix_to_first_word, vocab_to_ix, ix_to_vocab)
    print ix_to_first_word[val[0][0][0].tolist().index(max(val[0][0][0]))], ' ',
    for i in val[1][0][1:]:
        print ix_to_vocab[i.tolist().index(max(i))], ' ',
    print 
    '''
if __name__ == "__main__":
    '''
    if len(sys.argv) < 3:
        print "Run script as : "
        print "[1] python train_test.py train model_file"
        print "[2] python train_test.py test model_file"
        #exit()
    '''
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
    test_gru(inputs,targets)
    '''
    if sys.argv[1] == "train":
        train(sys.argv[2])
    if sys.argv[1] == "test":
        test(sys.argv[2])
    '''
