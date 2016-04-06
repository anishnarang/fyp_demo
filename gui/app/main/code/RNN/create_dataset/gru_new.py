'''
Created on 11-Nov-2015
Modified: 18 Jan 2015 from gru.py
@author: Anantharaman Narayana Iyer
This version implements the GRU
'''
import numpy as np
import pickle
import copy, pdb

class GRU(object):
    '''Implements GRU'''
    def __init__(self, nx, nh, nk, output_layer=None, alpha=0.1, bptt_truncate=15):
        self.bptt_truncate = bptt_truncate
        self.input_size = nx # size of input dimensions
        self.hidden_size = nh # size of hidden layer of neurons
        self.output_size = nk # size of output layer of neurons
        self.alpha = float(alpha)
        self.output_layer = output_layer
        self.activations = None # this will be set up by forward()
        
        # model parameters: Z gate for nh memory blocks
        self.Wz = np.random.randn(self.hidden_size, self.input_size)*0.01 # input xt to input gate
        self.Uz = np.random.randn(self.hidden_size, self.hidden_size)*0.01 # hidden units ht-1 to input gate
        self.bz = np.zeros((self.hidden_size, 1)) # bias for Z gate        
        # model parameters: forget gate for nh memory blocks
        self.Wr = np.random.randn(self.hidden_size, self.input_size)*0.01 # input xt to forget gate
        self.Ur = np.random.randn(self.hidden_size, self.hidden_size)*0.01 # hidden units ht-1 to forget gate
        self.br = np.zeros((self.hidden_size, 1)) # bias for forget gate
        # model parameters: cell state for nh memory blocks - let us assume 1 cell per block now
        self.W = np.random.randn(self.hidden_size, self.input_size)*0.01 # input xt to cell state
        self.U = np.random.randn(self.hidden_size, self.hidden_size)*0.01 # hidden units ht-1 to cell state
        self.b = np.zeros((self.hidden_size, 1)) # bias for cell state
        # output layer model parameters
        self.Wyh = np.random.randn(self.output_size, self.hidden_size)*0.01 # hidden to output
        self.by = np.zeros((self.output_size, 1)) # output bias
        
        # params for adagrid
        
        # model parameters: Z gate for nh memory blocks
        self.mWz = np.zeros_like(self.Wz) # input xt to input gate
        self.mUz = np.zeros_like(self.Uz) # hidden units ht-1 to input gate
        self.mbz = np.zeros_like((self.bz)) # bias for Z gate        
        # model parameters: forget gate for nh memory blocks
        self.mWr = np.zeros_like(self.Wr) # input xt to forget gate
        self.mUr = np.zeros_like(self.Ur) # hidden units ht-1 to forget gate
        self.mbr = np.zeros_like((self.br)) # bias for forget gate
        # model parameters: cell state for nh memory blocks - let us assume 1 cell per block now
        self.mW = np.zeros_like(self.W) # input xt to cell state
        self.mU = np.zeros_like(self.U) # hidden units ht-1 to cell state
        self.mb = np.zeros_like(self.b) # bias for cell state
        # output layer model parameters
        self.mWyh = np.zeros_like(self.Wyh) # hidden to output
        self.mby = np.zeros_like(self.by) # output bias

        self.final_hidden = [] # this stores the final hidden vectors that can be used for enc-dec pattern

        return
    def sigmoid(self,x):
        return (1.0/(1.0 + np.exp(-x)))
    def tanh(self,x):
        return np.tanh(x)
    def forward_step(self, theta, xt, ht_1, targets, pred):
        #print self.Wz.shape, xt.shape
        a1 = np.dot(theta["Wz"], xt)
        a2 = np.dot(theta["Uz"], ht_1)
        a3 = theta["bz"]
        zt = self.sigmoid(a1 + a2 + a3)
        rt = self.sigmoid(np.dot(theta["Wr"], xt) + np.dot(theta["Ur"], ht_1) + theta["br"])
        htil = self.tanh(np.dot(theta["W"], xt) + rt * np.dot(theta["U"], ht_1) + theta["b"]) # check elementwise mul
        #htil = self.tanh(np.dot(theta["W"], xt) + np.dot(theta["U"], ht_1) + theta["b"]) # check elementwise mul
        ht = zt * ht_1 + (1-zt) * htil
        #ht =  htil
        net_t = np.dot(theta["Wyh"], ht) + theta["by"]
        if pred or (targets is not None):
            if self.output_layer == None:
                yt = np.exp(net_t) / np.sum(np.exp(net_t))
            elif self.output_layer == "logistic":
                yt = self.sigmoid(net_t)
            elif self.output_layer == "linear":
                yt = net_t
            else:
                yt = None
        else: # targets = None
            yt = 0.0
        return (zt, rt, htil, ht, yt) #(None, None, htil, ht, yt)#
    def forward(self, theta, seq, targets=None, pred=False, ht_1=None):
        #pdb.set_trace()
        self.activations = []
        if ht_1 is None:
            ht_1 = np.array([0] * self.hidden_size).reshape(self.hidden_size, 1) # default initialization = 0
        if targets is not None:
            for xt, tgt in zip(seq, targets):
                xt1 = np.array(xt).reshape(len(xt), 1)
                (zt, rt, htil, ht, yt) = self.forward_step(theta, xt1, ht_1, tgt, pred)
                ht_1 = ht
                self.activations.append({"input": xt1, "zgate": zt, "rgate": rt, "htil": htil, "h": ht, "y": yt })
        else:
            for xt in seq:
                xt1 = np.array(xt).reshape(len(xt), 1)
                (zt, rt, htil, ht, yt) = self.forward_step(theta, xt1, ht_1, None, pred)
                ht_1 = ht
                self.activations.append({"input": xt1, "zgate": zt, "rgate": rt, "htil": htil, "h": ht, "y": yt })
            
        return self.activations

    def get_output_error(self, yt, tgt):
        if self.output_layer == "logistic":
            derivative = yt * (1 - yt)
        else:
            derivative = 1
        return -(tgt-yt) * derivative #(tgt-yt) * derivative
    def compute_loss(self, y, t, loss=0.0):
        if self.output_layer == None:
            loss += -t * np.log(y) # softmax (cross-entropy loss)
        elif self.output_layer == "linear":
            loss += 0.5 * ((y-t) ** 2)
        return loss
    
    def backward(self, theta, tgt, dhnext=None):
        initial_ht = np.zeros_like(theta["b"]) # default initialization = 0
        dWyh = np.zeros_like(theta["Wyh"])
        dby = np.zeros_like(theta["by"])
        acts = self.activations
        loss = 0.0
        
        dWz = np.zeros_like(theta["Wz"])
        dUz = np.zeros_like(theta["Uz"])
        dWr = np.zeros_like(theta["Wr"])
        dUr = np.zeros_like(theta["Ur"])
        dW = np.zeros_like(theta["W"])
        dU = np.zeros_like(theta["U"])

        dbz = np.zeros_like(theta["bz"])
        dbr = np.zeros_like(theta["br"])
        db = np.zeros_like(theta["b"])
        
        if dhnext is None:
            dhnext = np.zeros_like(theta["b"])
        
        for t in reversed(xrange(len(acts))):
            if tgt[t] is not None:
                # compute errors for output stage
                #pdb.set_trace()
                tgt1 = np.array(tgt[t]).reshape(len(tgt[t]), 1)
                loss = self.compute_loss(acts[t]["y"], tgt1, loss)
                #print "loss from bac = ", loss
                dy = self.get_output_error(acts[t]["y"], tgt1)
                dh1 = np.dot(theta["Wyh"].T, dy)
                #print "dh1 shape = ", dh1.shape, " dy shape = ", dy.shape
                dh = dh1 + dhnext #+ np.dot(self.Wch.T, next_delta_h)
                #print "E = ", dy, dy.shape, acts[t]["h"].shape
                dWyh += np.dot(dy, acts[t]["h"].T)
                dby += dy
            else:
                #dy = np.zeros_like(acts[0]["y"])
                dy = np.zeros_like(self.by)
                dh = dhnext
                #print "in None case, dy shape = ", dy.shape
            
            # compute error at the hidden layer dh (this will be propagated inside the cell)            
            #next_delta_h = 0 # set this to delta ht_1 #dhnext_Uz + dhnext_Ur + dhnext_U
            if t == 0 :
                a = initial_ht
            else:
                a = acts[t-1]["h"]
            ha = a - acts[t]["htil"]
            delta_z = dh * ha # elementwise mul
            delta_htilda = dh * (1-acts[t]["zgate"])

            db_new = delta_htilda * (1.0 - (acts[t]["htil"] ** 2))
            db += db_new
            dW +=  np.dot(db_new, acts[t]["input"].T)
            dU += np.dot(db_new * acts[t]["rgate"], a.T)
            
            delta_rt = delta_htilda * (1-acts[t]["htil"] ** 2) * np.dot(theta["U"], a) # should this be transpose of U?
            
            dbz_new = delta_z * acts[t]["zgate"] * (1.0 - acts[t]["zgate"])
            dbz += dbz_new
            dWz += np.dot(dbz_new, acts[t]["input"].T)
            dUz += np.dot(dbz_new, a.T)

            dbr_new = delta_rt * acts[t]["rgate"] * (1.0 - acts[t]["rgate"])
            dbr += dbr_new
            dWr += np.dot(dbr_new , acts[t]["input"].T)            
            dUr += np.dot(dbr_new, a.T)
                
            dhnext_Uz = np.dot(theta["Uz"].T, dbz_new) 
            dhnext_Ur = np.dot(theta["Ur"].T, dbr_new) 
            dhnext_U = np.dot(theta["U"].T, db_new * acts[t]["rgate"])
            dhnext_ht = dh * acts[t]["zgate"]            
            dhnext = dhnext_Uz + dhnext_Ur + dhnext_U + dhnext_ht
#  
#             for dparam in [dW, dWz,  dWr, dU,  dUz, dUr, dWyh]:
#                 np.clip(dparam, -50, 50, out=dparam) # clip to mitigate exploding gradients
#
        return {"loss": np.sum(loss), 
                "deltas": {
                    "Wyh": dWyh, 'Wz':dWz,'Uz':dUz,'W':dW,'U':dU,'Wr':dWr,'Ur':dUr,
                    "bz": dbz, "br": dbr, "b": db, "by": dby
                    },
                "dhnext": dhnext
                }
    
    def train(self, inputs, targets, output_layer = None, max_iter = 30):
        for i in range(max_iter):
            loss = 0.0
            print "#" * 100
            print "in iter: ", i
            print len(inputs), len(targets)
            for sample, target in zip(inputs, targets):
                theta = {'Wyh': self.Wyh, 'Wz':self.Wz,'Uz':self.Uz,'W':self.W,'U':self.U,'Wr':self.Wr,'Ur':self.Ur,
                         'bz': self.bz, 'br': self.br, 'b': self.b, 'by': self.by}        
                #print "sample = ", sample
                self.forward(theta, sample, target)
                #print self.activations
                result = self.backward(theta, target) 
                loss += result["loss"]
            
                # perform parameter update with Adagrad
                for param, dparam, mem in zip([self.Wyh, self.Wz, self.Wr, self.W, self.Uz, self.Ur, self.U, self.bz, self.br, self.b, self.by], 
                                            [result["deltas"]["Wyh"], result["deltas"]["Wz"],
                                             result["deltas"]["Wr"], result["deltas"]["W"],
                                             result["deltas"]["Uz"], result["deltas"]["Ur"],
                                             result["deltas"]["U"], result["deltas"]["bz"],
                                             result["deltas"]["br"], result["deltas"]["b"], result["deltas"]["by"]], 
                                            [self.mWyh, self.mWz, self.mWr, self.mW, self.mUz, self.mUr, self.mU, self.mbz, self.mbr, self.mb, self.mby]):
                    #print "mem = ", param, dparam, mem
                    mem += dparam * dparam
                    param += -self.alpha * dparam / np.sqrt(mem + 1e-8) # adagrad update
            print "loss = ", loss
        return

    def predict(self, x_seq1, h_enc=None, output_layer=None, only_final = False):
        """ 
        sample a sequence of integers from the model 
        h is memory state, x_seq is the input sequence that we want to classify
        """
        theta = {'Wyh': self.Wyh, 'Wz':self.Wz,'Uz':self.Uz,'W':self.W,'U':self.U,'Wr':self.Wr,'Ur':self.Ur,
                 'bz': self.bz, 'br': self.br, 'b': self.b, 'by': self.by}
        
        self.final_hidden = []
        
        ret = []
        seq_num = 0

        for x_seq in x_seq1:
            results = []

            if h_enc == None:
                hprev = np.zeros((self.hidden_size,1)) # reset RNN memory
            else:
                hprev = h_enc[seq_num]
            
            #hprev = np.zeros((self.hidden_size,1)) # reset RNN memory
            seq_num += 1
            xs, hs, ys, ps = {}, {}, {}, {}
            hs[-1] = np.copy(hprev)
            acts = self.forward(theta, x_seq, pred=True, ht_1=hprev)
            for t in xrange(len(x_seq)):
                ys[t] = acts[t]["y"] #np.dot(self.Why, hs[t]) + self.by # unnormalized log probabilities for next chars                
                if output_layer == None:
                    ps[t] = ys[t] #np.exp(ys[t]) / np.sum(np.exp(ys[t])) # probabilities for next chars
                elif output_layer == "linear":
                    ps[t] = ys[t]
                if only_final:
                    if t == len(x_seq) - 1:
                        results.append(ps[t])
                    else:
                        results.append(None)
                else:
                    results.append(ps[t])
            # following code helps the enc-dec
            final_t = len(x_seq) - 1
            self.final_hidden.append(acts[final_t]["h"])
            ret.append(results)
        return ret #results

    
    def get_rnn_hidden(self):
        return self.final_hidden
    
    def lossfunc(self, theta, x_seq, t_seq):
        self.forward(theta, x_seq, pred=True)
        results = self.backward(theta, t_seq)
        return results

    def gradient_check(self, x_seq, t_seq, num_checks=1): #
        from random import  uniform
        epsilon = 0.0001
        param = {'Wyh': self.Wyh, 'Wz':self.Wz,'Uz':self.Uz,'W':self.W,'U':self.U,'Wr':self.Wr,'Ur':self.Ur,
                 'bz': self.bz, 'br': self.br, 'b': self.b, 'by': self.by}
        theta_backup = copy.copy(param)
        results = self.lossfunc(param, x_seq, t_seq) # get the baseline results (loss, deltas)
        for key, val in param.items():
            theta_shape = param[key].shape
            print "---------------   Checking for theta = ", key, "  -------------------------------"
             
            for i in range(num_checks):
                param_vec = val.flatten() # get the theta as a vector
                print "Test: ", i,  " for grad check of: ", key
                ri = int(uniform(0, val.size))
                param_vec[ri] += epsilon # we perturb one element of theta at a time
                theta = param_vec.reshape(theta_shape) # set model with perturbed values
                param[key] = theta
                results_1 = self.lossfunc(param, x_seq, t_seq) # compute loss with this perturbation
                param[key] = copy.copy(theta_backup[key])
                param_vec = val.flatten() #restore the original model
                param_vec[ri] -= epsilon # we perturb one element of theta at a time
                param[key] = param_vec.reshape(theta_shape) # set model with perturbed values
                results_2 = self.lossfunc(param, x_seq, t_seq)
                param[key] = copy.copy(theta_backup[key]) # restore
                
                print "Losses: ", results_1['loss'], results_2['loss']
                grad1 = (results_1['loss'] - results_2['loss']) / (2 * epsilon)
                grad = results["deltas"][key].flatten()[ri] 
                print "numeric grad: ",grad1,", grad: ", grad, ", difference: ", grad-grad1 
        #grad = grad[self.limit0 : self.limit1]
#         return {'cost': results["loss"], 'grad': results["deltas"], 'numeric_grad': grad1}

if __name__ == "__main__":
    limit = 100
    nh = 16
    inputs = [[[1,0,0,0,0,0,0,0,0,0,0,0], [0,1,0,0,0,0,0,0,0,0,0,0], [0,0,1,0,0,0,0,0,0,0,0,0], [0,0,0,1,0,0,0,0,0,0,0,0], [0,0,0,0,1,0,0,0,0,0,0,0]]]
    inputs.append([[1,0,0,0,0,0,0,0,0,0,0,0], [0,0,1,0,0,0,0,0,0,0,0,0], [0,0,0,0,1,0,0,0,0,0,0,0], [0,0,0,0,0,0,1,0,0,0,0,0], [0,0,0,0,0,0,0,0,1,0,0,0]])
    inputs.append([[0,1,0,0,0,0,0,0,0,0,0,0], [0,0,0,1,0,0,0,0,0,0,0,0], [0,0,0,0,0,1,0,0,0,0,0,0], [0,0,0,0,0,0,0,1,0,0,0,0], [0,0,0,0,0,0,0,0,0,1,0,0]])
    
    targets = [[[0,1,0,0,0,0,0,0,0,0,0,0], [0,0,1,0,0,0,0,0,0,0,0,0], [0,0,0,1,0,0,0,0,0,0,0,0], [0,0,0,0,1,0,0,0,0,0,0,0], [0,0,0,0,0,1,0,0,0,0,0,0]]]
    targets.append([[0,0,1,0,0,0,0,0,0,0,0,0], [0,0,0,0,1,0,0,0,0,0,0,0], [0,0,0,0,0,0,1,0,0,0,0,0], [0,0,0,0,0,0,0,0,1,0,0,0], [0,0,0,0,0,0,0,0,0,0,1,0]])
    targets.append([[0,0,0,1,0,0,0,0,0,0,0,0], [0,0,0,0,0,1,0,0,0,0,0,0], [0,0,0,0,0,0,0,1,0,0,0,0], [0,0,0,0,0,0,0,0,0,1,0,0], [0,0,0,0,0,0,0,0,0,0,0,1]])
    nx = len(inputs[0][0])
    ny = 12
    targets = inputs
    tr = raw_input("Train?: ")
    gru = GRU(nx, nh, ny)
    gru.train(inputs[:limit], targets[:limit]) 
    #else:
    #    gru = pickle.load(open(pic_file))
    print("\n\n*************************************************")  
    import pdb; pdb.set_trace()
    print(gru.predict([inputs[0]]))
    print targets[0]     
