import random, re

classes_obj = eval(open('google_api/class_wise.txt').read())
images_obj = eval(open('google_api/image_wise.txt').read())
classes = classes_obj.keys()
d = {}

for c in range(len(classes)):
    if len(classes_obj[classes[c]].keys()) >= 2:
        # create question if there are more than 2 objects per class
        q_list = [] # add created questions to this list
        obj_class = classes[c].split('.')[0] # remove the .n.01 added by WordNet
        r = random.randint((c + 1)%len(classes), len(classes_obj.keys())-1) # get other objects to be given as options
        r2 = 0
        if len(classes_obj[classes[r]].keys()) < 2:
        	r2 = random.randint((c + 2)%len(classes), len(classes_obj.keys())-1)
        q_list.append('What are the ' + re.sub(r'_', r' ', obj_class) + 's present in the image set?')
        q_list.append('What are the ' + re.sub(r'_', r' ', obj_class) + 's present in the image grid?')
        q_list.append('Identify the ' + re.sub(r'_', r' ', obj_class) + 's present in the image set.')
        q_list.append('Identify the ' + re.sub(r'_', r' ', obj_class) + 's present in the image grid.')
        q_list.append('Which are the different ' +  re.sub(r'_', r' ', obj_class) + 's present in the image set?')
        q_list.append('Which are the different ' +  re.sub(r'_', r' ', obj_class) + 's present in the image grid?')
        q_list.append('Choose the ' + re.sub(r'_', r' ', obj_class) + 's not present in the image set?')
        q_list.append('Choose the ' + re.sub(r'_', r' ', obj_class) + 's not present in the image grid?')
        d[classes[c]] = {}
        d[classes[c]]['ans'] = classes_obj[classes[c]].items()
        d[classes[c]]['opt'] = classes_obj[classes[r]].items()
        if r2:
        	d[classes[c]]['opt'].extend(classes_obj[classes[r2]].items())
        d[classes[c]]['questions'] = q_list

print len(d.keys()), d.keys()
open('mca_mcq.txt','w').write(str(d))