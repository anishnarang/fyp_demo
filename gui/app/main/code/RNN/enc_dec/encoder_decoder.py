from rnn import *

def load(filename):
    return pickle.load(open(filename))

class encoder_decoder(object):


    def __init__(self, enc_output_dim, enc_input_dim, enc_hidden_size, dec_output_dim, dec_input_dim, dec_hidden_size):
        '''
        Initialise parameters for the encoder and decoder
        '''
        self.encoder = RNN(enc_output_dim, enc_input_dim, enc_hidden_size)
        self.decoder = RNN(dec_output_dim, dec_input_dim, dec_hidden_size)

    def _minimize_loss(self, weights_derivatives_mem, rnn_type):
        '''
        Minimize the loss function by adagrad update
        '''
        for (param, dparam, mem) in weights_derivatives_mem:
            mem += dparam * dparam
            param += -rnn_type.learning_rate * dparam / np.sqrt(mem + 1e-8)

    def train(self, inputs, targets, num_epochs, vocab_to_ix, first_word_to_ix, model_q):
        '''
        Invoke BPTT for num_epochs
        '''
        enc_mWxh, enc_mWhh, enc_mWhy = np.zeros_like(self.encoder.Wxh), np.zeros_like(self.encoder.Whh), np.zeros_like(
        self.encoder.Why)
        enc_mbh, enc_mby = np.zeros_like(self.encoder.bh), np.zeros_like(self.encoder.by)  # memory variables for Adagrad
        dec_mWxh, dec_mWhh, dec_mWhy = np.zeros_like(self.decoder.Wxh), np.zeros_like(self.decoder.Whh), np.zeros_like(
            self.decoder.Why)
        dec_mbh, dec_mby = np.zeros_like(self.decoder.bh), np.zeros_like(self.decoder.by)  # memory variables for Adagrad
        dec_smooth_loss = -np.log(
            1.0 / self.decoder.output_dim) * self.decoder.input_dim  # loss at iteration 0 (not sure if it should be self.input_dim)
        enc_smooth_loss = -np.log(1.0 / self.encoder.output_dim) * self.encoder.input_dim
        for i in xrange(num_epochs):
            hprev = np.zeros((self.encoder.hidden_size, 1))  # reset RNN memory every epoch
            for j in xrange(len(inputs)):
                # Encoder forward pass
                enc_xs, enc_hs, enc_ps, enc_loss = self.encoder.BPTT([inputs[j]], [first_word_to_ix[targets[j].split(' ')[0]]], hprev, 'enc', xs=None, hs=None, ps=None, loss=None, forward=True)
                # smooth_loss = smooth_loss * 0.999 + loss * 0.001

                # Decoder Forward pass
                #pdb.set_trace()
                dec_xs, dec_hs, dec_ps, dec_loss = self.decoder.BPTT([model_q[word] for word in targets[j].split(' ')[:-1]], [vocab_to_ix[word] for word in targets[j].split(' ')[1:]], enc_hs[len([inputs[j]])-1], 'dec', xs=None, hs=None, ps=None, loss=None, forward=True)

		# Decoder Back pass
                dec_loss, dec_dWxh, dec_dWhh, dec_dWhy, dec_dbh, dec_dby, dec_hprev = self.decoder.BPTT(
                    [model_q[word] for word in targets[j].split(' ')[:-1]],
                    [vocab_to_ix[word] for word in targets[j].split(' ')[1:]], dec_hs[len([model_q[word] for word in targets[j].split(' ')[:-1]])-1], 'dec', xs=dec_xs, hs=dec_hs, ps=dec_ps, loss=dec_loss, forward=False)

                # minimize the loss for decoder
                dec_weights_derivatives_mem = zip(
                    [self.decoder.Wxh, self.decoder.Whh, self.decoder.Why, self.decoder.bh, self.decoder.by],
                    [dec_dWxh, dec_dWhh, dec_dWhy, dec_dbh, dec_dby], [dec_mWxh, dec_mWhh, dec_mWhy, dec_mbh, dec_mby])
                self._minimize_loss(dec_weights_derivatives_mem, self.decoder)
                dec_smooth_loss = dec_smooth_loss * 0.999 + dec_loss * 0.001
                print 'epoch %d, DECODER loss: %f' % (i, dec_smooth_loss)  # print progress

                # Encoder Back pass
                enc_loss, enc_dWxh, enc_dWhh, enc_dWhy, enc_dbh, enc_dby, enc_hprev = self.encoder.BPTT([inputs[j]], [first_word_to_ix[targets[j].split(' ')[0]]], enc_hs[len([inputs[j]])-1], 'enc', xs=enc_xs, hs=enc_hs, ps=enc_ps, loss=enc_loss, forward=False)

                # minimize the loss for deocder
                enc_weights_derivatives_mem = zip(
                    [self.encoder.Wxh, self.encoder.Whh, self.encoder.Why, self.encoder.bh, self.encoder.by],
                    [enc_dWxh, enc_dWhh, enc_dWhy, enc_dbh, enc_dby], [enc_mWxh, enc_mWhh, enc_mWhy, enc_mbh, enc_mby])
                self._minimize_loss(enc_weights_derivatives_mem, self.encoder)
                enc_smooth_loss = enc_smooth_loss * 0.999 + enc_loss * 0.001
                print 'epoch %d, ENCODER loss: %f' % (i, enc_smooth_loss)  # print progress


    def predict_question(self, X, ix_to_first_word, ix_to_vocab, model):
        '''
        Given an input sequence, predict the output
        X : input sequence
        return output label/sequence
        '''
        ps, hs = self.encoder.predict(X, 'enc')
        ques = ''
        word = ix_to_first_word[ps.tolist().index(max(ps))]
        #print word, " ",
		#model = pickle.load(open('ques.p'))
        while (word != '?'):
            #print word, " ",
            ques += word + ' '
            #pdb.set_trace()
            ps, hs = self.decoder.predict([model[word]], 'dec', hs)
            word = ix_to_vocab[ps.tolist().index(max(ps))]
        #print word, "\n"
        ques += word
        #print ques
        return ques

    def save(self,filename):
        '''
        Saves the encoder decoder model
        '''
        pickle.dump(self,open(filename,'wb'))
