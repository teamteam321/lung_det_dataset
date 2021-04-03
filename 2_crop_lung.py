import skimage
from skimage.morphology import disk, dilation, remove_small_objects,erosion, closing, reconstruction, binary_closing, binary_dilation ,binary_erosion
from skimage.measure import label,regionprops, perimeter
from skimage.filters import roberts, sobel
from skimage import measure, feature
from skimage.segmentation import clear_border
from scipy import ndimage as ndi
import glob
import os
import nibabel as nib
import numpy as np
import cv2
import json
import os
import csv
import multiprocessing
from multiprocessing import Pool

niigz_path = '/notebooks/VOLUME_sdb_5TB/NIFTI_075/LNDb/*.nii.gz'
out_json = '_LIDC_crop_position.json'
thread_num = 2


temp_dir = '_temp'
current_path = os.path.dirname(os.path.abspath(__file__))


def get_segmented(images):
#     segmented = np.zeros_like( images )
    binary_list = [ get_segmented_lung( images[...,i] )[1] for i in range( 0, images.shape[-1] ) ]
    segmented = np.stack( binary_list, axis=-1 )
    return segmented

def get_segmented_lung( image, th=-300 ):
    backup = image.copy()
    binary = backup < th
    selem = disk(1)
    dilation = binary_dilation(binary, selem)
    cleared = clear_border( dilation )
    label_image = label(cleared)
    areas = regionprops(label_image)
    areas.sort( key=lambda x:x.area, reverse=True )
    
    for area in areas[:2]:
        for r, c in area.coords:
            label_image[ r, c ] = -1
            
    
    large_component = label_image == -1
    selem = disk(3)
    erode = binary_erosion(large_component, selem)
    selem = disk(10)
    closing = binary_closing(erode, selem)
    edges = roberts(closing)
    segmented_binary = ndi.binary_fill_holes(edges)
    backup[ segmented_binary == False ] = np.min(backup)
    segmented_image = backup
    return segmented_image, segmented_binary.astype(np.int)

def bbox2_3D(img):

    r = np.any(img, axis=(1, 2))
    c = np.any(img, axis=(0, 2))
    z = np.any(img, axis=(0, 1))

    rmin, rmax = np.where(r)[0][[0, -1]]
    cmin, cmax = np.where(c)[0][[0, -1]]
    zmin, zmax = np.where(z)[0][[0, -1]]

    return rmin, rmax, cmin, cmax, zmin, zmax






def croop(paths):
    print(paths)
    loaded_images = nib.load(paths)
    images = loaded_images.get_fdata()
    images = np.rot90(images,1)
    ct_mask = get_segmented(images)
    x = bbox2_3D(ct_mask)
    #images = images[x[0]:x[1]+1,x[2]:x[3]+1,x[4]:x[5]+1]
    
    
    
    
    #print(current_path+temp_dir+os.path.basename(path)[:os.path.basename(path).index('.')]+'.txt')
    with open(os.path.join(current_path,temp_dir,os.path.basename(paths)[:os.path.basename(paths).index('.')]+'.txt'), 'w+') as the_file:
        the_file.write(str(x[2])+" "+str(x[3])+" "+str(x[0])+" "+str(x[1])+" "+str(x[4])+" "+str(x[5])+"\n")
        
    
    '''jr[os.path.basename(path)[:path.index('.')]] = {
                        "x1":int(x[2]),
                        "x2":int(x[3]),
                        "y1":int(x[0]),
                        "y2":int(x[1]),
                        "z1":int(x[4]),
                        "z2":int(x[5])}'''



if __name__ == '__main__':
    
    fname = glob.glob(niigz_path)
    
    fname = fname[:5]
    
    
    #name = glob.glob('../NIFTI_050/LNDb/*.nii.gz')
    #create temp path before hand
    if not os.path.exists(os.path.join(current_path,temp_dir)):
        os.mkdir(os.path.join(current_path,temp_dir))
    
    #for t in fname:
        #print(os.path.basename(t))
    #    croop(t)
    #processes=multiprocessing.cpu_count()
    
    with Pool(thread_num) as pool:
        pool.map(croop, fname) 
    
        
    jr = {}
    temp_files = glob.glob(os.path.join(current_path,temp_dir,'*.txt'))
    for x in temp_files:
        t_name = os.path.basename(x)
        t_name = t_name[:t_name.rindex('.')]
        s = open(x,'r')
        ln = s.readline()
        data = ln.split(' ')
        jr[t_name] = {}
        jr[t_name]['x1'] = int(data[0])
        jr[t_name]['x2'] = int(data[1])
        jr[t_name]['y1'] = int(data[2])
        jr[t_name]['y2'] = int(data[3])
        jr[t_name]['z1'] = int(data[4])
        jr[t_name]['z2'] = int(data[5])
        

    with open(os.path.join(current_path,out_json),'w') as we:
        json.dump(jr,we,indent = 4)
    print(fname)



    
    

