import nltk, pickle
from matplotlib import colors

data = eval(open("../../flickr30k/tuples_30k.txt").read())
# data = [('clothing', 'striped polo shirt'), ('scene', 'seated position'), ('vehicles', 'three wheeled bikes')]
ques_list = []
c = 0
class_ques = {}
# in question, 0 indicates question based on object, 1 indicates question based on class
for tup in data:
    print c
    if tup[0] == 'animals' :
        ques_list.append((tup[0], 'What animals are shown in the picture ?',tup[1],1))
        class_ques[tup[0]] = ['What animals are shown in the picture ']

    elif tup[0] == 'vehicles':
        ques_list.append((tup[0],'Which type of vehicle(s) are present in the image ?',tup[1], 1))
        class_ques[tup[0]] = ['Which type of vehicle(s) are present in the image ']
    elif tup[0] == 'people':
        ques_list.append((tup[0], 'Choose the option that best describes the people in the image ?', tup[1], 1))
        class_ques[tup[0]] = ['Choose the option that best describes the people in the image ']

    elif tup[0] == 'clothing':
        ques_list.append((tup[0], 'Identify the type of clothing depicted in the image ?' , tup[1], 1))
        class_ques[tup[0]] = ['Identify the type of clothing depicted in the image ']

    elif tup[0] == 'other':
        ques_list.append((tup[0], 'Which of the following is present in the image ?' , tup[1], 1))
        class_ques[tup[0]] = ['Which of the following is present in the image ']
    elif tup[0] == 'bodyparts':
        ques_list.append((tup[0], 'Identify the bodypart present in the image ?' , tup[1], 1))
        class_ques[tup[0]] = ['Identify the bodypart present in the image ']
    elif tup[0] == 'scene':
        ques_list.append((tup[0], 'Choose the option that best describes the scene ?' , tup[1], 1))
        class_ques[tup[0]] = ['Choose the option that best describes the scene ']
    elif tup[0] == 'instruments':
        ques_list.append((tup[0], 'Select the instruments shown in the image ?' , tup[1], 1))
        class_ques[tup[0]] = ['Select the instruments shown in the image ']
    
    c += 1

open("../../../data/class_ques_lookup.txt","w").write(str(class_ques))
open("ques_annotations.txt","w").write(str(ques_list))
pickle.dump(ques_list, open('../../../data/image_wise_quesn.pickle','wb'))