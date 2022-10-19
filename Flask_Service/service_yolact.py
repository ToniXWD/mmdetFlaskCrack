import os
import zipfile
import time
import cv2
import torch
from flask import Flask, render_template, request, jsonify, Blueprint
from flask_mail import Message

from test_pic_web import eval
from gevent import pywsgi
from get_mask_data_web import get_mask
from get_mask_data_zip import get_mask_zip
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import config
from exts import db, mail
from blueprints import qa_bp, user_bp

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
mail.init_app(app)

app.register_blueprint(qa_bp)
app.register_blueprint(user_bp)

def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not zip')

def img_resize(image_pth):
    img = cv2.imread(image_pth)
    print(img.shape)
    if img.shape[0] > 900:
        print("重置大小")
        ratio = img.shape[0]//900
        img = cv2.resize(img, (img.shape[1] // ratio, img.shape[0] // ratio))
    cv2.imwrite('/home/qlx/mmdetection/Flask_Service/data/pic_temp/temp.jpg', img)


def getZipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)  # outFullName为压缩文件的完整路径
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '')

        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


@app.route("/")
def index_page():
    return render_template('index.html')

@app.route("/upload_image", methods=['POST'])
def return_result():
    startTime = time.time()
    received_file = request.files['input_image']
    imageFileName = received_file.filename
    print(imageFileName)
    if imageFileName.endswith('.zip'):
        unzip_path = 'data/zip/'+ str(int(time.time()))
        if not os.path.isdir(unzip_path):
            os.makedirs(unzip_path)
        received_dirPath = './resources'
        if not os.path.isdir(received_dirPath):
            os.makedirs(received_dirPath)
        save_name = 'temp.zip'
        save_path = os.path.join(received_dirPath, save_name)
        received_file.save(save_path)
        unzip_file(save_path, unzip_path)
        seg_out = eval(img_dir = unzip_path, score_thr=0.25)
        get_mask_zip(seg_out, unzip_path)

        email = request.values['acceptemail']
        print(email)
        if email is None:
            message = Message(subject="裂缝分割结果",
                          recipients=["807077266@qq.com"],
                          body="请查收附件",
                          )
        else:
            message = Message(subject="裂缝分割结果",
                              recipients=[email],
                              body="请查收附件",
                              )
        filelist = os.listdir(seg_out)
        for f in filelist:
            filepath = os.path.join(seg_out, f)
            if f.endswith('npy'):
                os.remove(filepath)
        getZipDir(seg_out, 'crack_result.zip')
        with app.open_resource("crack_result.zip") as fp:
            # attach("文件名", "类型", 读取文件）
            message.attach("crack_result.zip", 'application/octet-stream', fp.read())
        mail.send(message)
        return render_template("after_email.html")
    elif imageFileName.split('.')[-1] in ['jpg','png','jpeg','JPG']:
        save_name = 'temp.' + imageFileName.split('.')[-1]
        if received_file:
            received_dirPath = './resources/received_images'
            if not os.path.isdir(received_dirPath):
                os.makedirs(received_dirPath)
            imageFilePath = os.path.join(received_dirPath, save_name)
            received_file.save(imageFilePath)
            used_time = time.time()-startTime
            print('保存图片所花时间%0.2f秒'%used_time)
            img_resize(imageFilePath)
            startTime = time.time()
            eval(score_thr=0.25)
            crack_inf = get_mask('static',imageFilePath)
            used_time = time.time()-startTime
            print('模型预测消耗时间%0.2f秒'%used_time)
            # a = open('/home/oem/yolact-master/Flask_Service/static/temp_out.txt', 'r')
            # a = a.readlines()

            # crack_inf = []
            # for i in a:
            #     crack_inf.append(i.split('\n')[0])
            torch.cuda.empty_cache()
            return render_template("result.html", result=crack_inf)
        else:
            torch.cuda.empty_cache()
            return 'failed'


if __name__ =="__main__":
    # imageFilePath = os.path.join(BASE_DIR, 'data/pic_temp/temp.jpg')
    # app.run("10.201.193.75", port=5000)
    server = pywsgi.WSGIServer(('10.203.210.222', 5000), app)
    server.serve_forever()