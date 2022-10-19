import time
from argparse import ArgumentParser
import cv2
import os
from mmdet.apis import inference_detector

def show_result_pyplot(model,
                       img,
                       result,
                       score_thr=0.3,
                       title='result',
                       wait_time=0,
                       out_dir = None,
                       remove=False,
                       self_nms = False):
    """Visualize the detection results on the image.

    Args:
        model (nn.Module): The loaded detector.
        img (str or np.ndarray): Image filename or loaded image.
        result (tuple[list] or list): The detection result, can be either
            (bbox, segm) or just bbox.
        score_thr (float): The threshold to visualize the bboxes and masks.
        title (str): Title of the pyplot figure.
        wait_time (float): Value of waitKey param.
                Default: 0.
    """
    if hasattr(model, 'module'):
        model = model.module
    out = model.show_result(
        img,
        result,
        score_thr=score_thr,
        show=False,
        wait_time=wait_time,
        win_name=title,
        bbox_color=(72, 101, 241),
        text_color=(72, 101, 241),
        out_dir = out_dir,
        remove = remove,
        self_nms = self_nms,
    )
    return out

def eval(img_dir = 'data/pic_temp',
         out_dir = 'static',
         # config='../configs/swin/mask_rcnn_swin_small_patch4_window7_mstrain_480-800_adamw_3x_coco.py',
         model=None,
         score_thr = 0.25,
         remove_small=True,
         nms_thr = False,
         name=None):
    if img_dir != 'data/pic_temp':
        num = 0
        print("进行zip压缩文件的检测...")
        out_dir = 'static/'+img_dir.split('/')[-1]
        os.makedirs(out_dir)
        print("模型检测输出文件夹为:"+out_dir)
        # test a single image
        start_zip_time = time.time()
        for img_dir2 in os.listdir(img_dir):
            print(img_dir2)
            for img in os.listdir(os.path.join(img_dir,img_dir2)):
                if img.split('.')[-1] not in ("png", "jpg", "JPG", "jpeg"):
                    continue
                num+=1
                img_path = os.path.join(img_dir,img_dir2, img)
                print(img_path)
                result = inference_detector(model, img_path)
                # show the results
                out = show_result_pyplot(model, img_path, result, score_thr=score_thr,
                                         remove=remove_small, out_dir=out_dir, self_nms=nms_thr)
                save_name = os.path.join(out_dir, img.split('.')[0] + '.png')
                print("完成对文件"+save_name+"的检测和储存")
                cv2.imwrite(save_name, out)
        end_zip_time = time.time()
        print("模型检测图片耗时共{}秒".format(round(end_zip_time-start_zip_time,2)))
        print("检测帧数为:{}".format(round(num/(end_zip_time-start_zip_time),2)))
        return out_dir
    else:
        try:
            os.remove('static/'+name.split('.')[0]+'_mask.npy')
            os.remove('static/'+name.split('.')[0]+'_bbox.npy')
        except:
            print('没有遗留的同名npy文件')
        # build the model from a config file and a checkpoint file
        # test a single image
        img_path = os.path.join(img_dir, name)
        result = inference_detector(model, img_path)
        # show the results
        out = show_result_pyplot(model, img_path, result, score_thr=score_thr,
                                 remove=remove_small, out_dir = out_dir, self_nms=nms_thr)
        save_name = os.path.join(out_dir, name.split('.')[0]+'.png')
        cv2.imwrite(save_name,out)
        return save_name

if __name__ == '__main__':
    eval()
