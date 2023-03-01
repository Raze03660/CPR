import argparse
import math
import sys
import pyopenpose as op
import cv2


def get_angle_point(human, pos):
    # 返回各个部位的关键点
    pnts = []

    if pos == 'left_elbow':
        pos_list = (5, 6, 7)
    elif pos == 'left_hand':
        pos_list = (1, 5, 7)
    elif pos == 'left_knee':
        pos_list = (12, 13, 14)
    elif pos == 'left_ankle':
        pos_list = (5, 12, 14)
    elif pos == 'right_elbow':
        pos_list = (2, 3, 4)
    elif pos == 'right_hand':
        pos_list = (1, 2, 4)
    elif pos == 'right_knee':
        pos_list = (9, 10, 11)
    elif pos == 'right_ankle':
        pos_list = (2, 9, 11)
    else:
        print('Unknown  [%s]', pos)
        return

    for i in range(3):
        if human[pos_list[i]][2] <= 0.1:
            print('component [%d] incomplete' % (pos_list[i]))
            return pnts
        pnts.append((int(human[pos_list[i]][0]), int(human[pos_list[i]][1])))
    return pnts


def angle_between_points(p0, p1, p2):
    # 计算角度
    a = (p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2
    b = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
    c = (p2[0] - p0[0]) ** 2 + (p2[1] - p0[1]) ** 2
    try:
        if a * b == 0:
            return -1.0
        else:
            angle = math.acos((a + b - c) / math.sqrt(4 * a * b)) * 180 / math.pi
    except:
        angle == -1
    return angle


def angle_left_elbow(human):
    pnts = get_angle_point(human, 'left_elbow')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        # print('left elbow angle:%f' % (angle))
    return angle


def angle_right_elbow(human):
    pnts = get_angle_point(human, 'right_elbow')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        # print('right elbow angle:%f' % (angle))
    return angle


if __name__ == '__main__':
    # 帶入config參數
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", default="images",
                        help="Process a directory of images. Read all standard formats (jpg, png, bmp, etc.).")
    parser.add_argument("--no_display", default=False, help="Enable to disable the visual display.")
    parser.add_argument('--truncate', type=float, default=0, help='Truncate last n seconds of video.')
    args = parser.parse_known_args()

    # 讀取影片訊息
    cap = cv2.VideoCapture("/home/ezio/openpose/work_space/label_video/IMG_2320.MOV")
    frame_cnt = 0

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "/home/ezio/openpose/models"

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()
    datum = op.Datum()
    try:
        if cap.isOpened():
            rval, frame = cap.read()
        else:
            rval = False
            print("can't open video")
        while rval:
            rval, frame = cap.read()
            if not rval:
                print('retrieve frame failed.')
                sys.exit(-1)
            # 6幀取一次
            if frame_cnt % 6 == 0:
                image = cv2.resize(frame, (960, 540))
                datum.cvInputData = image
                opWrapper.emplaceAndPop(op.VectorDatum([datum]))
                # 判斷有沒有偵測到keypoint
                if datum.poseKeypoints is None:
                    print("can't detected keypoint")
                    continue
                # 判斷有沒有偵測到左右手腕
                if (angle_left_elbow(datum.poseKeypoints[0]) is None) or (
                        angle_right_elbow(datum.poseKeypoints[0]) is None):
                    print("can't detected left_elbow_keypoint or right_elbow_keypoint")
                    continue
                # 印出角度
                print("左手角度:",int(angle_left_elbow(datum.poseKeypoints[0])))
                print("右手角度:",int(angle_right_elbow(datum.poseKeypoints[0])))
            frame_cnt += 1
            cv2.imshow("OpenPose 1.7.0 - Tutorial Python API", datum.cvOutputData)
            key = cv2.waitKey(15)
            if cv2.waitKey(1) == ord('q'):  # 每一毫秒更新一次，直到按下 q 結束
                break
    except:
        pass
    cap.release()                           # 所有作業都完成後，釋放資源
    cv2.destroyAllWindows()                 # 結束所有視窗