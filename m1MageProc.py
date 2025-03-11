import numpy as np
import cv2
import os
import re
from datetime import datetime
import random
import json

from Util import Util

util = Util()

class ImageProc:
    def __init__(self, dictArg: dict) -> None:
        self.namePattern = re.compile("(\d\d\d\d)-(\d\d)-(\d\d)_(\d\d)-(\d\d)-(\d\d)")

        self.pDirOri = dictArg['path']['dir_original']
        self.pDirCp = os.path.join(dictArg['path']['dir_volume'], 'cp')
        self.pFileCpList = os.path.join(dictArg['path']['dir_volume'], 'update_list.json')
        self.pFileDrop = os.path.join(dictArg['path']['dir_volume'], 'dropcache.json')
        
        self.dirBlack = dictArg['dirBlacklist']
        self.dropD = dictArg['drop']['distance']
        self.dropS = dictArg['drop']['step']
        self.numPick = dictArg['pick_num']
        self.oSizeW = dictArg['size']['width']
        self.oSizeH = dictArg['size']['height']
        self.oSizeTX = dictArg['size']['tx']
        self.oSizeTY = dictArg['size']['ty']

        self.tagSw = dictArg['tag']['sw']
        self.tagType = dictArg['tag']['type']
        self.pathToTag = dictArg['tag']['path_to_tag']
        
        if not os.path.exists(self.pDirCp):
            os.makedirs(self.pDirCp)

    
    def image_ReSize_PutText_Copy(self, fullName: str, tagOn: bool, dateType: int, localeTags: dict) -> None:
        name = os.path.basename(fullName)

        w = self.oSizeW
        h = self.oSizeH

        size = (w, h)

        base_pic=np.zeros((size[1],size[0],3),np.uint8)
        pic1=cv2.imread(fullName, cv2.IMREAD_COLOR)
        try:
            while(True):
                h,w=pic1.shape[:2]
                break
        except Exception as e:
            print(f"Error! : {type(e).__name__}", end="")
            print(fullName)
            return
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
                tag = os.path.getctime(fullName)
                timetag = datetime.fromtimestamp(tag).strftime('%Y.%m.%d %H:%M')
            elif dateType == 1:
                tag = os.path.getmtime(fullName)
                timetag = datetime.fromtimestamp(tag).strftime('%Y.%m.%d %H:%M')
            elif dateType == 2:
                search_res = self.namePattern.search(name)
                try:
                    search_res = search_res.groups()
                    timetag = '%s.%s.%s %s:%s'%(search_res[0], search_res[1], search_res[2], search_res[3], search_res[4])
                except:
                    tag = os.path.getmtime(fullName)
                    timetag = datetime.fromtimestamp(tag).strftime('%Y.%m.%d %H:%M')
            else:
                return
            #------------------------------------------------------
            untagch = True
            for key in localeTags.keys():
                if key in fullName:
                    timetag += f" {localeTags[key]}"
                    untagch = False
                    break
            if untagch:
                if "__ELSE__" in localeTags.keys():
                    timetag += f' {localeTags["__ELSE__"]}'
                else:
                    timetag += " __"
            #------------------------------------------------------
            cv2.putText(base_pic,timetag,(self.oSizeTX,self.oSizeTY),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,1,(0,0,0),4,cv2.LINE_AA)
            cv2.putText(base_pic,timetag,(self.oSizeTX,self.oSizeTY),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,1,(255,255,255),1,cv2.LINE_AA)
        cv2.imwrite(os.path.join(self.pDirCp, name), base_pic)


    def updateCpList(self) -> None:
        cps = set()
        try:
            with open(self.pFileCpList, 'r') as f:
                for line in f:
                    file_name, file_size = line.strip().split(',')
                    cps.add((file_name, int(file_size)))
        except FileNotFoundError:
            pass
        
        oris = util.allFilesSet(self.pDirOri, self.dirBlack, 'png')

        cMo = cps - oris
        numDel = len(cMo)
        for fullName, size in cMo:
            os.system(f'rm -rf {fullName}')
            cps.remove((fullName, size))
        oMc = oris - cps
        numNew = len(oMc)
        for fullName, size in oMc:
            self.image_ReSize_PutText_Copy(fullName, self.tagSw, self.tagType, self.pathToTag)
            cps.add((fullName, size))

        with open(self.pFileCpList, 'w') as f:
            for item in cps:
                f.write(f"{item[0]},{item[1]}\n")
                
        tTime = datetime.now()
        print(f"SUB_{tTime}_Updated->Deleted:{numDel},Created:{numNew}", end="")


    def pathRandPick(self) -> list:
        return util.pickImageLocale(self.pDirCp, self.dirBlack, self.dropD, self.dropS, self.numPick, 'png')