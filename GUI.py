import sys
import cv2 as cv
import onnx
import onnxruntime as ort
import numpy as np
import random
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from PyQt5.QtWidgets import QFileDialog, QMainWindow
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication
from Crack_Detection import Ui_MainWindow

device = ort.get_device()
model = onnx.load('weights/yolact_epoch_37.onnx')
if device == 'CPU':
    providers = ['CPUExecutionProvider']
elif device == 'GPU':
    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']  # 'TensorrtExecutionProvider'?
onnx.checker.check_model(model)
session = ort.InferenceSession('weights/yolact_epoch_37.onnx', providers=providers)

def test_pic(img_path,session, score_thresh = 0.3):
    # model = onnx.load('temp_dy.onnx')
    img = cv.imread(img_path)
    # img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    if img.shape !=(550,550,3):
        img = cv.resize(img,(550,550))
    # if img.shape[0] > 1080:
    #     ratio = int(img.shape[0]/1080)
    #     img = cv.resize(img, (img.shape[1]//ratio, img.shape[0]//ratio))
    img_ori = img.copy()
    img = img.astype(np.float32)
    img = img.transpose(2,0,1)

    device = ort.get_device()

    # session = ort.InferenceSession('temp_dy.onnx',providers=['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider'])
    start = time.time()
    outputs = session.run([],{'input': [img]})
    print(outputs[0].shape)
    print(outputs[1].shape)
    print(outputs[2].shape)
    end = time.time()
    print("Use {}".format(device))
    Bbox = outputs[0][:,:4].astype(int)
    Score = outputs[0][:,4].astype(np.float16)
    print(outputs[2].shape)
    Mask = outputs[2][:,0,:,:]
    remain = Score>score_thresh
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
        print(mask.shape)
        print(img_ori.shape)
        img_ori[mask] = img_ori[mask] * 0.5 + color_mask * 0.5
        cv.rectangle(img_ori, (box[0],box[1]),(box[2],box[3]),color,thickness=2,lineType=4)
        # cv2.rectangle(img_ori, (box[0],box[1]),(box[2],box[3]),(184, 125, 234),thickness=2,lineType=4)
        cv.putText(img_ori, 'Crack{}|{}'.format(str(id),str(Score[id])), (box[0],box[1]-5),
                   cv.FONT_HERSHEY_TRIPLEX, 1.0, color, 2)
    cv.imwrite('out.jpg',img_ori)
    return Score,Bbox,Mask


class PyQtMainEntry(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Crack Detection")

        self.labelinput.setAlignment(Qt.AlignCenter)
        self.labelinput.setStyleSheet("QLabel{background:gray;}"
                                      "QLabel{color:rgba(255,255,255,150);"
                                      "font-size:15px;"
                                      "font-weight:bold;"
                                      "font-family:Roman times;}")

        self.labelresult.setAlignment(Qt.AlignCenter)
        self.labelresult.setStyleSheet("QLabel{background:gray;}"
                                       "QLabel{color:rgba(255,255,255,150);"
                                       "font-size:15px;"
                                       "font-weight:bold;"
                                       "font-family:Roman times;}")

    # def btnTest_Pressed(self):
    def slot3(self):
        if not hasattr(self, "captured"):
            # print("没有输入图像")
            # self.textBrowser.setPlainText("没有输入图像")
            return
        self.textBrowser.append("图像检测中...")



    # def btnInput_Clicked(self):
    def slot1(self):
        '''
        从本地读取图片
        '''
        global fname
        # 打开文件选取对话框
        filename, _ = QFileDialog.getOpenFileName(self, '打开图片', "", "*.jpg;;*.png;;*.jpeg;;All Files(*)")
        if filename:
            self.captured = cv.imread(str(filename))
            # OpenCV图像以BGR通道存储，显示时需要从BGR转到RGB
            self.captured = cv.cvtColor(self.captured, cv.COLOR_BGR2RGB)

            rows, cols, channels = self.captured.shape
            bytesPerLine = channels * cols
            QImg = QImage(self.captured.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
            self.labelinput.setPixmap(QPixmap.fromImage(QImg).scaled(
                self.labelinput.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        fname = filename
        print(fname)
        self.textBrowser.setPlainText("成功打开图片")

    # def btnTest_Clicked(self):
    def slot2(self):
        '''
        test
        '''
        global fname
        # 如果没有捕获图片，则不执行操作
        if not hasattr(self, "captured"):
            print("请输入图片")
            self.textBrowser.setPlainText("请输入图片")
            return
        print("start")
        print(fname.split("/")[-1])
        # -*- coding: utf-8 -*-
        import os
        import sys
        import matplotlib
        matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
        matplotlib.rcParams['font.serif'] = ['KaiTi']

        # Root directory of the project
        ROOT_DIR = os.getcwd()

        # Import Mask RCNN
        sys.path.append(ROOT_DIR)  # To find local version of the library

        score,bbox,mask = test_pic(fname,session)
        area=0
        length=0
        num = score.shape[0]
        if num==0:
            self.textBrowser.append('未检测到裂缝')
        for i in range(len(score)):
            crack_id = 'crack'+'i:'
            area = mask[i].sum()
            mask_i = mask[i].astype(np.uint8)
            contours, hierachy = cv.findContours(mask_i, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
            length=0
            for crack_chips in contours:
                if len(crack_chips) < 8:
                    continue
                length += cv.arcLength(crack_chips, True) / 2
            self.textBrowser.append('裂缝序号：{}'.format(str(i)))
            self.textBrowser.append('概率：{}'.format(str(score[i])))
            self.textBrowser.append('检测到裂缝数量：{}'.format(str(num)))
            self.textBrowser.append('面积：{}'.format(str(area)))
            self.textBrowser.append('长度：{}'.format(str(length)))
            self.textBrowser.append('宽度：{}'.format(str(area/length)))
            self.textBrowser.append(' ')


        self.captured = cv.imread(r"out.jpg")
        # OpenCV图像以BGR通道存储，显示时需要从BGR转到RGB
        self.captured = cv.cvtColor(self.captured, cv.COLOR_BGR2RGB)

        rows, cols, channels = self.captured.shape
        bytesPerLine = channels * cols
        QImg = QImage(self.captured.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
        self.labelresult.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.labelresult.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.textBrowser.append("检测完成")



    # def btnSave_Clicked(self):
    def slot4(self):
        '''
        保存
        '''
        global fname
        if not hasattr(self, "captured"):
            print("没有输入图像")
            self.textBrowser.setPlainText("没有输入图像")
            return
        tmp = fname.split('/')[-1]
        img = cv.imread("out.jpg")
        fd, type = QFileDialog.getSaveFileName(self,
                                               "保存图片", tmp)
        print(fd)
        cv.imwrite(fd, img)
        # self.textBrowser.setPlainText("保存成功")
        self.textBrowser.append("保存成功")  # textedit是文本框的名称

        print("保存成功")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PyQtMainEntry()
    window.show()
    sys.exit(app.exec_())

