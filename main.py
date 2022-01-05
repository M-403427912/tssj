# -*- coding: utf-8 -*-


import math
import re
import random
import sys
import time
import os
from PIL import Image
import os
from PIL import Image, ImageDraw, ImageFile
import numpy
import cv2
import imagehash
import collections
if sys.version_info.major != 3:
    print('请使用Python3')
    exit(1)
try:
    from common import debug, config, screenshot, UnicodeStreamFilter
    from common.auto_adb import auto_adb
except Exception as ex:
    print(ex)
    print('请将脚本放在项目根目录中运行')
    print('请检查项目根目录中的 common 文件夹是否存在')
    exit(1)
adb = auto_adb()


# DEBUG 开关，需要调试的时候请改为 True，不需要调试的时候为 False
DEBUG_SWITCH = False
adb.test_device()
# Magic Number，不设置可能无法正常执行，请根据具体截图从上到下按需
# 设置，设置保存在 config 文件夹中
# cfg = config.open_accordant_config()


def compare_image_with_hash(image_file1, hash_2_1, max_dif=0):
    """
    max_dif: 允许最大hash差值, 越小越精确,最小为0
    推荐使用
    """
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    hash_1 = None
    hash_2 = hash_2_1
    hash_1 = imagehash.average_hash(image_file1)
    # with open(image_file1, 'rb') as fp:
    #     hash_1 = imagehash.average_hash(Image.open(fp))
    # print(hash_1)
    # with open(image_file2, 'rb') as fp:
    #     hash_2 = imagehash.average_hash(Image.open(fp))
    # print(hash_2)
    dif = hash_1 - hash_2
    # print(dif)
    if dif < 0:
        dif = -dif
    if dif <= max_dif:
        return True
    else:
        return False
SCENECFG = {

    #'首页': [[(306, 1088, 411, 1144), "关卡", 1]],

    "新英雄": [(171, 1007, 230, 1055), "新英雄", 5],
    "2星英雄": [(53, 1140, 133, 1215), "2星英雄", 5],
    #'继续ok': [[(324, 1174, 398, 1228), "OK", 3]],
    '体力不足': [(292, 134, 435, 180), "体力不足", 5],

    '战斗页': [(477, 24, 532, 56), "分数", 5],



    #'登陆页': [[(272, 1095, 429, 1140), "点击", 2]],
    '直接发放': [(293, 723, 440, 761), "直接发放", 5],

    '升级': [(317, 561, 387, 604), "升级", 5],
    '弹窗概要1': [(305, 386, 435, 449), "弹窗概要1", 5],
    '弹窗概要4': [(305, 386, 435, 449), "弹窗概要4", 5],
    '弹窗概要': [(305, 386, 435, 449), "弹窗概要", 5],
    '弹窗关闭': [(290, 792, 440, 857), "弹窗关闭", 5],
    '跳过': [(681, 36, 699, 67), "跳过", 5],
    '每日跳过': [(681, 36, 699, 67), "每日跳过", 5],
    #'奖励跳过': [[(600, 24, 681, 70), "奖励跳过", 1]],
    '是否参加': [(376, 1165, 519, 1222), "关卡信息", 5],
    '参加': [(457, 1040, 592, 1098), "参加", 5],
    '准备完毕': [(285, 894, 435, 941), "准备完毕", 5],
    '准备完毕1': [(285, 894, 435, 941), "准备完毕1", 5],
    '解算ok': [(335, 806, 390, 844), "OK", 5],
    '过关ok': [(305, 1180, 408, 1234), "过关ok", 5],
    '继续': [(324, 1174, 398, 1228), "继续", 5],
    '离开房间': [(152, 1181, 277, 1228), "离开房间", 5],
    '挑战': [(296, 1069, 382, 1115), "挑战", 5],
    '挑战1': [(296, 1069, 382, 1115), "挑战1", 5],
    '继续副本': [(484, 795, 565, 848), "继续", 5],
    '再次挑战': [(457, 1180, 598, 1227), "再次挑战", 5],

    '放弃': [(62, 1189, 205, 1261), "放弃", 5],
    '关闭': [(314, 1143, 402, 1213), "关闭", 5],
    '登陆页1': [(37, 1182, 89, 1263), "登陆页1", 5],




    '加号': [(406, 18, 455, 64), "加号", 5],
    # '获得道具': [[(93, 731, 190, 759), "获得道具", 1]],
}


BUTTONCFG = {
    '点击登陆': (272, 1095),
    '参加': (481, 1064),
    '是否参加': (448, 1189),
    '放弃': (645, 68),
    '体力不足取消': (368, 1070),
    '返回': (60, 1230),
    '跳窗跳过': (500, 854),
}

COLORCFG = {
    "铃铛": [(48, 35), (255, 255, 255)],
    "铃铛战斗": [(35, 75), (255, 255, 255)],
    "准备完毕": [(262, 931), (224, 224, 224)]
}

VALUECFG = {
    "体力": (119, 18, 212, 48)
}


def recolor(img):
    width = img.size[0]  # 长度
    height = img.size[1]  # 宽度
    for i in range(0, width):  # 遍历所有长度的点
        for j in range(0, height):  # 遍历所有宽度的点
            c = img.getpixel((i, j))
            if abs(c[0] - 46) <= 30 and abs(c[1] - 196) <= 30 and abs(c[2] - 182) <= 30:
                img.putpixel((i, j), (255, 255, 255))
            else:
                img.putpixel((i, j), (0, 0, 0))
    return img


def w2bcolor(img):
    width = img.size[0]  # 长度
    height = img.size[1]  # 宽度
    for i in range(0, width):  # 遍历所有长度的点
        for j in range(0, height):  # 遍历所有宽度的点
            c = img.getpixel((i, j))
            if abs(c[0] - 255) <= 40 and abs(c[1] - 255) <= 40 and abs(c[2] - 255) <= 40:
                img.putpixel((i, j), (0, 0, 0))

    return img


def writeLog(str1):
    s1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    s = s1 + "  " + str1 + "\n"
    print(s)
    # with open('log.txt', 'a') as f:
    #     s = s1 + "  " + str1 + "\n"
    #     print(s)
    #     f.write(s)


def checkColor(cfg):
    im = screenshot.pull_screenshot()
    im_pixel = im.load()
    c = im_pixel[cfg[0]]
    d = 5
    # print(c)
    if abs(c[0] - cfg[1][0]) <= 5 and abs(c[1] - cfg[1][1]) <= 5 and abs(c[2] - cfg[1][2]) <= 5:
        return True
    return False


def click(cfg):
    cmd = 'adb shell input tap ' + str(round(random.uniform(cfg[0], cfg[0] + 10), 1)) + ' ' + str(round(random.uniform(cfg[1], cfg[1] + 10), 1))
    # print(cmd)
    os.system(cmd)
    time.sleep(random.uniform(0.6, 0.8))


def restart(name, name1):
    # print("尝试关闭：" + name)
    cmd = 'adb shell am force-stop ' + name
    # print(cmd)
    os.system(cmd)
    time.sleep(5)
    # print("尝试启动：" + name)
    cmd = 'adb shell am start -n ' + name1
    # print(cmd)
    os.system(cmd)
    time.sleep(5)
    print("重启游戏完毕：" + name)


def getValue(cfg):
    im = screenshot.pull_screenshot()
    text = pytesseract.image_to_string(im.crop(cfg), lang='chi_sim').replace(' ', '').replace('\n', '')
    return text


def checkScene():
    count = 0
    while True:
        begin_time = time.time()
        im = screenshot.pull_screenshot()
        for key in SCENECFG:
            flag = True
            cfg = SCENECFG[key]

            im1 = im.crop(cfg[0])
            if cfg[2] == 3:
                im1 = recolor(im.crop(cfg[0]))
            if cfg[2] == 4:
                im1 = w2bcolor(im.crop(cfg[0]))
            if cfg[2] == 5:
                # 找图
                # im.crop(cfg[0]).save("spng/" + key + ".png")

                if not compare_image_with_hash(im.crop(cfg[0]), hash_2s[key], 1):
                    flag = False

            else:
                text = ""
               # text = pytesseract.image_to_string(im1, lang='chi_sim').replace(' ', '').replace('\n', '')
                # print(key + "  :  " + text)
                # print(cfg[1])
                if key == '英雄':
                    im.crop(cfg[0]).save(key + ".png")
                if text != cfg[1]:
                    # print("界面识别成功为：" + key)
                    flag = False
            if flag:
                if cfg[2] != 5:
                    im.crop(cfg[0]).save(key + ".png")
                # print("界面识别成功为：" + key)
                count = 0
                return key
        # print("无法识别当前界面，等待1秒继续")
        time.sleep(0.5)
        count = count + 1
        if count >= 60 * 10:
            count = 0
            print("卡住了。截图重启")
            im.save("异常/异常截图.png")
            restart("com.leiting.wf", "com.leiting.wf/air.com.leiting.wf.AppEntry")
hash_2s = dict()


def main():
    """
    主函数
    """

    VERSION = "1.0.0"
    print("当前版本：" + VERSION)
    print('激活窗口并按 CONTROL + C 组合键退出')
    # debug.dump_device_info()
    screenshot.check_screenshot()
    print("初始化截图")
    for key in SCENECFG:
        cfg = SCENECFG[key]
        if cfg[2] == 5:
            with open("png/" + key + ".png", 'rb') as fp:
                hash_2 = imagehash.average_hash(Image.open(fp))
                hash_2s[key] = hash_2

    print("开始")
    # 启动游戏
    # restart("com.leiting.wf", "com.leiting.wf/air.com.leiting.wf.AppEntry")
    while True:
        scene = checkScene()
        # continue
        # print(scene)
        if scene == "登陆页1":
            print("当前是登陆页")
            click(BUTTONCFG["点击登陆"])
        elif scene == "加号":
            # print("当前是首页")
            # tili = getValue(VALUECFG["体力"])
            # print("当前体力:" + tili)

            # 开始检查 铃铛

            flag = checkColor(COLORCFG["铃铛"])
            if flag:
                # print("铃铛可以点击！！！！！！！！！！！")
                writeLog("铃铛可以点击！！！！！！！！！！！")
                click(COLORCFG["铃铛"][0])
                click(BUTTONCFG["参加"])
        elif scene == "战斗页":

            flag = checkColor(COLORCFG["铃铛战斗"])
            if flag:
                # print("铃铛可以点击！！！！！！！！！！！")
                writeLog("铃铛战斗可以点击！！！！！！！！！！！")
                click(COLORCFG["铃铛战斗"][0])
                click(BUTTONCFG["是否参加"])
        elif scene == "参加":
            # print("当前是参加界面")
            click(BUTTONCFG["参加"])
        elif scene == "放弃":
            # print("当前是放弃界面")
            click(BUTTONCFG["放弃"])
        elif scene == "是否参加":
            # print("当前是参加界面")
            click(BUTTONCFG["是否参加"])
        elif "弹窗概要" in scene:
            # print("当前是参加界面")
            click(BUTTONCFG["跳窗跳过"])
        elif scene == "准备完毕" or scene == "准备完毕1":
            # print("当前是准备完毕界面")
            flag = checkColor(COLORCFG["准备完毕"])
            if flag:
                # print("需要点击准备完毕")
                click(COLORCFG["准备完毕"][0])

                # writeLog("参加一次")

        elif scene == "解算ok":
            # print("当前是解算ok界面")
            click(SCENECFG["解算ok"][0])
            # writeLog("OK一次")
        elif scene == "2星英雄":
            print("掉落新卡片了！！")
            im = screenshot.pull_screenshot()
            im.save("掉落/掉落新英雄" + str(time.time()) + ".png")
            click(SCENECFG[scene][0])
        elif scene == "英雄":
            print("掉落卡片了！！")
            im = screenshot.pull_screenshot()
            im.save("掉落/掉落英雄" + str(time.time()) + ".png")
            click(SCENECFG[scene][0])
        elif scene == "体力不足":
            print("体力不足！")
            restart("com.leiting.wf", "com.leiting.wf/air.com.leiting.wf.AppEntry")
        else:
            # pass
            click(SCENECFG[scene][0])
        # time.sleep(0.1)
        # print("\n\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        adb.run('kill-server')
        print('\n谢谢使用', end='')
        exit(0)
