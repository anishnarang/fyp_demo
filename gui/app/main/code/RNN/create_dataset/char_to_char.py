'''
Created on 07-Jan-2016
@author: Anantharaman Narayana Iyer
This is meant as a toy problem to test enc-dec
'''
#import os
#import random
#from myrnn.myrnn import MyRnn
#from myrnn.enc_dec.enc_dec import EncoderDecoderRnn
#from myrnn.enc_dec.enc_dec_sutskever_vinyals import EncoderDecoderRnn
from enc_dec_gru_sutskever_vinyals import EncoderDecoderRnn
from nltk import word_tokenize, sent_tokenize
import numpy
import pickle
import pdb
#import random
#import string

# text_corpus_file = r"C:\Users\Anantharaman\My Documents\LiClipse Workspace\nbc\rnn_based_dialogue\rnn_dialogue\corpora\ndtv.txt"
# inc_corpus_files = [
#         r"C:\Users\Anantharaman\My Documents\LiClipse Workspace\nbc\rnn_based_dialogue\rnn_dialogue\corpora\ndtv.txt",
#         r"C:\Users\Anantharaman\My Documents\LiClipse Workspace\nbc\rnn_based_dialogue\rnn_dialogue\corpora\consolidated_corpus.txt",
#         r"C:\Users\Anantharaman\My Documents\LiClipse Workspace\nbc\rnn_based_dialogue\rnn_dialogue\corpora\questions.txt",
#     ]
ext_corpus_file = "input.txt"
inc_corpus_files = [
        "input.txt"
    ]
pic_file = "char_to_char_model.p"

def get_words(fname, limit=1000): #limit specifies number of sentences to return
    remove_non_ascii = lambda text: ''.join([i if ord(i) < 128 else ' ' for i in text])
    data = open(fname).read()
    ascii_data = remove_non_ascii(data) #data.encode("ascii", "ignore")
    sents = sent_tokenize(ascii_data)
    words = [word_tokenize(sent) for sent in sents]
    return words[:limit]


"""
def get_strings(count):
    population = string.lowercase[:26] + string.uppercase[:26] + ";[])({}_"
    strings = []
    for c in range(count):
        n1 = random.randint(3, 16) #this is to be used for strlen
        strings.append(random.sample(population, n1))
    return strings
"""
def create_str_dataset(words, limit=10000):
    inputs = []
    targets = []
    for word in words:
        chars = [c for c in word]
        chars_bits_seq = []
        out_bits_seq = []
        # chars is the input sequence, we will now make them numeric and also output strings
        for c in chars:
            vec = [0] * output_units # one hot softmax vector - eg 256 bits to encode ascii of a char
            vec[ord(c)] = 1
            #chars_bits_seq.append(binary(ord(c), 8))
            chars_bits_seq.append(vec)
            if c in "AEIOUaeiou":
                #pass
                #out_bits_seq.append(binary(ord(c), 8)) #if its a vowel we will repeat it
                out_bits_seq.append(vec) #if its a vowel we will repeat it
            #out_bits_seq.append(binary(ord(c), 8))
            out_bits_seq.append(vec)
        
        #insert an <eos> char, which is $ in our implementation
        vec = [0] * output_units
        vec[ord("$")] = 1
        chars_bits_seq.append(vec)
        #out_bits_seq.append(vec)
        out_bits_seq.reverse()
        inputs.append(chars_bits_seq)
        targets.append(out_bits_seq)
        #pdb.set_trace()
        if len(inputs) == limit:
            break
        
    return inputs, targets

def create_dataset_for_enc_dec(inputs1, targets1):
    display = lambda smlist: [chr(sm.index(1)) for sm in smlist if sm != None]
    enc_tgts = []
    dec_tgts = []
    for seq, tgt in zip(inputs1, targets1): # eg seq = the$ and tgt = eht in onehot form
        e_tgts = [None] * len(seq)
        if len(tgt[0]) > 0:
            e_tgts[-1] = tgt[0]
        else: #the following is for situations where the target sequence has just 1 element
            vec = [0] * output_units
            vec[ord("#")] = 1
            e_tgts[-1] = vec #binary(ord("#"), nbits=8)
        enc_tgts.append(e_tgts)
        
        d_tgts = []
        for t in (tgt[1:]): # eg ht in one hot form
            d_tgts.append(t)
        #d_tgts.append(binary(ord("$"), nbits=8))
        
        # we will add a special sign $ to mark end of output
        vec = [0] * output_units
        vec[ord("$")] = 1
        d_tgts.append(vec) # e.g ht$ in one hot
        
        dec_tgts.append(d_tgts) # [ [ [], [].... []], [ [], [].... []], ...]
    #print "len inputs1, targets1, inputs2, targets2 = ", len(inputs1), len(enc_tgts), len(targets1), len(dec_tgts)
    #print "inputs1, targets1, inputs2, targets2 = ", display(inputs1[0]), display(enc_tgts[0]), display(targets1[0]), display(dec_tgts[0])
    #a = xbvx
    return (inputs1, enc_tgts, targets1, dec_tgts) # e.g the$, [none...e], eht, ht$

def binary(num, nbits=8):
    """Converts num to a binary form and returns it as a list: "{0:08b}".format(6)"""
    fmt = "{0:0" + str(nbits) + "b}"
    return [int(c) for c in list(fmt.format(num))]

def test_clf(ds, limit, rnn, max_iter=1, train=None):
    print "len ds0, ds1, ds2, ds3, limit", len(ds[0][:limit]), len(ds[1][:limit]), len(ds[2][:limit]), len(ds[3][:limit]), limit
    #print ds[2][:limit]
    if train:
        rnn.train(ds[0][:limit], ds[1][:limit], ds[2][:limit], ds[3][:limit], max_iter = max_iter)
    results = rnn.test_predict(ds[0][limit:]) #, ds[2][limit:])
    return results #results contain e_results, d_results

def display_encoder_results(tgt, results):
    total = 0
    correct = 0
    for r, e in zip(results, tgt):
        if r != None:
            total += 1
            expected = chr(e[-1].index(1))
            mx = numpy.argmax(r[-1])
            if expected == chr(mx):
                correct += 1
    print "############# ENCODER RESULTS ###############" 
    print "Total tests = ", total, " correct = ", correct, " accuracy = ", float(correct)/total
    return

def display_decoder_results(tgt, results, in_words, tgt_words):
    total = 0
    correct = 0
    
    for word, t_word, result in zip(in_words, tgt_words, results):
        word1 = [chr(c.index(max(c))) for c in word]
        word2 = [chr(c.index(max(c))) for c in t_word]
        print "#" * 100
        print word1, "\t\t=>\t\t", word2
        predicted = []
        for res in result:
            predicted_char = chr(numpy.argmax(res))
            print predicted_char,
            predicted.append(predicted_char)
        if predicted[:-1] == word2:
            correct += 1
        total += 1
        print
    accuracy = (float(correct) / total) * 100.0
    print "Accuracy of exact match: ", accuracy
    return

def display_results(results, ds, limit, in_words, tgt_words):
    display_decoder_results(ds[3][limit:], results[1], in_words, tgt_words)
    display_encoder_results(ds[1][limit:], results[0])
    return

def enc_dec_train(words1, inc=True):
    dataset = create_str_dataset(words1, samples)
    limit = int(len(dataset[0]) * 0.85) # 0.75
    print "total seqs = ", len(dataset[0])
    dataset_1 = create_dataset_for_enc_dec(dataset[0], dataset[1])
    
    if inc:
        max_iter = 10
        rnn = pickle.load(open(pic_file))
    else:
        rnn = EncoderDecoderRnn([nx, nh, ny], [nx, nh, ny], output_layer=None)
        max_iter = 10
    results = test_clf(dataset_1, limit, rnn, max_iter=max_iter, train = True)
    # save the model
    pickle.dump(rnn, open(pic_file, "wb"))
    
    display_results(results, dataset_1, limit, dataset[0][limit:], dataset[1][limit:])
    return

def get_inc_vocabulary(fnlist):
    """Given a list of corpus files return the incremental vocab of last file"""
    vocab = []
    vocab1 = set([])
    for fn in fnlist:
        print "Training with: ", fn
        sents_words = get_words(fn, limit=100000)
        words1 = []
        for sent in sents_words:
            words1.extend(sent)
        print len(words1), " vocab = ", len(set(words1))
        print words1[:20]
        words1 = set(words1)
        result = (words1 - vocab1)
        vocab.extend(words1)
        vocab1 = set(vocab) # this has the union of vocabs got so far
        print "len vocab1 = ", len(vocab1), len(vocab)
    print "len of inc vocab: ", len(result)
    return result

if __name__ == '__main__':
    output_units = 128
    nx = output_units
    nh = 96 #128 #96 # 48 with 10k and 20 iters gave good results
    ny = output_units
    samples = 100000
    max_iter = 3 #20 #15, 30
    #import pdb;pdb.set_trace()
    words1 = get_inc_vocabulary(inc_corpus_files)
    t = raw_input("Train? (INC, YES) : ")
    if t == "YES":
        enc_dec_train(words1, inc=False)
    elif t == "INC":
        enc_dec_train(words1, inc=True)
    
    rnn = pickle.load(open(pic_file))
    limit = 0
    while True:
        inp = raw_input("Enter a string: ")
        print "--------- Length of Input: %d------------" % (len(inp))
        dataset = create_str_dataset(inp.split(), 1)
        dataset_1 = create_dataset_for_enc_dec(dataset[0], dataset[1])
#        pdb.set_trace()
        results = rnn.test_predict(dataset_1[0])
        display_results(results, dataset_1, limit, dataset[0][limit:], dataset[1][limit:])
