from flask import Flask, request, jsonify
from flask_cors import CORS  # 引入 CORS
import base64
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier

from package.database import HandSignDecetion

import math
import re
import sqlite3

app = Flask(__name__)
CORS(app)  # 在應用程式上啟用 CORS(處理跨域問題)=>跨域資源共享

detector = HandDetector(maxHands=3) #maxHands最多可檢測手的數量，只偵測第一隻檢測到的手，其餘忽略
classfier = Classifier("Model/keras_model.h5", "Model/labels.txt")
filename = "MODEL\labels.txt"
offset = 20
imgSize = 300
temp = ""

labels = []
# 之後讀取資料庫類別取代此串列
with open(filename, 'r') as f:
    text = f.read()
    text = re.findall(r"(?:\s*)(\b[a-zA-Z' ]+\b)\s*", text)
labels = text

database = HandSignDecetion('Hand.db') # 連結資料庫

@app.route('/camera', methods=['POST'])
def receive_image():
    global temp
    try:
        # 從請求的 JSON 數據中獲取圖片數據URL
        data = request.get_json()
        image_data_url = data.get('image', '') #從POST請求的JSON數據中提取'image'的鍵對應的值
        # print(data)

        # 將Base64編碼的圖片數據解碼為OpenCV格式
        _, img_encoded = image_data_url.split(",", 1)
        img_decoded = base64.b64decode(img_encoded.encode('utf-8'))
        nparr = np.frombuffer(img_decoded, np.uint8)
        if img_decoded:
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            # 返回相應的錯誤消息
            error_message = '影像解碼失敗'
            return jsonify(error=error_message)

        hands, _ = detector.findHands(img)
        if len(hands) > 2:
            # 檢測到多於兩隻手，返回錯誤訊息
            error_message = '多於可偵測數量'
            return jsonify(error=error_message)
        
        if hands:
            # Hand 1
            hand1 = hands[0]
            lmList1 = hand1['lmList'] # List of 21 Landmark points
            x, y, w, h = hand1['bbox'] # Bouding box info x, y, w, h
            fingers1 = detector.fingersUp(hand1) # 檢測每根手指是否展開

            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
            imgCrop = img[y - offset : y + h + offset, x - offset : x + w + offset]

            if imgCrop is not None and imgCrop.shape[0] > 0 and imgCrop.shape[1] > 0:
                aspectRatio = h / w
                if aspectRatio > 1:
                    k = imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                    wGap = math.ceil((imgSize - wCal) / 2)
                    imgWhite[:, wGap : wCal + wGap] = imgResize
                    prediction, index = classfier.getPrediction(imgWhite, draw=False)
                    if index is None:
                        index = '無對應類別'
                        prediction = '無對應預測值'
                        print(prediction, index)
                    else:
                        print(prediction, index)
                else:
                    k = imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                    hGap = math.ceil((imgSize - hCal) / 2)
                    imgWhite[hGap : hCal + hGap, :] = imgResize
                    prediction, index = classfier.getPrediction(imgWhite, draw=False)
                    if index is None:
                        index = '無對應類別'
                        prediction = '無對應預測值'
                        print(prediction, index)
                    else:
                        print(prediction, index)
            
            if len(hands)==2:
                # Hand 2
                hand2 = hands[1]
                lmList2 = hand2['lmList']
                x2, y2, w2, h2 = hand2['bbox']
                fingers2 = detector.fingersUp(hand2)

                # length, info, img = detector.findDistance() # 計算兩關鍵點間的距離，可以是同隻或是不同隻手

                imgWhite2 = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                imgCrop2 = img[y2-offset:y2+h2+offset, x2-offset:x2+w2+offset]

                # 處理手部圖片的尺寸和比例
                imgCropShape2 = imgCrop2.shape
                if imgCrop2 is not None and imgCrop2.shape[0] > 0 and imgCrop2.shape[1] > 0:
                    aspectRatio = h2/w2
                    if aspectRatio > 1:
                        k2 = imgSize/h2
                        wCal2 = math.ceil(k2*w2)
                        imgResize2 = cv2.resize(imgCrop2, (wCal2, imgSize))
                        imgResizeShape2 = imgResize2.shape
                        wGap2 = math.ceil((imgSize-wCal2)/2)
                        imgWhite2[:, wGap2:wCal2+wGap2] = imgResize2
                    else:
                        k2 = imgSize/w2
                        hCal2 = math.ceil(k2*h2)
                        imgResize2 = cv2.resize(imgCrop2, (imgSize, hCal2))
                        imgResizeShape2 = imgResize2.shape
                        hGap2 = math.ceil((imgSize-hCal2)/2)
                        imgWhite2[hGap2:hCal2+hGap2, :] = imgResize2
                    
                    # 串接左右手各自擷取區域的陣列(以y軸左右連接)
                    imgWhite = np.concatenate((imgWhite, imgWhite2), axis=1)
                    prediction, index = classfier.getPrediction(imgWhite, draw=False)
                    confidence_score = prediction[0][index]
                    if index is None:
                        index = '無對應類別'
                        prediction = '無對應預測值'
                        print(prediction, index, confidence_score)
                    else:
                        print(prediction, index, confidence_score)

            result = {'prediction': labels[index], 'transfer': ''}
            success = database.select_sign_from_keyword(
                keyword=result['prediction'])
            if (temp!=''.join(success)): #temp與success比較若是不相同則儲存結果(目的:因為辨識結果可能在一段時間會重複出現同樣的值所以會對拼成短句造成干擾，故以temp將單字儲存成短句再到資料庫搜尋翻譯結果)
                temp+= ''.join(success)
                # print(temp)
                transfer = database.select_sign_from_keyword(
                    keyword=temp)
                result['transfer'] = transfer
                # print(transfer)
            result['prediction'] = temp
            
            print(result)

            temp = ''.join(success) #更新temp的值 

            return jsonify(result) # 將 Python 對象轉換為 JSON 格式將辨識結果回傳前端
        else:
            # 如果未找到手，返回相應的錯誤消息
            index = '無對應類別'
            prediction = '無對應預測值'
            print(prediction, index)
            error_message = '未檢測到手'
            return jsonify(error=error_message)
        
    except Exception as e:
        index = '無對應類別'
        prediction = '無對應預測值'
        print(prediction, index)
        return jsonify(error=str(e))
@app.errorhandler(Exception)
def handle_error(e):
    response = jsonify(error=str(e))
    response.status_code = 500  # 內部伺服器錯誤
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
