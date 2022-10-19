import onnx
import onnxruntime as ort
import cv2
import numpy as np
import time
import random

def cv_show(title,img):
    cv2.imshow(title,img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def test_pic(img_path):
    model = onnx.load('weights/mask2former_s.onnx')
    # model = onnx.load('swin_s_707_38.onnx')
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
    # if img.shape !=(550,550,3):
    #     img = cv2.resize(img,(550,550))
    img_ori = img.copy()
    img = img.transpose(2,0,1)

    device = ort.get_device()
    if device == 'CPU':
        providers = ['CPUExecutionProvider']
    elif device == 'GPU':
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']# 'TensorrtExecutionProvider'?
    onnx.checker.check_model(model)
    session = ort.InferenceSession('weights/mask2former_s.onnx',providers = providers)
    # session = ort.InferenceSession('weights/tmp.onnx',providers=['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider'])
    start = time.time()
    outputs = session.run([],{'input': [img]})
    end = time.time()
    for i in outputs:
        print(i.shape)
    print("Use {}".format(device))
    Bbox = outputs[0][:,:4]
    Score = outputs[0][:,4]
    print(outputs[2].shape)
    Mask = outputs[2][:,0,:,:]
    print(Mask.shape)
    remain = Score>0.5
    Bbox = Bbox[remain]
    Score = Score[remain]
    Mask = Mask[remain]
    print("耗时:{}".format(end-start))
    for id in range(len(Bbox)):
        box = Bbox[id].astype(int)
        mask = Mask[id]
        print(mask.shape)
        np.random.seed(id)
        color = tuple((random.randint(0,255),random.randint(1,255),random.randint(1,255)))
        color_mask = np.array(color).reshape((1,1,3))
        img_ori[mask] = img_ori[mask] * 0.5 + color_mask * 0.5
        cv2.rectangle(img_ori, (box[0],box[1]),(box[2],box[3]),color,thickness=2,lineType=4)
        # cv2.rectangle(img_ori, (box[0],box[1]),(box[2],box[3]),(184, 125, 234),thickness=2,lineType=4)
        cv2.putText(img_ori, 'Crack{}|{}'.format(str(id),str(Score[id])), (box[0],box[1]-5),
                   cv2.FONT_HERSHEY_TRIPLEX, 1.0, color, 2)
    cv2.imwrite('out.jpg',img_ori)
    return Score,Bbox,Mask

if __name__=='__main__':
    test_pic(img_path = 'data/coco/val2017/2_concrete_simple_12.jpg')