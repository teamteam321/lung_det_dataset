import os
import csv
import json

current_path = os.path.dirname(os.path.abspath(__file__))

# folder 
#target_folder = current_path+'/result_075'

#image path
#image_path_lidc = "/notebooks/VOLUME_sdb_5TB/PNG/LIDC_075"
#image_path_lndb = "/notebooks/VOLUME_sdb_5TB/PNG/LNDb_075"


def csv2cocojson(target_csv, image_path_lidc, image_path_lndb):

    dupimg={}
    imid=0
    anid=0

    loadpath= target_csv

    savepath= target_csv.replace('.csv', '.json')




    from PIL import Image

    wjson={"info":{"year":2020,"version":"1",
                   "description":"Exported using VGG Image Annotator (http://www.robots.ox.ac.uk/~vgg/software/via/)",
                   "contributor":"","url":"http://www.robots.ox.ac.uk/~vgg/software/via/",
                   "date_created":"Thu Apr 02 2020 17:40:37 GMT+0700 (Indochina Time)"},
                "images":[],
                "annotations":[],
                "licenses":[{"id":1,"name":"Unknown","url":""}],
                "categories":[{"id":1,"name":"nodule","supercategory":"nodule"}]
          }
    with open(loadpath, 'r') as csvfile:
        reader = csv.reader(csvfile, skipinitialspace=True)
        for row in reader:
            #print(row)
            rownum=row
            row=row[0]
            imgpath=""
            if  "LIDC-IDRI" in row:
                imgpath = image_path_lidc
                imginfo = row[row.index('LIDC-IDRI'):row.index('LIDC-IDRI')+14]
                imgname = row[row.rindex('LIDC-IDRI'):row.index('_Nodule_')] + ".png"
            else:
                imgpath = image_path_lndb
                imginfo = row[row.index('LNDb-'):row.index('LNDb-')+14]
                imgname = row[row.rindex('LNDb-'):row.index('_Nodule_')] + ".png"


            im = Image.open(os.path.join(imgpath,imginfo,imgname))
            width, height = im.size
            x1 = int(rownum[1])
            y1 =  int(rownum[2])
            x2 = int(rownum[3])
            y2 =  int(rownum[4])
            xlen=abs(x1-x2)
            ylen=abs(y1-y2)
            area=xlen*ylen
            boxlist=[x1,y1,x2,y1,x2,y2,x1,y2]

            if imgname not in dupimg:
                dupimg.update({imgname:imid})
                wjson["images"].append({"id":imid,
                                       "width":width,
                                       "height":height,
                                       "file_name":imgname,
                                       "license":1,
                                       "date_captured":""
                                       })

                wjson["annotations"].append({"id":anid,
                                            "image_id":imid,
                                            "category_id":1,
                                            "segmentation":boxlist,
                                            "area":area,
                                            "bbox":[x1,y1,xlen,ylen],
                                            "iscrowd":0})
                imid=imid+1
            else:
                key=dupimg[imgname]
                #print(key)
                wjson["annotations"].append({"id":anid,
                                            "image_id":key,
                                            "category_id":1,
                                            "segmentation":boxlist,
                                            "area":area,
                                            "bbox":[x1,y1,xlen,ylen],
                                            "iscrowd":0})
            anid=anid+1

    with open(savepath, 'w') as outfile:
        json.dump(wjson, outfile,separators=(',', ':'))
    #print(len(wjson['images']))
    return len(wjson['images']), len(wjson['annotations'])
    
    
    