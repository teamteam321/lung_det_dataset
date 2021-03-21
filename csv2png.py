import os
import skimage
from skimage.morphology import disk, dilation, remove_small_objects,erosion, closing, reconstruction, binary_closing, binary_dilation ,binary_erosion
from skimage.measure import label,regionprops, perimeter
from skimage.filters import roberts, sobel
from skimage import measure, feature
from skimage.segmentation import clear_border
from scipy import ndimage as ndi
import nibabel as nib
import numpy as np
import cv2
import json
import os
import csv
import glob
import multiprocessing
from multiprocessing import Pool
from tqdm import tqdm
current_path = os.path.dirname(os.path.abspath(__file__))

LNDb = False

#crop json
CROPPOS = "/notebooks/VOLUME_sdb_5TB/CROP_POSITION/075/LIDC_CropPosition_ori.json"
#csv
CROPANNO = '/notebooks/VOLUME_sdb_5TB/script/create_lidc_csv/result/LIDC_annotation_0_75.csv'
#zoomed nifti
DRIVEPATH = "/notebooks/VOLUME_sdb_5TB/NIFTI_075/LIDC/"
#png path
PICPATH = os.path.join(current_path,"fold_split_and_coco/OUTPUT_PNG/LIDC/")

if LNDb:
    CROPPOS = "/notebooks/VOLUME_sdb_5TB/CROP_POSITION/075/newcroplndb.json"
    CROPANNO = '/notebooks/VOLUME_sdb_5TB/script/create_lndb_csv/result/LNDb_train_075.csv'
    DRIVEPATH = "/notebooks/VOLUME_sdb_5TB/NIFTI_075/LNDb/"
    PICPATH = os.path.join(current_path,"fold_split_and_coco/OUTPUT_PNG/LNDb/")

#png path (all pics with no folder)
PICPATH_ALL = os.path.join(current_path,"fold_split_and_coco/OUTPUT_PNG/ALL/")

#draw rectangle bbox
bbox_debug = False

def bbox2_3D(img):

    r = np.any(img, axis=(1, 2))
    c = np.any(img, axis=(0, 2))
    z = np.any(img, axis=(0, 1))

    rmin, rmax = np.where(r)[0][[0, -1]]
    cmin, cmax = np.where(c)[0][[0, -1]]
    zmin, zmax = np.where(z)[0][[0, -1]]

    return rmin, rmax, cmin, cmax, zmin, zmax
    
def lidc2fast(dict_crop):
    
    
  
    txtfile = dict_crop['name']
    
    
    #extract case name
    if 'LIDC' in txtfile:
        name = txtfile[txtfile.rindex("LIDC"):txtfile.rindex("LIDC")+14]
    else:
        name = txtfile[txtfile.rindex("LNDb"):txtfile.rindex("LNDb")+14]
        
    #print(DRIVEPATH+name+"*.nii.gz")
    file = glob.glob(DRIVEPATH+name+"*.nii.gz")
    if len(file) == 0:
        print("File not  founnd")
        return
    file = file[0]


    z_start = 0
    z_end = 0
    z_list = []
    anno_z = open(CROPANNO)
    #print(name)
    linez = anno_z.readline()
    xx = True
    while linez :
        if name in linez:
            xx = False
            break
        linez = anno_z.readline()
    
    if xx:
        return

    xy_list = []
    oo = 0
    while True:
        z_list.append(int(linez[linez.rindex("_frame_")+7:linez.index("_Nodule_")]))
        xy_list.append(linez[linez.index(".png")+5:linez.rindex(",")])
        #print(xy_list[oo])
        oo+=1
        linez = anno_z.readline()



        if name not in linez:
            #print(linez)
            break
    anno_z.close()
    z_start = min(z_list)
    z_end = max(z_list)


    loaded_images = nib.load(file)
    images = loaded_images.get_fdata() 
    images = np.rot90(images,1)
    imagedum = images
    lenbefore = len(images)
    
   
    newY2 = images.shape[0]-dict_crop['y1']
    newY1 = images.shape[0]-dict_crop['y2']
    #print('newY ',newY1,newY2)
    
#     print(dict_crop)
#     ddn = bbox2_3D(images_lung_mask)
#     print(ddn)
#     z_len = images.shape[-1]
#     print(z_len)

    images = images[dict_crop['y1']:dict_crop['y2']+1,dict_crop['x1']:dict_crop['x2']+1,dict_crop['z1']:dict_crop['z2']+1]
    #images = images[ddn[0]:ddn[1]+1,ddn[2]:ddn[3]+1,z_len-ddn[5]:z_len-ddn[4]+1]
    #images = images[]
    #if 'LNDb' in txtfile:
    #    images = images[newY1:newY2+1,dict_crop['x1']:dict_crop['x2']+1,dict_crop['z1']:dict_crop['z2']+1]
    #else:
    #    images = images[dict_crop['y1']:dict_crop['y2']+1,dict_crop['x1']:dict_crop['x2']+1,dict_crop['z1']:dict_crop['z2']+1]

        
    img_nor = images.astype(np.float32)
    img_nor = img_nor + 1300.0
    img_nor = np.where(img_nor < 0.0, 0.0, img_nor)
    img_nor = (img_nor / 1600.0)
    img_nor = np.where(img_nor > 1.0, 1.0, img_nor)
    index = img_nor.shape[2]
    img_new = np.empty((img_nor.shape[0],img_nor.shape[1],3))
         
    space = 0
    dis = space + 1
        
    for i2 in range(int(z_start),int(z_end)+1) :
            if not i2 in z_list:
                continue
            if i2 < dis:
                img1 = img_nor[..., i2]*255
            else:
                img1 = img_nor[..., i2-dis]*255
    
            img2 = img_nor[..., i2]*255
    
            if i2 >= index-dis:
                img3 = img_nor[..., i2]*255
            else:
                img3 = img_nor[..., i2+dis]*255
            
            
            img_new[:,:,0] = img1
            img_new[:,:,1] = img2
            img_new[:,:,2] = img3
            img_new = img_new.astype(np.uint8)
            
            #png save path
            #pathW = PICPATH
            fileName = name
            
            
            ext = ".png"

            ##
            temp_boxx = []
            
            for lll in range(len(z_list)):
                if z_list[lll] == i2:
                    temp_boxx.append(xy_list[lll])
            
            #LNDb RAI need to flip
            if 'LNDb' in fileName:
                img_new = cv2.flip(img_new,0)
            
            

            for boxes in temp_boxx:
                sttr = boxes.split(",")
                cropx1 = int(sttr[0])
                cropy1 = int(sttr[1])
                cropx2 = int(sttr[2])
                cropy2 = int(sttr[3])
                
                #draw box nodule -- debugging perpose
                if bbox_debug:
                    img_new = cv2.rectangle(img_new,(cropx1,cropy1),(cropx2,cropy2),(255,255,255),1)
                
            
            
            if not os.path.exists(os.path.join(PICPATH,fileName)):
                os.makedirs(os.path.join(PICPATH,fileName))
            if not os.path.exists(os.path.join(PICPATH_ALL)):
                os.makedirs(os.path.join(PICPATH_ALL))
            
            cv2.imwrite(os.path.join(PICPATH,fileName,fileName +"_frame_" + str(i2) + ext), img_new)
            cv2.imwrite(os.path.join(PICPATH_ALL,fileName +"_frame_" + str(i2) + ext), img_new)
            
            
            
            
def main():
    
    with open (CROPPOS) as j:
        jr = json.load(j)

    newlist = []
    for k in jr:
        jr[k]['name'] = k
        newlist.append(jr[k])
        
    
    
    #print(newlist[0])

    #lidc2fast(newlist[0])
    #lidc2fast(newlist[139])
    processes=multiprocessing.cpu_count()
    processes = 1
    print("Thread:"+str(processes))

    #from itertools import repeat
    with Pool(processes) as pool:
       #pool.map(lidc2fast, newlist,len(newlist)//processes) 
        r = list(tqdm(pool.imap(lidc2fast, newlist), total=len(newlist)))

    
    
   
     
if __name__ == "__main__":
    main()