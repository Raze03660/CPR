import cv2
import os

# 一帧一帧的分割 需要几帧写几
c = 0
videoCount = 0
index = 1

# 先讀取資料夾內的檔案
filepath = "/home/ezio/openpose/work_space/label"
pathDir = os.listdir(filepath)
for allDir in pathDir:
    videopath = filepath + '/' + allDir
    vc = cv2.VideoCapture(videopath)
    # 分離名稱e.g.: IMG_2326.MOV => IMG_2326
    fileName = allDir.split(".")

    if vc.isOpened():
        rval, frame = vc.read()
        print("success")
    else:
        rval = False
        print("failed")
    while rval:
        cv2.imshow('video', frame)
        key = cv2.waitKey(10)
        if c % 1 == 0:
            cv2.imwrite("save_cpr_label/" + fileName[0] + "_" + str(index) + '.jpg', frame)
            index += 1
        c += 1
        rval, frame = vc.read()
