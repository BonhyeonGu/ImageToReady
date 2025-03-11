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

    
    def image_ReSize_PutText_Copy(self, file_abs_path: str, tagOn: bool, dateType: int, localeTags: dict) -> None:
        util.resizeAndPutText(file_abs_path, tagOn, dateType, localeTags, self.namePattern, self.oSizeW, self.oSizeH, self.oSizeTX, self.oSizeTY)
        
        
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