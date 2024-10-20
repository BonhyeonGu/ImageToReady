import json
from datetime import datetime
from time import sleep
import os
import numpy as np
import cv2
import random
import re


namePattern = re.compile("(\d\d\d\d)-(\d\d)-(\d\d)_(\d\d)-(\d\d)-(\d\d)")

def allDirs(rootdir: str, localeBlacks: list) -> list:
    ret = []
    for dir in os.listdir(rootdir):
        #포함 확인
        if any(black in dir for black in localeBlacks):
            continue
        d = os.path.join(rootdir, dir)
        if os.path.isdir(d):
            ret.append(d)
            ret += allDirs(d, localeBlacks)
    return ret


def pickImageLocale(localeInp: str, localeBlacks: list, dropD: int, dropS: int, pick_count=6):
    allDirsRet = allDirs(localeInp, localeBlacks)
    allDirsRet.append(localeInp)
    #------------------------------------------------------------------------------------------
    tempRet = []
    emmRet = []
    #------------------------------------------------------------------------------------------
    for dir in allDirsRet:
        dir2fileName_list = os.listdir(dir)
        for dir2fileName in dir2fileName_list:
            if dir2fileName.lower().endswith(".png"):
                tempRet.append((dir2fileName, os.path.join(dir, dir2fileName)))
                emmRet.append((dir2fileName, os.path.join(dir, dir2fileName)))
    #------------------------------------------------------------------------------------------
    try:
        with open('./dropcache.json', 'r') as f:
            dropFiles = json.load(f)
    except FileNotFoundError:
        dropFiles = dict()
    #------------------------------------------------------------------------------------------
    nextDropFiles = dict()
    #------------------------------------------------------------------------------------------
    tempRet = [item for item in tempRet if item[1] not in dropFiles or dropFiles[item[1]] <= 1]
    
    if len(tempRet) < pick_count:
        print("!!! : Small Result, Please edit Distance or Step")
        nextDropFiles = dict()
        ret = random.sample(emmRet, pick_count)
    else:
        idxList = list(range(len(tempRet)))
        idxRet = []
        ret = []
        # 위에는 키 값으로 비교하지만 여기선 인덱스로 비교한다. 순서가 꼬일 수 있다는 것을 고려해야한다.
        # 효율 없지만 순서가 지켜져야하기 때문에..
        for i in range(pick_count):
            ri = random.choice(idxList)
            for j in range(ri, ri + dropD + 1):
                if j in idxList:
                    idxList.remove(j)
                    nextDropFiles[tempRet[j][1]] = dropS
            for j in range(ri - dropD, ri):
                if j in idxList:
                    idxList.remove(j)
                    nextDropFiles[tempRet[j][1]] = dropS
            idxRet.append(ri)
            #------------------------------------------------------------------------------------------
            # [0]은 이름 [1]은 파일 경로
            nextDropFiles[tempRet[ri][1]] = dropS
            ret.append((tempRet[ri][0], tempRet[ri][1]))
        #------------------------------------------------------------------------------------------
        for key, value in dropFiles.items():
            if value > 1:
                nextDropFiles[key] = value - 1
        
        with open('dropcache.json', 'w') as f:
            json.dump(nextDropFiles, f, indent=4)
        #------------------------------------------------------------------------------------------
    return ret


def resizeAndPutText(fileList: list, tagOn: bool, dateType: int, localeTags: dict, w=1920, h=1080):
    global namePattern

    size = (w, h)
    for file in fileList:
        base_pic=np.zeros((size[1],size[0],3),np.uint8)
        pic1=cv2.imread(file[1], cv2.IMREAD_COLOR)
        try:
            while(True):
                h,w=pic1.shape[:2]
                break
        except:
            print("치명적인 문제!")
            print(file)
            continue
        ash = size[1]/h
        asw = size[0]/w
        if asw<ash:
            sizeas = (int(w*asw), int(h*asw))
        else:
            sizeas = (int(w*ash), int(h*ash))
        pic1 = cv2.resize(pic1,dsize=sizeas)
        base_pic[int(size[1]/2-sizeas[1]/2):int(size[1]/2+sizeas[1]/2),
        int(size[0]/2-sizeas[0]/2):int(size[0]/2+sizeas[0]/2),:]=pic1

        if tagOn:
            if dateType == 0:
                tag = os.path.getctime(file[1])
                timetag = datetime.fromtimestamp(tag).strftime('%Y.%m.%d %H:%M')
            elif dateType == 1:
                tag = os.path.getmtime(file[1])
                timetag = datetime.fromtimestamp(tag).strftime('%Y.%m.%d %H:%M')
            elif dateType == 2:
                search_res = namePattern.search(file[0])
                try:
                    search_res = search_res.groups()
                    timetag = '%s.%s.%s %s:%s'%(search_res[0], search_res[1], search_res[2], search_res[3], search_res[4])
                except:
                    tag = os.path.getmtime(file[1])
                    timetag = datetime.fromtimestamp(tag).strftime('%Y.%m.%d %H:%M')
            else:
                break
            #------------------------------------------------------
            untagch = True
            for key in localeTags.keys():
                if key in file[1]:
                    timetag += f" {localeTags[key]}"
                    untagch = False
                    break
            if untagch:
                timetag += "__"
            #------------------------------------------------------
            cv2.putText(base_pic,timetag,(1528,1040),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,1,(0,0,0),4,cv2.LINE_AA)
            cv2.putText(base_pic,timetag,(1528,1040),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,1,(255,255,255),1,cv2.LINE_AA)
        cv2.imwrite('./' + file[0], base_pic)


def routine(localeInp: str, localeBlacks: list, localeTags: dict, dropD: int, dropS: int, tagOn: bool, dateType: str, localeOut: str) -> None:
    print("%s start: routine" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    fileList = pickImageLocale(localeInp, localeBlacks, dropD, dropS)
    for i in range(len(fileList)):
        print(fileList[i][1])
    resizeAndPutText(fileList, tagOn, dateType, localeTags)

    maxIdx = 0
    for idx, file in enumerate(fileList):
        os.rename(os.path.join("./", file[0]), os.path.join("./", f"{idx}.png"))
        maxIdx = idx
    #----------------------------------------------------------------------------------------------------------
    for i in range(maxIdx + 1):
        os.system(f'cp ./{i}.png {localeOut}')
    #----------------------------------------------------------------------------------------------------------
    os.system('rm -rf ./*.png')
    print("%s end: routine" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print("")

if __name__ == "__main__":
    with open('./png2mp4.json', 'r') as f:
        inp = json.load(f)
        interTime = inp["interTime"]
        localeInp = inp["locale_inp"]
        localeOut = inp["locale_out"]
        localeBlacks = inp["locale_blacklist"]
        localeTags = inp["locale_tag"]

        tagOn = inp["tag_on"]
        dateType = inp["date_type"]

        dropD = inp["drop"]["distance"]
        dropS = inp["drop"]["step"]


    while(True):
        sleep(interTime)
        if("START" in os.listdir('./cmd/')):
            try:
                routine(localeInp, localeBlacks, localeTags, dropD, dropS, tagOn, dateType, localeOut)
            except ValueError as ve:
                print(f"Caught a ValueError: {ve}")
            except TypeError as te:
                print(f"Caught a TypeError: {te}")
            except IndexError as ie:
                print(f"Caught an IndexError: {ie}")
            except Exception as e:
                print(f"Caught an unexpected error: {e}")
