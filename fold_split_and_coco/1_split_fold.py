
import glob
import os
import json
import cocos
import copy_validation

current_path = os.path.dirname(os.path.abspath(__file__))

# csv contains both info from 2 dataset
csv_path = current_path+'/input_merge_csv/merge075.csv'

# total fold , must be equal to json file in /reference
fold_num = 5

# output path
dataset_name = 'new_dataset_test2'
output_path = current_path+'/fold_result/' + dataset_name

#picture path
image_path_lidc = current_path+"/OUTPUT_PNG/LIDC/"
image_path_lndb = current_path+"/OUTPUT_PNG/LNDb/"
image_all = current_path+"/OUTPUT_PNG/ALL"
image_path_infer = current_path+'/OUTPUT_PNG/INFER_075_'

# coco tfrecord
efficientdet_path = '/notebooks/Test_Env/automl/efficientdet/'
tfrecord_out_path = current_path + '/final_dataset/' + dataset_name


# train script
model_name = 'efficientdet-d2'
ckpt_path = '/notebooks/Test_Env/automl3/efficientdet-d2'
# dir name must contains 'foldx' -- will be raplaced by fold number IE. fold1, fold2...
train_model_dir = '/notebooks/VOLUME_sdb_5TB/EFF_RESULT/'+ dataset_name + '_foldx_result'


#fixed path
efficientdet_main = efficientdet_path + 'main.py'
coco_tfrecord = efficientdet_path + '/dataset/create_coco_tfrecord.py'

def run_fold(f):
    #integer fold number
    fold = 'fold'+str(f)
    with open(current_path+'/reference/'+ fold +'_result.json','r') as fc:
        fold_csv = json.load(fc)
        
    all_csv = open(csv_path,'r')

    traincsv = []
    valcsv = []
    for ln in all_csv:
        if "LNDb" in ln:
            strname = ln[ln.rindex("LNDb"):ln.rindex("LNDb")+14]
            if strname in fold_csv["val"]:
                valcsv.append(ln)
            else:
                traincsv.append(ln)
        else:
            strname = ln[ln.rindex("LIDC"):ln.rindex("LIDC")+14]
            if strname in fold_csv["val"]:
                valcsv.append(ln)
            else:
                traincsv.append(ln)

    if not os.path.exists(os.path.join(output_path,fold)):
        os.makedirs(os.path.join(output_path,fold))
    
    train_csv_path = os.path.join(output_path,fold)+"/train.csv"
    tr = open(train_csv_path,'w')
    tr.writelines(traincsv)
    tr.close()
    # create coco json
    train_images_count, train_anno_count = cocos.csv2cocojson(train_csv_path, image_path_lidc, image_path_lndb)
    # create coco dataset from coco json
    os.system('python '+ coco_tfrecord + ' --logtostderr \
              --image_dir='+ image_all +' \
              --object_annotations_file='+ train_csv_path.replace('.csv','.json') +'\
              --output_file_prefix='+ tfrecord_out_path+'/'+fold+'/train/a' +'\
              --num_shards=32')
    
    val_csv_path = os.path.join(output_path,fold)+"/val.csv"
    vr = open(val_csv_path,'w')
    vr.writelines(valcsv)
    vr.close()
    # create coco json
    val_images_count, val_anno_count = cocos.csv2cocojson(val_csv_path, image_path_lidc, image_path_lndb)
    os.system('python '+ coco_tfrecord +' --logtostderr \
              --image_dir='+ image_all +' \
              --object_annotations_file='+ val_csv_path.replace('.csv','.json') +' \
              --output_file_prefix='+ tfrecord_out_path+'/'+fold+'/val/a' +' \
              --num_shards=32')
        
    if 'fold1' in fold:
        train_script = open(tfrecord_out_path+'/train_script.sh','w')
    else:
        train_script = open(tfrecord_out_path+'/train_script.sh','a')
        
    train_script.write('CUDA_VISIBLE_DEVICES="0" python '+efficientdet_main+' --mode=\'train_and_eval\' \
    --training_file_pattern='+tfrecord_out_path+'/'+fold+'/train/*.tfrecord \
    --validation_file_pattern='+tfrecord_out_path+'/'+fold+'/val/*.tfrecord \
    --model_name='+model_name+' --backbone_ckpt='+ckpt_path+' \
    --model_dir='+train_model_dir.replace('foldx',fold)+' \
    --num_examples_per_epoch='+str(train_images_count)+' \
    --eval_samples='+str(val_images_count)+' \
    --num_epochs=8 \
    --train_batch_size=3 --hparams="num_classes=1"\n')
    

for i in range (0,fold_num):
    run_fold(i+1)
    #save validation pice on every fold
    copy_validation.copy_infer(i+1,image_path_lidc,image_path_lndb,image_path_infer,output_path)
    












