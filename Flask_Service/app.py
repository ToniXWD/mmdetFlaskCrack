import sys
sys.path.append('..')
import os
import zipfile
import time
import cv2
import torch
from flask import Flask, render_template, request, jsonify, session,g
from mmdet.apis import init_detector
from test_pic_web import eval
from gevent import pywsgi
from get_mask_data_web import get_mask
from get_mask_data_zip import get_mask_zip
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import config
from blueprints.user import mail
from exts import db
from blueprints import qa_bp, user_bp
from blueprints.user import user_dict
from tools import pictype


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
mail.init_app(app)

app.register_blueprint(qa_bp)
app.register_blueprint(user_bp)

score_thresh = 0.5
nms_thresh = 0.5
small_remove = False

@app.before_request
def before_request():
    user_emial = session.get("email")
    if user_emial is not None:
        try:
            g.user = user_dict[user_emial]["username"]
        except:
            g.user = None

@app.context_processor # 所有的模板都会执行以下代码
def context_processor():
    if hasattr(g,"user"):
        context = {"user":g.user}
        return context
    else:
        return {}

def load_checkpoint(cfg,check,dev):
    model = init_detector(cfg, check, device=dev)
    print("Loading the model from {} successfully！".format(check.split('/')[-1]))
    print("Type: {}".format(cfg.split('/')[-1].split('.')[0]))
    return model

config = {
    'm2fSwinT':'../configs/mask2former/mask2former_swin-t-p4-w7-224_lsj_8x2_50e_coco.py',
    'm2fSwinS':'../configs/mask2former/mask2former_swin-s-p4-w7-224_lsj_8x2_50e_coco.py',
    'm2fR101':'../configs/mask2former/mask2former_r101_lsj_8x2_50e_coco.py',
    'm2fR50':'../configs/mask2former/mask2former_r50_lsj_8x2_50e_coco.py',
    'yolactR101':'../configs/yolact/yolact_r101_1x8_coco.py',
    'msR101':'../configs/ms_rcnn/ms_rcnn_r101_caffe_fpn_2x_coco.py',}
checkpoint = {
    'm2fSwinT':'../work_dirs/mask2former_t_885/iter_11800.pth',
    'm2fSwinS':'../work_dirs/mask2former_s_845/iter_15500_488_264.pth',
    'm2fR101':'../work_dirs/mask2former_res101_845/iter_10998_523_289.pth',
    'm2fR50':'../work_dirs/mask2former_res50_845/iter_12126_512_280.pth',
    'yolactR101':'../work_dirs/yolact_845/epoch_34.pth',
    'msR101':'../work_dirs/ms_845/epoch_30.pth',}
device = 'cuda:0'
cur_config = config['m2fSwinT']
cur_checkpoint = checkpoint['m2fSwinT']
model = load_checkpoint(cur_config,cur_checkpoint, device)


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
    if img.shape[0] > 1024:
        print("重置大小")
        ratio = img.shape[0]//1024
        img = cv2.resize(img, (img.shape[1] // ratio, img.shape[0] // ratio))
    cv2.imwrite(os.path.join('data/pic_temp',os.path.basename(image_pth)), img)
    # cv2.imwrite('data/pic_temp/temp.jpg', img)


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


@app.before_request
def before_request():
    user_email = session.get("email")
    if user_email is not None:
        try:
            setattr(g,"user",user_dict[user_email]["username"])
        except:
            setattr(g, "user", None)

@app.context_processor
def context_processor():
    if hasattr(g,"user"):
        return {"user":g.user}
    else:
        return {}

@app.route("/")
def index_page():
    return render_template('index.html')

@app.route("/upload_image", methods=['POST'])
def return_result():
    startTime = time.time()
    image = request.files.get('image')  # FileStorage
    # 图片保存至指定路径
    # received_file = request.files['input_image']
    # imageFileName = received_file.filename
    imageFileName = image.filename
    if imageFileName.split('.')[-1] in ['jpg','png','jpeg','JPG']:
        received_dirPath = './resources/received_images'
        if not os.path.isdir(received_dirPath):
            os.makedirs(received_dirPath)
        imageFilePath = os.path.join(received_dirPath, imageFileName)
        image.save(imageFilePath)
        used_time = time.time()-startTime
        print('保存图片所花时间%0.2f秒'%used_time)
        img_resize(imageFilePath)
        startTime = time.time()
        out_pic = eval(score_thr=score_thresh, model=model, nms_thr=nms_thresh, remove_small=small_remove, name=imageFileName)
        crack_inf = get_mask('static',imageFilePath)
        used_time = time.time()-startTime
        print('模型预测消耗时间%0.2f秒'%used_time)

        for_send = cv2.imread(out_pic)
        for_send_base64 = pictype.image_to_base64(for_send)

        # pic_send_name = os.path.join('for_send', imageFileName.split('.')[0]) + '.png'
        # cv2.imwrite(pic_send_name, for_send)
        # json_send_name = os.path.join('for_send', imageFileName.split('.')[0]) + '.json'
        # for_send_json = os.path.join('./static', imageFileName.split('.')[0])+'_mask_data.json'
        # print(for_send_json)

        output = {}
        output["img_result"] = for_send_base64
        output["crack_data"] = crack_inf
        # return send_file(pic_send_name, mimetype='image/gif'), jsonify(crack_inf)
        torch.cuda.empty_cache()
        return jsonify(output)
    else:
        torch.cuda.empty_cache()
        print('failed')
        return "请输入以下格式的图片：jpg','png','jpeg','JPG'"

@app.route("/upload_image_web", methods=['POST'])
def return_result_web():
    startTime = time.time()
    received_file = request.files['input_image']
    modelType = request.form.get("modelType")
    print(modelType)
    temp_config = config[modelType]
    temp_checkpoint = checkpoint[modelType]
    global cur_config
    global cur_checkpoint
    global model
    global score_thresh
    temp_thresh = request.form.get('thresh')
    if temp_thresh != '':
        try:
            score_thresh = float(temp_thresh)
        except:
            print("输入的阈值不是0~1的小数，将采用系统默认值")
    if cur_config!=temp_config:
        print("更改模型...")
        model = load_checkpoint(temp_config,temp_checkpoint,device)
        cur_checkpoint = temp_checkpoint
        cur_config = temp_config
    imageFileName = received_file.filename
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
        seg_out = eval(img_dir = unzip_path, score_thr=score_thresh, model=model,
                       nms_thr=nms_thresh, remove_small=small_remove)
        get_mask_zip(seg_out, unzip_path)

        # email = request.values['acceptemail']
        # print(email)
        # if email is None:
        #     message = Message(subject="裂缝分割结果",
        #                   recipients=["807077266@qq.com"],
        #                   body="请查收附件",
        #                   )
        # else:
        #     message = Message(subject="裂缝分割结果",
        #                       recipients=[email],
        #                       body="请查收附件",
        #                       )
        filelist = os.listdir(seg_out)
        for f in filelist:
            filepath = os.path.join(seg_out, f)
            if f.endswith('npy'):
                os.remove(filepath)
        getZipDir(seg_out, 'crack_result.zip')
        # with app.open_resource("crack_result.zip") as fp:
        #     # attach("文件名", "类型", 读取文件）
        #     message.attach("crack_result.zip", 'application/octet-stream', fp.read())
        # mail.send(message)
        # return render_template("after_email.html")
        torch.cuda.empty_cache()
        return render_template("zip.html",link="请点击此处下载检测结果")
        # return send_file('crack_result.zip', as_attachment=True)
    elif imageFileName.split('.')[-1] in ['jpg','png','jpeg','JPG']:
        print(imageFileName)
        # save_name = 'temp.' + imageFileName.split('.')[-1]
        if received_file:
            received_dirPath = './resources/received_images'
            if not os.path.isdir(received_dirPath):
                os.makedirs(received_dirPath)
            imageFilePath = os.path.join(received_dirPath, imageFileName)
            received_file.save(imageFilePath)
            used_time = time.time()-startTime
            print('保存图片所花时间%0.2f秒'%used_time)
            img_resize(imageFilePath)
            startTime = time.time()
            out_pic = eval(score_thr=score_thresh, model=model, nms_thr=nms_thresh, remove_small=small_remove, name=imageFileName)
            crack_inf = get_mask('static',imageFilePath)
            used_time = time.time()-startTime
            print('模型预测消耗时间%0.2f秒'%used_time)

            torch.cuda.empty_cache()
            crack_html = [[num]+(list(i.values())) for num,i in enumerate(crack_inf.values())]
            return render_template("result.html", result=crack_html, img=out_pic)

        else:
            torch.cuda.empty_cache()
            return 'failed'

if __name__ =="__main__":
    # imageFilePath = os.path.join(BASE_DIR, 'data/pic_temp/temp.jpg')
    # app.run("10.201.193.75", port=5000)
    # server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server = pywsgi.WSGIServer(('10.203.186.251', 5000), app)
    server.serve_forever()
