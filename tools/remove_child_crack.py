import numpy as np

def area(index):
    return (index[2]-index[0])*(index[3]-index[1])

def remove(bboxs, remove_thresh=0.3):
    bboxs = bboxs[:,:4]
    remove_mask = np.ones(bboxs.shape[0])
    remve_id = []
    for i in range(bboxs.shape[0]):
        if i in remve_id:
            continue
        for j in range(i+1, bboxs.shape[0]):
            if j in remve_id:
                continue
            if bboxs[i][0]>bboxs[j][0] and bboxs[i][1]>bboxs[j][1]\
                and bboxs[i][2]<bboxs[j][2] and bboxs[i][3]<bboxs[j][3]:
                area_i = (bboxs[i][2]-bboxs[i][0])*(bboxs[i][3]-bboxs[i][1])
                area_j = (bboxs[j][2]-bboxs[j][0])*(bboxs[j][3]-bboxs[j][1])
                if area_i/area_j>=remove_thresh:
                    remove_mask[i]=0
                    remve_id.append(i)
            if bboxs[j][0]>bboxs[i][0] and bboxs[j][1]>bboxs[i][1]\
                and bboxs[j][2]<bboxs[i][2] and bboxs[j][3]<bboxs[i][3]:
                area_i = (bboxs[i][2]-bboxs[i][0])*(bboxs[i][3]-bboxs[i][1])
                area_j = (bboxs[j][2]-bboxs[j][0])*(bboxs[j][3]-bboxs[j][1])
                if area_j/area_i>=remove_thresh:
                    remove_mask[j]=0
                    remve_id.append(j)
    return remove_mask.astype(bool)

if __name__=='__main__':
    bboxs = np.array([[204,40,255,256],[191,2,210,54]])
    out = remove(bboxs)
    bboxs = bboxs[out]
    print(out)
    print(bboxs)