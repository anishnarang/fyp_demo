import pickle
from gensim.models import Word2Vec

ques = pickle.load(open("../../../data/image_wise_quesn_pair.pickle",'rb'))
classes_obj = []
obj = []
initial_questions = []
for k in ques:
    obj.append(k[2])
    if k[-1] == 1:
        # 1 means question based on class, append the class
        classes_obj.append(k[0])
    else:
        # append the object
        classes_obj.append(k[2])
    initial_questions.append(k[1])

open("objects_pair.txt","w").write(str(obj))
# questions = []
# for q in initial_questions:
#     words = q.split(" ")
#     last_word = words[-1]
#     del words[-1]
#     words.append(last_word.split("?")[0])
#     words.append("?")
#     questions.append(" ".join(words))

# classes = list(set(classes))
# questions = list(set(questions))

questions = initial_questions



model_cls = Word2Vec([[i] for i in classes_obj] , size=30, window=1, min_count=1, workers=4)
pickle.dump(model_cls, open("../../../data/classes_obj_pair.pickle",'wb'))


open("classes_obj_pair.txt","w").write(";".join(classes_obj))
open("questions_pair.txt","w").write(";".join(questions))

inputs = []
targets = []
d = eval(open('ques_annotations_pair.txt').read())
ques_vocab = set()
first_words = set()
class_obj = set()

for c in classes_obj:
    class_obj.add(c)
    
for q in questions:
    for i in q.split(' '):
        ques_vocab.add(i)
    first_words.add(q.split(' ')[0])
ques_vocab.add('and')
ix_to_first_word = {i: w for i, w in enumerate(first_words)}
first_word_to_ix = {w: i for i, w in enumerate(first_words)}
vocab_to_ix = {w: i for i, w in enumerate(ques_vocab)}
ix_to_vocab = {i: w for i, w in enumerate(ques_vocab)}
ix_to_class_obj = {i: c for i, c in enumerate(class_obj)}
class_obj_to_ix = {c: i for i, c in enumerate(class_obj)}

for i in range(len(d)-1):
    if d[i][-1] == 1:
        # send class
        # inputs.append(model_cls[tup[0]])
        temp = []
        temp.append(class_obj_to_ix[d[i][0]])
        j = i
        while d[j][0] == d[i][0] and j < len(d)-2:
            j += 1
        temp.append(class_obj_to_ix[d[j][0]])
        inputs.append(temp)
    else:
        # send obj
        # inputs.append(model_cls[tup[2]])
        temp = []
        temp.append(class_obj_to_ix[d[i][2]])
        j = i
        while d[j+1][2] == d[i][2] and j < len(d)-2:
            j += 1
        temp.append(class_obj_to_ix[d[j][2]])
        inputs.append(temp)
    targets.append(d[i][1].replace(' ?','') + ' and ' + d[j][1])

pickle.dump(inputs, open('../../../data/enc_dec_inputs_pair.pickle', 'wb'))
pickle.dump(targets, open('../../../data/enc_dec_targets_pair.pickle', 'wb'))
pickle.dump(ix_to_vocab, open('../../../data/ix_to_vocab_pair.pickle', 'wb'))
pickle.dump(ix_to_first_word, open('../../../data/ix_to_first_word_pair.pickle', 'wb'))
pickle.dump(vocab_to_ix, open('../../../data/vocab_to_ix_pair.pickle', 'wb'))
pickle.dump(first_word_to_ix, open('../../../data/first_word_to_ix_pair.pickle', 'wb'))
pickle.dump(ix_to_class_obj, open('../../../data/ix_to_class_obj_pair.pickle', 'wb'))
pickle.dump(class_obj_to_ix, open('../../../data/class_obj_to_ix_pair.pickle', 'wb'))

model_q = Word2Vec([q.split(" ") for q in targets], size=30, window=1, min_count=1, workers=4)
pickle.dump(model_q, open("../../../data/questions_pair.pickle",'wb'))