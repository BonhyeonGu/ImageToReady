import json
from datetime import datetime
from time import sleep
import os

import re
import subprocess
import pysftp

from Util import Util

util = Util()
namePattern = re.compile("(\d\d\d\d)-(\d\d)-(\d\d)_(\d\d)-(\d\d)-(\d\d)")


def imagesToMp4(fileList):
    cmd = ""
    cmd += 'ffmpeg -loglevel fatal -y -loop 1 -t 10 -i %s -loop 1 -t 10 -i %s -loop 1 -t 10 -i %s -loop 1 -t 10 -i %s -loop 1 -t 10 -i %s ' % ("./" + fileList[0][0], "./" + fileList[1][0], "./" + fileList[2][0], "./" + fileList[3][0], "./" + fileList[4][0])
    cmd += ' -loop 1 -t 10 -i %s -loop 1 -t 10 -i %s -loop 1 -t 10 -i %s -loop 1 -t 10 -i %s -loop 1 -t 10 -i %s ' % ("./" + fileList[5][0], "./" + fileList[6][0], "./" + fileList[7][0], "./" + fileList[8][0], "./" + fileList[9][0])

    cmd += '-filter_complex "[0:v]fade=t=in:st=0:d=1, fade=t=out:st=9:d=1[v0]; '
    cmd += '[1:v]fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[v1]; [2:v]fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[v2]; '
    cmd += '[3:v]fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[v3]; [4:v]fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[v4]; '
    cmd += ' [5:v]fade=t=in:st=0:d=1, fade=t=out:st=9:d=1[v5]; '
    cmd += '[6:v]fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[v6]; [7:v]fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[v7]; '
    cmd += '[8:v]fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[v8]; [9:v]fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[v9]; '
    cmd += '[v0][v1][v2][v3][v4][v5][v6][v7][v8][v9]concat=n=10:v=1:a=0,format=yuv420p[v]" -map "[v]" %s' % ('./' + "out0.mp4")
    os.system(cmd)


def routine(localeInp: str, localeBlacks: list, localeTags: dict, dropD: int, dropS: int, tagOn: bool, dateType: str, mp4On: bool, host: str, port: int, id: str, pw: str, sftpOutLocale: str, ) -> None:
    print("%s start: routine" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    fileList = util.pickImageLocale(localeInp, localeBlacks, dropD, dropS, 6, ".png")
    for i in range(len(fileList)):
        print(fileList[i][1])
    for i in fileList:
        print(fileList[i], end=" ")
        util.resizeAndPutText(i, tagOn, dateType, localeTags, namePattern)
        print("")

    #print("%s start: ffmpeg" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    if mp4On:
        imagesToMp4(fileList)
    #print("%s end: ffmpeg" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    maxIdx = 0
    for idx, file in enumerate(fileList):
        os.rename(os.path.join("./", file[0]), os.path.join("./", f"{idx}.png"))
        maxIdx = idx
    #----------------------------------------------------------------------------------------------------------
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(host, port=port, username=id, password=pw, cnopts=cnopts) as sftp:
        for i in range(maxIdx + 1):
            sftp.put(f"./{i}.png", sftpOutLocale+f"{i}.png")
        if mp4On:
            sftp.put('./out0.mp4', sftpOutLocale+'out0.mp4')
    #----------------------------------------------------------------------------------------------------------
    os.system('rm -rf ./*.png')

    print("%s end: routine" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print("")


def routineJD(localeInp: str, localeBlacks: list, localeTags: dict, dropD: int, dropS: int, tagOn: bool, dateType: str, mp4On: bool, host: str, port: int, id: str, pw: str, sftpOutLocale: str, ) -> None:
    fileList = util.pickImageLocale(localeInp, localeBlacks, dropD, dropS, 4, ".png")
    for i in fileList:
        print(fileList[i], end=" ")
        util.resizeAndPutTextJD(i, tagOn, dateType, localeTags)
        print("")
    #한개라는 가정
    util.merge(fileList)
    #----------------------------------------------------------------------------------------------------------
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(host, port=port, username=id, password=pw, cnopts=cnopts) as sftp:
        sftp.put(f"jd.png", sftpOutLocale+f"jd.png")
    #----------------------------------------------------------------------------------------------------------
    os.system('rm -rf ./*.png')


if __name__ == "__main__":
    with open('./setting.json', 'r') as f:
        inp = json.load(f)
        interTime = inp["interTime"]
        localeInp = inp["locale_inp"]
        localeBlacks = inp["locale_blacklist"]
        localeTags = inp["locale_tag"]

        tagOn = inp["tag_on"]
        dateType = inp["date_type"]
        mp4On = inp["mp4_on"]

        dropD = inp["drop"]["distance"]
        dropS = inp["drop"]["step"]
        host = inp["sftp"]["host"]
        port = inp["sftp"]["port"]
        id = inp["sftp"]["id"]
        pw = inp["sftp"]["pw"]
        sftpOutLocale = inp["sftp"]["locale"]

        jdSw = inp["jd"]["sw"]
        jdInp = inp["jd"]["inp"]
        jdBlacklist = inp["jd"]["blacklist"]
        jdDropD = inp["jd"]["distance"]
        jdDropS = inp["jd"]["step"]


    swStart = True
    while(True):
        sleep(interTime)
        if("START" in os.listdir('./cmd/')):
            if(swStart):
                for i in inp["cmd"]:
                    subprocess.run(i, shell=True, check=True, capture_output=True, text=True)
                swStart = False
            try:
                if jdSw:
                    routineJD(jdInp, jdBlacklist, localeTags, jdDropD, jdDropS, tagOn, dateType, mp4On, host, port, id, pw, sftpOutLocale)
                routine(localeInp, localeBlacks, localeTags, dropD, dropS, tagOn, dateType, mp4On, host, port, id, pw, sftpOutLocale)

            except ValueError as ve:
                print(f"Caught a ValueError: {ve}")
            except TypeError as te:
                print(f"Caught a TypeError: {te}")
            except IndexError as ie:
                print(f"Caught an IndexError: {ie}")
            except Exception as e:
                print(f"Caught an unexpected error: {e}")
