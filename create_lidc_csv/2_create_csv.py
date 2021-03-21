import os
import json



# IMPORTANT!!!!!
current_path = os.path.dirname(os.path.abspath(__file__))

# merged label (from)
merged_label_3d = "/temp"+"/3d_union.json"

# new spacing
new_spacing = 0.75

# csv output path
out_csv_name = current_path+'/result/'+'LIDC_reduce_100.csv'

# default png path (path in csv file)
png_path = "/notebooks/VOLUME/LIDC/"


def takefirst(elem):
    return elem[0]

with open(current_path+'/important_data/LIDC_CropPosition_075.json', 'r') as file:
    cropData = json.load(file,)

with open(current_path+'/important_data/filter.json', 'r') as file:
    wrong_fil = json.load(file,)

# annotation final container
csvList = []


raw_anno = current_path+merged_label_3d

with open(raw_anno, 'rb') as k:
    raw_anno = json.load(k)


for i in range(len(raw_anno["data"])):

    case_anno = raw_anno["data"][i]
    case_posi = case_anno["position"]
    case_name = case_anno["case_name"]

    if case_name in wrong_fil:
        continue

    kkk = len(case_posi)
    #print(kkk)
    for siz in range(kkk):
        for k in case_posi[siz]:
            xyz = case_posi[siz][k]
            # initialized temp xyz list with void to fill
            temp = []
            for ext in xyz:
                # print("DEBUG:",ext['z'])
                xlen = int(cropData[case_name]["x2"]) - \
                    int(cropData[case_name]["x1"]) + 1
                ylen = int(cropData[case_name]["y2"]) - \
                    int(cropData[case_name]["y1"]) + 1

                x1 = (ext["x1"] * case_anno["VoxSpaceX"] / new_spacing) - \
                    int(cropData[case_name]["x1"]) - 10 - 1
                if(x1 < 0):
                    x1 = 0
                x2 = (ext["x2"] * case_anno["VoxSpaceX"] / new_spacing) - \
                    int(cropData[case_name]["x1"]) + 10 - 1
                if(x2 > xlen):
                    x2 = xlen-1
                y1 = (ext["y1"] * case_anno["VoxSpaceY"] / new_spacing) - \
                    int(cropData[case_name]["y1"]) - 10 - 1
                if(y1 < 0):
                    y1 = 0
                y2 = (ext["y2"] * case_anno["VoxSpaceY"] / new_spacing) - \
                    int(cropData[case_name]["y1"]) + 10 - 1

                if(y2 > ylen):
                    y2 = ylen-1
                z = (ext["z"] * case_anno["VoxSpaceZ"] /
                     new_spacing) - int(cropData[case_name]["z1"])

                x1 = int(round(x1))
                x2 = int(round(x2))
                y1 = int(round(y1))
                y2 = int(round(y2))
                z = int(round(z))
                # print("after:",z)
                # added
                temp.append([z, x1, y1, x2, y2])

            temp.sort(key=takefirst)
            ratiovoid = []
            voidstep = 0
            sum_ratio = 0
            for zzz in range(len(temp)-1):

                frame_x = temp[zzz]
                frame_next = temp[zzz+1]
                voidstep = frame_next[0]-frame_x[0]
                sum_ratio += voidstep

                pathPng = png_path + case_name + "/" + \
                    case_name + "_frame_" + str(frame_x[0])+"_Nodule_"+ str(siz+1) + ".png"
                csv = [pathPng, frame_x[1], frame_x[2],
                       frame_x[3], frame_x[4], "tumor"]
                # main frame

                if frame_x[0] == frame_next[0]:
                    continue
                csvList.append(csv)

                ratiovoid = [frame_next[1]-frame_x[1], frame_next[2]-frame_x[2],
                             frame_next[3]-frame_x[3], frame_next[4]-frame_x[4]]
                for step in range(1, voidstep):
                    new_x1 = round(frame_x[1]+ratiovoid[0] / voidstep*step)

                    new_x2 = round(frame_x[2]+ratiovoid[1] / voidstep*step)
                    new_y1 = round(frame_x[3]+ratiovoid[2] / voidstep*step)
                    new_y2 = round(frame_x[4]+ratiovoid[3] / voidstep*step)
                    pathPng2 = png_path + case_name + "/" + case_name + \
                        "_frame_" + str(frame_x[0]+step) +"_Nodule_"+ str(siz+1) + ".png"
                    csv2 = [pathPng2, new_x1, new_x2, new_y1, new_y2, "tumor"]
                    # artificial frame
                    csvList.append(csv2)
            # if len(temp) != 0:
            # for step in range(1):

            frame_x = temp[-1]
            new_x1 = round(frame_x[1])
            new_x2 = round(frame_x[2])
            new_y1 = round(frame_x[3])
            new_y2 = round(frame_x[4])
            pathPng3 = png_path + case_name + "/" + \
                case_name + "_frame_" + str(frame_x[0]) +"_Nodule_"+ str(siz+1) + ".png"

            csv3 = [pathPng3, new_x1, new_x2, new_y1, new_y2, "tumor"]
            csvList.append(csv3)
            # csv +=csv2 +

import csv

with open(out_csv_name, 'w', newline = '') as csvFile:
    writer = csv.writer(csvFile)
    
    writer.writerows(csvList)
csvFile.close()
