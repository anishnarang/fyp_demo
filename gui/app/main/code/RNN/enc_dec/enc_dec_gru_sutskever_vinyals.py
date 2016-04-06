'''
Created on 10-Feb-2016
@author: Anantharaman Narayana Iyer
This implements the model described in the paper by Sutskever etal but using gru_new module
'''
from gru_new import GRU as MyRnn
import numpy as np
import pickle
def load(filename):
    return pickle.load(open(filename))

class EncoderDecoderRnn(object):
    """Implements an encoder decoder RNN pattern"""
    def __init__(self, params1, params2, output_layer=None):
        #params1 and params2 refer to the parameters for encoder and decoder respectively
        self.output_layer = output_layer
        self.encoder = MyRnn(params1[0], params1[1], params1[2], output_layer=output_layer)
        self.decoder = MyRnn(params2[0], params2[1], params2[2], output_layer=output_layer)
        #self.decoder = DecoderRnn(params2[0], params2[1], params2[2], output_layer=output_layer)
        self.h_enc = None
        return
    def train(self, inputs1, targets1, inputs2, targets2, max_iter=2, epochs=1, output_layer=None):
        """
            train the enc-dec with the following:
            for each seq (x1, y1, x2, y2)
                - enc forward
                - dec forward
                - dec backward
                - enc backward
        """
        iteration = 0 # p keeps track of sequence index
        while True:
            seq_num = 0
            loss = 0.0
            loss1 = 0.0
            for X1, Y1, X2, Y2 in zip(inputs1, targets1, inputs2, targets2):
                #inputs1 is a list of char sequences (word) where each element in a seq is char in one hot form
                #targets1 is a list of targets for each sequence where each element in the seq is the tgt char in 1-h form
                #inputs2 are the list of input seq to the decoder
                #targets2 are corresponding targets for the decoder
                #X1, Y1, X2, Y2 are one sequence in the list for encoder and decoder
                # eg of X1, Y1, X2, Y2 is:  Alcatel$  l  letaclA   etaclA$  (all in 1 hot form)

                theta = {'Wyh': self.encoder.Wyh, 'Wz':self.encoder.Wz,'Uz':self.encoder.Uz,'W':self.encoder.W,
                         'U':self.encoder.U,'Wr':self.encoder.Wr,'Ur':self.encoder.Ur,
                         'bz': self.encoder.bz, 'br': self.encoder.br, 'b': self.encoder.b, 'by': self.encoder.by}
                     

                theta1 = {'Wyh': self.decoder.Wyh, 'Wz':self.decoder.Wz,'Uz':self.decoder.Uz,'W':self.decoder.W,
                         'U':self.decoder.U,'Wr':self.decoder.Wr,'Ur':self.decoder.Ur,
                         'bz': self.decoder.bz, 'br': self.decoder.br, 'b': self.decoder.b, 'by': self.decoder.by}
                     
                acts = self.encoder.forward(theta, X1, Y1)
                self.encoder.final_hidden.append(acts[-1]["h"]) # this is the encoder final stage ht

                # now we would have got the ht of the final stage of the encoder - eh
                # let us now do forward of decoder
                acts1 = self.decoder.forward(theta1, X2, Y2, ht_1=acts[-1]["h"])
                
                # now we need to do the backward for decoder
                result = self.decoder.backward(theta1, Y2) 
                loss1 += result["loss"]
            
                # perform parameter update with Adagrad for DECODER
                for param, dparam, mem in zip([self.decoder.Wyh, self.decoder.Wz, self.decoder.Wr, self.decoder.W, 
                                               self.decoder.Uz, self.decoder.Ur, self.decoder.U, 
                                               self.decoder.bz, self.decoder.br, self.decoder.b, self.decoder.by], 
                                            [result["deltas"]["Wyh"], result["deltas"]["Wz"],
                                             result["deltas"]["Wr"], result["deltas"]["W"],
                                             result["deltas"]["Uz"], result["deltas"]["Ur"],
                                             result["deltas"]["U"], result["deltas"]["bz"],
                                             result["deltas"]["br"], result["deltas"]["b"], result["deltas"]["by"]], 
                                            [self.decoder.mWyh, self.decoder.mWz, self.decoder.mWr, self.decoder.mW, 
                                             self.decoder.mUz, self.decoder.mUr, self.decoder.mU, 
                                             self.decoder.mbz, self.decoder.mbr, self.decoder.mb, self.decoder.mby]):
                    mem += dparam * dparam
                    param += -self.decoder.alpha * dparam / np.sqrt(mem + 1e-8) # adagrad update

                # Let us do the backward for encoder, propagating from the decoder
                result = self.encoder.backward(theta, Y1, dhnext=result["dhnext"])
                loss += result["loss"]
                
                # perform parameter update with Adagrad for encoder
                for param, dparam, mem in zip([self.encoder.Wyh, self.encoder.Wz, self.encoder.Wr, self.encoder.W, 
                                               self.encoder.Uz, self.encoder.Ur, self.encoder.U, 
                                               self.encoder.bz, self.encoder.br, self.encoder.b, self.encoder.by], 
                                            [result["deltas"]["Wyh"], result["deltas"]["Wz"],
                                             result["deltas"]["Wr"], result["deltas"]["W"],
                                             result["deltas"]["Uz"], result["deltas"]["Ur"],
                                             result["deltas"]["U"], result["deltas"]["bz"],
                                             result["deltas"]["br"], result["deltas"]["b"], result["deltas"]["by"]], 
                                            [self.encoder.mWyh, self.encoder.mWz, self.encoder.mWr, self.encoder.mW, 
                                             self.encoder.mUz, self.encoder.mUr, self.encoder.mU, 
                                             self.encoder.mbz, self.encoder.mbr, self.encoder.mb, self.encoder.mby]):
                    mem += dparam * dparam
                    param += -self.encoder.alpha * dparam / np.sqrt(mem + 1e-8) # adagrad update
                
            if iteration % 1 == 0:
                print 'iter %d' % (iteration,) # print progress
                print "enc loss = ", loss, " dec loss = ", loss1
            iteration += 1 # iteration counter
            if iteration >= max_iter:
                print "Training completed %d iterations" % (iteration)
                break
        return #self.final_hidden
       
    def test_predict(self, inputs1, ix_to_first_word, vocab_to_ix, ix_to_vocab, output_layer=None, max_len = 48):
        """Predict the output sequence, use $ as the termination, 
        max seq len is given by max_len that ensures termination after finite steps"""
        final_output = []
        e_results = self.encoder.predict(inputs1, output_layer=output_layer, only_final = True)
        h_enc = self.encoder.get_rnn_hidden() # get the thought vectors - note predict() will overwrite
        print "len of e res = ", len(e_results) 
        for i, result in enumerate(e_results):
            if result != None:
                h_enc1 = [h_enc[i].tolist()]
                predicted_char = "a" #some char not equal to $
                seq_len = 0
                f_output = [result[-1]] # include the encoders final stage output in the result set
                index = np.argmax(result[-1])
#                vec = [0] * len(result[-1])
#                vec[index] = 1
                fw = ix_to_first_word[index]
                vec = np.zeros((len(vocab_to_ix.keys()),))
                vec[vocab_to_ix[fw]] = 1
                inputs2 = [[vec]] #[[sm]] #d_results                    
                while predicted_char != "?": # we use $ to terminate
                    if seq_len >= max_len:
                        print "max seq len exceeded"
                        break
                    seq_len += 1
                    
                    d_results = self.decoder.predict(inputs2, h_enc=h_enc1, output_layer=output_layer, only_final = False)
                    softmax_result = d_results[0][0]
                    sm = [r[0] for r in softmax_result]
                    f_output.append(softmax_result)
                    index = np.argmax(softmax_result)
                    predicted_char = ix_to_vocab[index]
                    vec = [0] * len(sm)
                    vec[index] = 1
                    inputs2 = [[vec]] #[[sm]] #d_results                    
                    h_enc1 = [self.decoder.get_rnn_hidden()[0]]
                    #print sm, len(sm), len(h_enc1) #softmax_result
                final_output.append(f_output)
            else: #result none
                print "Result = None", result
        print len(final_output)
        return (e_results, final_output)

    def save(self,filename):
        pickle.dump(self,open(filename,"wb"))
