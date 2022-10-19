# 0.引入库
import requests
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1.主函数
if __name__ == "__main__":
    # 定义请求服务的url
    url = "Http://127.0.0.1:5000"
# 2.确定上传图片
    while True:
        input_content = input("输入图片路径：")
        imageFilePath = input_content.strip()
        imageFileName = os.path.split(imageFilePath)[1]
        file_dict = {
            'file':(imageFileName, open(imageFilePath, 'rb'), 'image/jpg')
        }
    # 3.接受返回结果
        result = requests.post(url, files=file_dict)
        print(result.text)