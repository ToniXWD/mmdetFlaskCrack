import cv2
import numpy as np
import os
import json

def cv_show(title,img):
    cv2.imshow(title,img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_mask(npy_dir = 'static', pic = 'data/temp.jpg'):
    data_dict = {}
    # mask_npy_path = 'test/tiny_b2_epoch95/b2_c1_4_2_1_1_2_mask.npy'
    # bbox_npy_path = 'test/tiny_b2_epoch95/b2_c1_4_2_1_1_2_bbox.npy'
    # img_path = 'data/coco/test_2017/b2_c1_4_2_1_1_2.jpg'

    mask_npy_name = pic.split('/')[-1].split('.')[0] + '_mask.npy'
    bbox_npy_name = pic.split('/')[-1].split('.')[0] + '_bbox.npy'

    mask_npy_path = os.path.join(npy_dir, mask_npy_name)
    bbox_npy_path = os.path.join(npy_dir, bbox_npy_name)
    img_path = pic

    try:
        mask_npy = np.load(mask_npy_path)
        mask_npy = mask_npy.astype(np.uint8)*255
        bbox_npy = np.load(bbox_npy_path)[:,:-1].astype(int)
        img = cv2.imread(img_path, 0)
    except:
        return 'Nothing Detected!'

    # print(img.shape)
    # img = np.where(img<60, 255, 0).astype(np.uint8)
    # cv_show('img',img)
    for i, (mask_instance, bbox_instance) in enumerate(zip(mask_npy, bbox_npy)):

        data_dict[str(i)] = {}

        x1,y1,x2,y2 = bbox_instance
        img_new = np.zeros_like(img)

        # 获得原面积和修正后的mask面积
        img_new[y1:y2+1,x1:x2+1] = 255 - img[y1:y2+1,x1:x2+1]
        max_img_new = np.max(255 - img[y1:y2 + 1, x1:x2 + 1])
        thresh = np.average(255 - img[y1:y2+1,x1:x2+1])
        thresh_big = thresh + (max_img_new - thresh) / 3
        thresh_small = thresh / 2
        area = mask_instance.sum() / 255
        # cv_show('img_new', img_new)
        # cv_show('example', mask_instance)
        # print(mask_example.shape)
        # 第一种方法，权值相加
        # mask_fuse = 0.5*img_new+0.5*mask_example
        # mask_fuse = np.where(mask_fuse>200, 255, 0).astype(np.uint8)
        # cv_show('mask_fuse', mask_fuse)

        # 第二种方法，原图有裂缝的地方置为裂缝
        length = 0
        contours, hierachy = cv2.findContours(mask_instance, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for crack_chips in contours:
            if len(crack_chips) < 8:
                continue
            length += cv2.arcLength(crack_chips, True)/2
        width = area / length
        if width > 8:
            img_new = np.where(img_new < thresh_big, 0.5, 255)
        elif width > 6:
            img_new = np.where(img_new < thresh, 0.5, 255)
        elif width > 4:
            img_new = np.where(img_new < thresh_small, 0.5, 255)
        else:
            img_new = np.where(img_new < 1, 0.5, 255)
        mask_fuse = np.where(img_new == mask_instance, mask_instance, 0)

        area_fuse = mask_fuse.sum() / 255

        # data_dict[str(i)]['original_area'] = round(area,2)
        # data_dict[str(i)]['fixed_area'] = round(area_fuse,2)
        # data_dict[str(i)]['length'] = round(length,2)
        # data_dict[str(i)]['width'] = round(width,2)
        data_dict[str(i)]['原始面积'] = round(area, 2)
        data_dict[str(i)]['修正面积'] = round(area_fuse, 2)
        data_dict[str(i)]['长度'] = round(length, 2)
        data_dict[str(i)]['宽度'] = round(width, 2)
    print('Complet {}'.format(pic))
    with open(os.path.join(npy_dir, pic.split('/')[-1].split('.')[0]+'_mask_data.json'), 'w') as fp:
        json.dump(data_dict, fp, indent=4)
    return data_dict




