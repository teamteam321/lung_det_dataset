import os
import matplotlib.pyplot as plt
import json
import nibabel as nib

import numpy as np
import cv2

# create lndb csv nodule annotation

current_path = os.path.dirname(os.path.abspath(__file__))

# mask in nii.gz format
path = current_path+"/merge_niigz_filtered_zoom"

# json crop position
lndb_crop_pos = '/notebooks/VOLUME_sdb_5TB/script/create_lndb_csv/newcroplndb.json'

# output file name or path
outfile = 'result/LNDb_annotation_075.csv'

def progress(count, total, status=''):
    import sys 
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()
    
def bbox2_2D(img):

    r = np.any(img, axis= 1)
    c = np.any(img, axis= 0)

    rmin, rmax = np.where(r)[0][[0, -1]]
    cmin, cmax = np.where(c)[0][[0, -1]]

    return rmin, rmax, cmin, cmax

with open( lndb_crop_pos , 'r') as file:
    crop = json.load( file )
    
csv_list = []

folderWalk = next(os.walk(path))
total = len(folderWalk[2])

folderWalk[2].sort()

for i,file in enumerate(folderWalk[2][:300]):
    # debugging perpose
    #if i >= 50:
    #    break
    
    progress(i, total, status=file)

    #if file.split(".")[0].replace("_Union","") in trainTest["train"]:
    #    continue
    pathMask = os.path.join(path,file)
    loaded_labels = nib.load(pathMask)
    labels = loaded_labels.get_fdata()
    #print(labels)

    

    labels = np.fliplr(np.rot90(labels,3))
    
    labels = labels.astype(np.uint8)
    index = labels.shape[2]
    image_name = file.split(".")[0].replace("_Union","")
    png_dir_path = "LNDb_png_space0_-1300_300/" + image_name
    for i in range(index):
        s = i - crop[file.replace("_Union","")]['z1']
        png_path = "/notebooks/VOLUME/LNDb/" + png_dir_path + "/" + image_name + "_frame_" + str(s+1)
        num_label = np.unique(labels[...,i])
        if len(num_label) == 1:
            continue
        num_label = np.delete(num_label,0)
        
        for j in num_label:
            label_temp = np.where(labels[...,i] == j, 1 , 0)
            box = bbox2_2D(label_temp)
            x1,x2,y1,y2 = box[2],box[3],box[0],box[1]
            area = (x2 - x1) * (y2 - y1)
            #area = (x2 - x1 + 1) * (y2 - y1 + 1)
            if area <= 4:
                continue

            x1 = x1 - 1 - 10
            x2 = x2 - 1 + 10
            y1 = y1 - 1 - 10
            y2 = y2 - 1 + 10

            name = file.replace("_Union","")
            
            x1 = x1 - crop[name]['x1']
            if(x1 < 0):
                x1 = 0

            x2 = x2 - crop[name]['x1']
            if(x2 > crop[name]['x2'] - crop[name]['x1'] ):
                x2 = crop[name]['x2'] - crop[name]['x1']
                
            #flip crop coordination Y only
            
            newY2 = labels.shape[0]-crop[name]['y1']
            newY1 = labels.shape[0]-crop[name]['y2']
            
            # ALTERNATIVE OF NOFLIP
            # newY1 = crop[name]['y1']
            # newY2 = crop[name]['y2']
            
#             y1 = y1 - crop[name]['y1'] 
#             if(y1 < 0):
#                 y1 = 0

#             y2 = y2 - crop[name]['y1'] 
#             if(y2 > crop[name]['y2'] - crop[name]['y1']):
#                 y2 = crop[name]['y2'] - crop[name]['y1']

            y1 = y1 - newY1 
            if(y1 < 0):
                y1 = 0

            y2 = y2 - newY1 
            if(y2 > newY2 - newY1):
                y2 = newY2 - newY1

            list = [png_path+"_Nodule_"+str(j)+".png",x1,y1,x2,y2,"tumor"]
            csv_list.append(list)
    
    

    
import csv
with open(outfile , 'w', newline = '') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(csv_list)
csvFile.close()
            
        
