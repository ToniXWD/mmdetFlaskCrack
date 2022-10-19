# 0.引入库
import time
import os
import torch
import torchvision.transforms as transforms
import cv2
from PIL import Image
from flask import Flask, render_template, request, jsonify
from yolact import Yolact
from eval_for_web import eval
import io


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1.加载模型
# path_model = '../weights/624_1c/yolact_coco_custom_506_40000.pth'
# model = Yolact()
# model.load_weights(path_model)
# model.eval()

# 2.预处理
def img_resize(image_pth):
    img = cv2.imread(image_pth)
    if img.shape[0] > 1000:
        ratio = img.shape[0]//1000
        img = cv2.resize(img, (img.shape[1] // ratio, img.shape[0] // ratio))
    cv2.imwrite('/home/oem/yolact-master/Flask_Service/data/pic_temp/temp.jpg', img)

# 3.模型预测
 # eval()

# 4.服务返回
@app.route("/")
def index_page():
    return render_template('index_old.html')

@app.route("/upload_image", methods=['POST'])
def return_result():
    # 1.获取并保存上传的图片，并计算所用时间
    startTime = time.time()
    received_file = request.files['input_image']
    imageFileName = received_file.filename
    if received_file:
        received_dirPath = './resources/received_images'
        if not os.path.isdir(received_dirPath):
            os.makedirs(received_dirPath)
        imageFilePath = os.path.join(received_dirPath, imageFileName)
        received_file.save(imageFilePath)
        used_time = time.time()-startTime
        print('保存图片所花时间%0.2f秒'%used_time)
        img_resize(imageFilePath)
    # 2.对图片进行预测并返回结果
        startTime = time.time()
        eval()
        used_time = time.time()-startTime
        print('模型预测消耗时间%0.2f秒'%used_time)
        # img = Image.open(io.BytesIO('/home/oem/yolact-master/Flask_Service/data/pic_temp/temp_out.jpg'))
        # # img = str(img)
        # return render_template("result_old.html", result=img)
    else:
        return 'failed'

# 5.主函数
if __name__ =="__main__":
    # imageFilePath = os.path.join(BASE_DIR, 'data/pic_temp/temp.jpg')
    app.run("127.0.0.1", port=5000)