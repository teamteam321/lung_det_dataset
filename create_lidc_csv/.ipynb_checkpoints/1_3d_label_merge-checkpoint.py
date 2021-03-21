from collections import namedtuple
import numpy as np
import cv2
import numpy as np
import json
import glob
import cc3d
import cv2
import csv
import nibabel as nib
import os
import copy
from tqdm import tqdm


current_path = os.path.dirname(os.path.abspath(__file__))

# output file
out_json_file = current_path+'/temp'+'/3d_union_test.json'

#Detection = namedtuple("Detection", ["image_path", "gt", "pred"])

def bb_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])#3
    yA = max(boxA[1], boxB[1])#3
    xB = min(boxA[2], boxB[2])#6
    yB = min(boxA[3], boxB[3])#6

    interArea = (xB - xA) * (yB - yA)

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou
    
def savenp(np,x1,y1,x2,y2,z,nodule_no):
    #added np as params
    #for i in range (len(nps))
    for i in range(x1,x2+1):
        for j in range(y1,y2+1):
            nps[z][i][j]=nodule_no
    #np[z,x1:x2+1,y1:y2+1] = nodule_no
    
js={"data":[]}
duplicatelist=[]
name ="LIDC-IDRI-"
file = glob.glob(current_path+"/JSON_less_2-5mm/"+name+"*.json")
print(len(file))
file.sort()
print(len(file))
i2=0
for i in tqdm(range(len(file))):
    # debugging perpose
    #if i >= 10:
    #    break
    with open (file[i]) as j:
        jr = json.load(j)
        if(len(jr["nodule"])==0):
            continue
        actualname = jr["PatientID"]
        if len(jr["nodule"][0]["roi"])==0 or jr["nodule"][0]["roi"][0]["nifti_zpos"]<0 or jr["DimZ"]<jr["nodule"][0]["roi"][0]["nifti_zpos"]  :
            continue
        if actualname in duplicatelist:
            continue
        duplicatelist.append(actualname)
        
        zlist=[]
        
        nps =np.zeros([jr["DimZ"],jr["DimX"],jr["DimY"]],dtype="int")
        #init character dict
        characteristic_info = {}

        char_dict = {}
        for j in range(len(jr["nodule"])):
            #print(jr["nodule"][j]["noduleid"])
            #pre cast int number to string for dict key
            nodule_number = j+1
            #nodule number is contains it self
            char_dict[str(nodule_number)] = []
            char_dict[str(nodule_number)].append(nodule_number)

            #collecting real characteristic infomation for next step
            characteristic_info[str(nodule_number)] = jr["nodule"][j]["characteristic"]
            
            
            for k in range(len(jr["nodule"][j]["roi"])):
                x1=min(jr["nodule"][j]["roi"][k]["x"])
                y1=min(jr["nodule"][j]["roi"][k]["y"])
                x2=max(jr["nodule"][j]["roi"][k]["x"])
                y2=max(jr["nodule"][j]["roi"][k]["y"])
                
                z=jr["nodule"][j]["roi"][k]["nifti_zpos"]
                
                zlist.append(z)
                #j is number of nodule 
                savenp(nps,x1,y1,x2,y2,z,nodule_number)
            #after all boxs in nodule has been added
            #check if previous nodules is missing (override) by new (bigger) nodule
            current_unique = np.unique(nps)
            overriden_list_to_remove = []
            for x in char_dict:
                if int(x) not in current_unique:
                    overriden_list_to_remove.append(x)
                    char_dict[str(nodule_number)].extend(char_dict[x])
            for k in overriden_list_to_remove:
                del char_dict[k]

            
        
        nc=2
        #print(actualname)
        nps_bck = copy.deepcopy(nps)
        #all to 1
        nps[np.where(nps > 0)] = 1
        nps =cc3d.connected_components(nps,connectivity = 6)
        # for debuging only
        # for x in np.unique(nps):
        #     tmp_lst = []
        #     for ks in np.unique(nps_bck[np.where(nps== x) ]):
        #         if ks == 0:
        #             continue
        #         tmp_lst.extend(char_dict[str(ks)])
        #     prnt nodule area after cc3d and its list of original nodule
        #     print(x, tmp_lst)
        # print(np.unique(nps_bck))
        
        #print(char_dict)
        js["data"].append({"case_name":actualname,
                           "VoxSpaceX":jr["VoxSpaceX"], 
                           "VoxSpaceY":jr["VoxSpaceY"],
                           "VoxSpaceZ":jr["VoxSpaceZ"],
                           "nodule_number":int(np.max(nps)),
                           "position":[],
                           "characteristic":[]})
        
        for seg in range(1,np.max(nps)+1):
            js["data"][i2]["position"].append({"nodule{:03d}".format(seg):[]})
            js["data"][i2]["characteristic"].append({"nodule{:03d}".format(seg):[]})
            z,x,y=np.where(nps==seg)
            z = list(dict.fromkeys(z))

            #characteristic inject
            tmp_lst = []
            for ks in np.unique(nps_bck[np.where(nps == seg)]):
                if ks == 0:
                    continue
                tmp_lst.extend(char_dict[str(ks)])

            #for x in tmp_lst:
            #    print(characteristic_info[str(x)])
            

            #print(tmp_lst)
            new_char_list = {}
            #create new char info store (list)
            for kyy in characteristic_info[str(tmp_lst[0])]:
                new_char_list[kyy] = []
                new_char_list[kyy].append(characteristic_info[str(tmp_lst[0])][kyy])
            #adding [1:] char of the nodule in to list
            for x in tmp_lst[1:]:
                for kyy in characteristic_info[str(tmp_lst[0])]:
                    new_char_list[kyy].append(characteristic_info[str(x)][kyy])
            
            #print(new_char_list)
            #print('----')
            js["data"][i2]["characteristic"][seg-1]["nodule{:03d}".format(seg)].append(new_char_list)
            for m in range(min(z),max(z)+1):
                
                x,y=np.where(nps[m]==seg)
                if x.size==0:
                    continue
                if y.size==0:
                    continue
                
                xmin =min(x)
                xmax =max(x)
                ymin =min(y)
                ymax =max(y)
                
                js["data"][i2]["position"][seg-1]["nodule{:03d}".format(seg)].append({"x1":int(xmin),
                                                                                     "y1":int(ymin),
                                                                                     "x2":int(xmax),
                                                                                     "y2":int(ymax),
                                                                                     "z":int(m)})
                
                for n  in range(xmin,xmax+1):
                    for o  in range(ymin,ymax+1):
                        nps[m][n][o]=seg
    i2=i2+1

    
with open(out_json_file, 'w') as outfile:
    json.dump(js, outfile,indent=4)