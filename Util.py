import os
import json
import random
from typing import List, Tuple
from datetime import datetime

import numpy as np
import cv2
import random

class Util:
    def allDirs(self, rootdir: str, localeBlacks: list) -> list:
        ret = []
        for dir in os.listdir(rootdir):
            if any(black in dir for black in localeBlacks):
                continue
            d = os.path.join(rootdir, dir)
            if os.path.isdir(d):
                ret.append(d)
                ret += self.allDirs(d, localeBlacks)
        return ret


    def allFilesTwoList(self, rootdir: str, localeBlacks: list, ext: str) -> Tuple[List[str], List[str]]:
        allDirsRet = self.allDirs(rootdir, localeBlacks)
        allDirsRet.append(rootdir)
        ret0 = []
        ret1 = []
        #------------------------------------------------------------------------------------------
        for dir in allDirsRet:
            dir2fileName_list = os.listdir(dir)
            for dir2fileName in dir2fileName_list:
                # ext가 비어있으면 모든 파일을 수집, 아니면 확장자를 체크
                if not ext or dir2fileName.lower().endswith(ext):
                    fullName = os.path.join(dir, dir2fileName)
                    ret0.append(fullName)
                    ret1.append(fullName)
        return ret0, ret1


    def allFilesSet(self, rootdir: str, localeBlacks: list, ext: str):
        allDirsRet = self.allDirs(rootdir, localeBlacks)
        allDirsRet.append(rootdir)
        ret = set()
        #------------------------------------------------------------------------------------------
        for dir in allDirsRet:
            dir2fileName_list = os.listdir(dir)
            for dir2fileName in dir2fileName_list:
                # ext가 비어있으면 모든 파일을 수집, 아니면 확장자를 체크
                if not ext or dir2fileName.lower().endswith(ext):
                    fullName = os.path.join(dir, dir2fileName)
                    ret.add((fullName, os.path.getsize(fullName)))
        return ret


    def procTime(self, start_time) -> str:
        now = datetime.now()
        elapsed_time = now - start_time
        total_seconds = elapsed_time.total_seconds()
        formatted_time = f"{total_seconds:.2f}"  # 소수점 둘째 자리까지 표시
        return f"{formatted_time}"


    def checkMoreThanSec(self, start_time, sec: int) -> bool:
        now = datetime.now()
        elapsed_seconds = (now - start_time).total_seconds()
        
        if elapsed_seconds > sec:
            return True
        else:
            return False
        

    def pickImageLocale(self, localeInp: str, localeBlacks: list, dropD: int, dropS: int, pick_count: int, ext: str):
        ret = []
        pickAll = []
        #------------------------------------------------------------------------------------------
        allDirsRet = self.allDirs(localeInp, localeBlacks)
        allDirsRet.append(localeInp)
        for dir in allDirsRet:
            dir2fileName_list = os.listdir(dir)
            for dir2fileName in dir2fileName_list:
                # ext가 비어있으면 모든 파일을 수집, 아니면 확장자를 체크
                if not ext or dir2fileName.lower().endswith(ext):
                    fullName = os.path.join(dir, dir2fileName)
                    pickAll.append(fullName)
        try:
            with open('./dropcache.json', 'r') as f:
                dropDict = json.load(f)
        except FileNotFoundError:
            dropDict = dict()
        #-예외-------------------------------------------------------------------------------------
        if (len(pickAll) + pick_count) < len(dropDict):
            print("!!! : Small Result, Please edit Distance or Step")
            dropDict = dict()
            return random.sample(pickAll, pick_count)
        #------------------------------------------------------------------------------------------
        pickEdit_dropCache = [] # 전체 리스트 - 드롭 캐시
        dropKeys = dropDict.keys()
        for i in pickAll:
            if i not in dropKeys:
                pickEdit_dropCache.append(i)
        #------------------------------------------------------------------------------------------
        for i in range(pick_count):
            pick_value = random.choice(pickEdit_dropCache)
            #---------------------------------------------------
            ret.append(pick_value)
            pickEdit_dropCache.remove(pick_value)
            dropDict[pick_value] = dropS
            #---------------------------------------------------
            real_idx = pickAll.index(pick_value)
            for j in range(real_idx, real_idx - dropD - 1, -1):
                #-----------------------------------------------
                if j == -1:
                    break
                if pickAll[j] in dropKeys:
                    continue
                #-----------------------------------------------
                pickEdit_dropCache.remove(pickAll[j])
                dropDict[pickAll[j]] = dropS
            #---------------------------------------------------
            for j in range(real_idx, real_idx + dropD + 1):
                #-----------------------------------------------
                if j == -1:
                    break
                if pickAll[j] in dropKeys:
                    continue
                #-----------------------------------------------
                pickEdit_dropCache.remove(pickAll[j])
                dropDict[pickAll[j]] = dropS
        #------------------------------------------------------------------------------------------
        for key, value in dropDict.items():
            if value > 1:
                dropDict[key] = value - 1
        with open('dropcache.json', 'w') as f:
            json.dump(dropDict, f, indent=4)
        return ret
    

    def resizeAndPutText(self, fileList: list, tagOn: bool, dateType: int, localeTags: dict, w=1920, h=1080):
        size = (w, h)
        for file in fileList:
            base_pic = np.zeros((size[1],size[0],3),np.uint8)
            pic1 = cv2.imread(file[1], cv2.IMREAD_COLOR)
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
                    if "__ELSE__" in localeTags.keys():
                        timetag += f' {localeTags["__ELSE__"]}'
                    else:
                        timetag += " __"
                #------------------------------------------------------
                cv2.putText(base_pic,timetag,(1528,1040),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,1,(0,0,0),4,cv2.LINE_AA)
                cv2.putText(base_pic,timetag,(1528,1040),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,1,(255,255,255),1,cv2.LINE_AA)
            cv2.imwrite('./' + file[0], base_pic)


    def resizeAndPutTextJD(self, file_list, tagOn, dateType, localeTags: dict, w=1920, h=1080, splitSize=2, textSize=1, tx=650, ty=515):
        size = (w//splitSize, h//splitSize)
        for file in file_list:
            base_pic = np.zeros((size[1],size[0],3),np.uint8)
            pic1 = cv2.imread(file[1], cv2.IMREAD_COLOR)
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
                    if "__ELSE__" in localeTags.keys():
                        timetag += f' {localeTags["__ELSE__"]}'
                    else:
                        timetag += " __"
                #------------------------------------------------------
                cv2.putText(base_pic,timetag,(tx,ty),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,textSize,(0,0,0),4,cv2.LINE_AA)
                cv2.putText(base_pic,timetag,(tx,ty),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,textSize,(255,255,255),1,cv2.LINE_AA)
            cv2.imwrite('./' + file[0], base_pic)


    """
    def merge(file_list, w=1920, h=1080, splitSize=2):
        w = w // splitSize
        h = h // splitSize
        result_image = np.zeros((h*splitSize, w*splitSize, 3), dtype=np.uint8)
        fidx = 0
        nidx = 0
        retList = []
        while fidx != len(file_list):
            for i in range(splitSize):
                for j in range(splitSize):
                    pic = cv2.imread(file_list[fidx][0])
                    fidx += 1
                    result_image[i*h:(i+1)*h, j*w:(j+1)*w] = pic
            cv2.imwrite(f'./{nidx}.png', result_image)
            retList.append(f'./{nidx}.png')
            nidx += 1
        return retList
    """

    def merge(self, file_list, w=1920, h=1080, splitSize=2):
        w = w // splitSize
        h = h // splitSize
        result_image = np.zeros((h*splitSize, w*splitSize, 3), dtype=np.uint8)
        fidx = 0
        while fidx != len(file_list):
            for i in range(splitSize):
                for j in range(splitSize):
                    pic = cv2.imread(file_list[fidx][0])
                    fidx += 1
                    result_image[i*h:(i+1)*h, j*w:(j+1)*w] = pic
            cv2.imwrite(f'./jd.png', result_image)
        return