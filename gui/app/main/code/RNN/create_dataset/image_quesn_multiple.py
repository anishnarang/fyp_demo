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
        ques_list.append((tup[0], 'What animals are shown in the picture grid ?',tup[1],1))
        class_ques[tup[0]] = ['What animals are shown in the picture grid ']
        # tags = nltk.pos_tag(nltk.word_tokenize(tup[1]))
        # for t in tags:
        #     if t[1] == 'CD': # number 
        #         #ques_list.append((tup[0], 'How many ' + tup[1].replace(t[0],'').strip() + ' are present in the image ?', tup[1], 0))
        #         ques_list.append((tup[0],'How many ' + tup[0] + ' are present in the image ?',tup[1], 1))
        #         class_ques[tup[0]] = ['How many ' + tup[0] + ' are present in the image ']
        #     if t[1] == 'JJ' and t[1] in colors.cnames.keys(): # color
        #         for x in tags:
        #             if x[1] == 'NNS' or x[1] == 'NN':
        #                 ques_list.append((tup[0], 'What is the color of ' + x[0] + ' shown in the image ?', tup[1], 0))

    elif tup[0] == 'vehicles':
        ques_list.append((tup[0],'Which type of vehicle(s) are present in one of the images ?',tup[1], 1))
        class_ques[tup[0]] = ['Which type of vehicle(s) are present in one of the images ']
    elif tup[0] == 'people':
        # tags = nltk.pos_tag(nltk.word_tokenize(tup[1]))
        # for t in tags:
        #     if t[1] == 'CD': # number 
                #ques_list.append((tup[0], 'How many ' + tup[1].replace(t[0],'').strip() + ' are there in the image ?', tup[1], 0))
        ques_list.append((tup[0], 'Choose the option that best describes the people in any of the images shown ?', tup[1], 1))
        class_ques[tup[0]] = ['Choose the option that best describes the people iin any of the images shown ']

    elif tup[0] == 'clothing':
        ques_list.append((tup[0], 'Identify the type of clothing depicted in the picture grid ?' , tup[1], 1))
        class_ques[tup[0]] = ['Identify the type of clothing depicted in the picture grid ']

    elif tup[0] == 'other':
        ques_list.append((tup[0], 'Which of the following is present in one of the 4 images ?' , tup[1], 1))
        class_ques[tup[0]] = ['Which of the following is present in one of the 4 images ']
    elif tup[0] == 'bodyparts':
        ques_list.append((tup[0], 'Identify the bodypart present in any one of the images ?' , tup[1], 1))
        class_ques[tup[0]] = ['Identify the bodypart present in any one of the images ']
    elif tup[0] == 'scene':
        ques_list.append((tup[0], 'Choose the option that best describes the scene shown in any one image ?' , tup[1], 1))
        class_ques[tup[0]] = ['Choose the option that best describes the scene shown in any one image ']
    elif tup[0] == 'instruments':
        ques_list.append((tup[0], 'Select the instruments shown in the picture grid ?' , tup[1], 1))
        class_ques[tup[0]] = ['Select the instruments shown in the picture grid ']
    # else:
    #    if c%2 == 0:
    #        ques_list.append((tup[0], 'What is the type of ' + tup[0] + ' present in the image ?' , tup[1], 1))
    #        class_ques[tup[0]] = ['What is the type of ' + tup[0] + ' present in the image  ', 'Select the type of ' + tup[0] + ' present in the image ']
    #    else:
    #        ques_list.append((tup[0], 'Select the type of ' + tup[0] + ' present in the image ?' , tup[1], 1))
    #        class_ques[tup[0]] = ['What is the type of ' + tup[0] + ' present in the image  ', 'Select the type of ' + tup[0] + ' present in the image ']

    c += 1

# print ques_list
open("../../../data/class_ques_lookup_pair.txt","w").write(str(class_ques))
open("ques_annotations_pair.txt","w").write(str(ques_list))
pickle.dump(ques_list, open('../../../data/image_wise_quesn_pair.pickle','wb'))