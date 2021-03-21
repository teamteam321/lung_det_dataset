
def main():
    gt = open('C:\\PROJECT_ALL\\SITE\\fold4\\val.csv','r')


    gt_list = []
    for r in gt:
        gt_list.append(r)

    print(len(gt_list))
    print(len(set(gt_list)))
    #print(len(dt_list))

    gt_img_name = []
    gt_bbox = []
    for r in gt_list:
        st = r.split(',')[0]
        st = st[st.rindex('/')+1:st.rindex('.')]
        gt_img_name.append(st)

        wr = open('C:\\PROJECT_ALL\\SITE\\mAP-master\\DEBUGLIST.txt','a')
        wr.write(st+'\n')

        st = r.split(',')[1:5]
        gt_bbox.append(list(map(int,st)))
        

    print(len(set(gt_img_name)))
    print(gt_img_name[1000])
    for i,x in enumerate(zip(gt_img_name,gt_bbox)):
        wr = open('C:\\PROJECT_ALL\\SITE\\mAP-master\\out_box\\'+x[0]+".txt",'a')
        wr.write('tumor '+str(x[1][0])+' '+str(x[1][1])+' '+str(x[1][2])+' '+str(x[1][3])+'\n')
    #for x in zip(gt_img_name,gt_bbox):
        #wr = open('C:\\PROJECT_ALL\\SITE\\mAP-master\\DEBUGLIST.txt','a')
        #wr.write('tumor '+str(x[1][0])+' '+str(x[1][1])+' '+str(x[1][2])+' '+str(x[1][3])+'\n')


if __name__ == "__main__":
    main()
