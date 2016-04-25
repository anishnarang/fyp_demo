from shutil import copy
import os

path = raw_input('Enter the path with the live images \n')
dst_path = 'app/static/'
live_annotations = {}
live_images = []
live_class_obj = {}
live_all_tuples = []

for f in os.listdir(path):
    if f.endswith('png') or f.endswith('jpg'):    
        copy(path + f, dst_path)
        c_o_l = eval(raw_input('Enter list of (class,obj) for ' + f + '\n')) #class_obj_list
        live_all_tuples.extend(c_o_l)
        live_images.append(f)
        live_annotations[f.split('.')[0]] = []
        live_annotations[f.split('.')[0]].extend(c_o_l)
        for i in c_o_l:
            if i[0] not in live_class_obj.keys():
                live_class_obj[i[0]] = []
                live_class_obj[i[0]].append(i[1])
            else:
                live_class_obj[i[0]].append(i[1])


for k in live_class_obj.keys():
    live_class_obj[k] = list(set(live_class_obj[k]))

live_all_tuples = list(set(live_all_tuples))
open('app/main/live_annotations.txt','w').write(str(live_annotations))
open('app/main/live_class_obj.txt','w').write(str(live_class_obj))
open('app/static/live_images.txt','w').write(str(live_images))
open('app/main/code/flickr30k/live_all_tuples.txt','w').write(str(live_all_tuples))

    
        
