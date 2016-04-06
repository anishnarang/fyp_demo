import nltk, pickle
from matplotlib import colors

data = eval(open("../../flickr30k/tuples_10k.txt").read())
# data = ['bodyparts', 'clothing', 'instruments','animals', 'vehicles', 'scene']

# data = [('clothing', 'striped polo shirt'), ('scene', 'seated position'), ('vehicles', 'three wheeled bikes')]
ques_list = []
c = 0
# in question, 0 indicates question based on object, 1 indicates question based on class
for tup in data:
    print c
    if tup[0] not in ['people','other'] :
        if c%2 == 0:
            ques_list.append((tup[0], 'What is the type of ' + tup[0] + ' present in the image ?' , tup[1], 1))
        else:
            ques_list.append((tup[0], 'Select the type of ' + tup[0] + ' present in the image ?' , tup[1], 1))

        c += 1

# for j in data:
#     for i in range(1000):
#         if c%2 == 0:
#             ques_list.append((j, 'What is the type of ' + j + ' present in the image ?' , j, 1))
#         else:
#             ques_list.append((j, 'Select the type of ' + j + ' present in the image ?' , j, 1))
#         c += 1        

# print ques_list
open("ques_annotations.txt","w").write(str(ques_list))
pickle.dump(ques_list, open('../../../data/image_wise_quesn.pickle','wb'))