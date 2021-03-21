
from distutils.dir_util import copy_tree
import os
import glob
from shutil import copyfile

#lidc_png_path = "/notebooks/VOLUME_sdb_5TB/PNG/LIDC_075/"
#lndb_png_path = "/notebooks/VOLUME_sdb_5TB/PNG/LNDb_075/"
#infer_png_path = "/notebooks/VOLUME_sdb_5TB/PNG/INFER_075_"
# INFER_075_1, 2, 3...

def copy_infer(fold_num,lidc_png_path,lndb_png_path,infer_png_path,val_csv_path):
    current_path = os.path.dirname(os.path.abspath(__file__))
    number = 5
    #path = open(current_path+'/fold_split/075/fold'+str(fold_num)+'/val.csv','r')
    temp_path = val_csv_path+'/fold'+str(fold_num)+'/val.csv'
    path = open(temp_path,'r')
    
    ls = []
    kxy = 0
    for s in path:
        kxy+=1
        if 'LIDC' in s:
            kode = s[s.index('LIDC-IDRI'):s.index('LIDC-IDRI')+14]
        else :
            kode = s[s.index('LNDb-'):s.index('LNDb-')+14]
            
        if kode not in ls:
            ls.append(kode)
       
    print(kxy)
    cct = 0 #total copy counter
    kkk = []
    for i,xx in enumerate(ls):

        #x = xx+'_'+str(int(i/30))
        x = xx
        if("LIDC" in x):
            fromDirectory = lidc_png_path+x
            toDirectory = infer_png_path+str(fold_num)+"/"+x
        else:
            fromDirectory = lndb_png_path+x
            toDirectory = infer_png_path+str(fold_num)+"/"+x
        
        #print(fromDirectory+'/*.png')
        #print(glob.glob(fromDirectory+'/*.png'))
            
        for nb,ipath in enumerate(glob.glob(fromDirectory+'/*.png')):
            if not os.path.exists(toDirectory):
                os.makedirs(toDirectory)
            
            copyfile(ipath, toDirectory+ipath[ipath.rindex('/'):])
            #print(ipath)
            #print(toDirectory+ipath[ipath.rindex('/'):])
            
        #break




if __name__ == "__main__":
    print('sdsd')
    for i in range(1,6):
        print(i)
        copy_infer(i)