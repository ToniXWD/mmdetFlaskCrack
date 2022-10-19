# -*- coding:utf-8 -*-
# @Time : 2021/10/25 9:22
# @Author : JulyLi
# @File : CV2image.py
# @Software: PyCharm

import cv2
import numpy as np
import base64

def bytes2cv(im):
    '''二进制图片转cv2

    :param im: 二进制图片数据，bytes
    :return: cv2图像，numpy.ndarray
    '''
    return cv2.imdecode(np.array(bytearray(im), dtype='uint8'), cv2.IMREAD_UNCHANGED)  # 从二进制图片数据中读取


def cv2bytes(im):
    '''cv2转二进制图片

    :param im: cv2图像，numpy.ndarray
    :return: 二进制图片数据，bytes
    '''
    return np.array(cv2.imencode('.png', im)[1]).tobytes()


def image_to_base64(image_np):
    """
    将np图片(imread后的图片）转码为base64格式
    image_np: cv2图像，numpy.ndarray
    Returns: base64编码后数据
    """
    image = cv2.imencode('.png', image_np)[1]
    image_code = str(base64.b64encode(image))[2:-1]
    return image_code


def base64_to_image(base64_code):
    """
    将base64编码解析成opencv可用图片
    base64_code: base64编码后数据
    Returns: cv2图像，numpy.ndarray
    """
    # base64解码
    img_data = base64.b64decode(base64_code)
    # 转换为np数组
    img_array = np.fromstring(img_data, np.uint8)
    # 转换成opencv可用格式
    img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)

    return img


if __name__ == '__main__':

    filename = 'horse.jpg'
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    image_code = image_to_base64(img)
    print(image_code)

    img = base64_to_image(image_code)
    cv2.imshow('bytes2cv', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
