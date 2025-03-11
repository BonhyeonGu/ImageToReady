from flask import Flask, send_file, render_template, jsonify, make_response
import threading
import time
import json
from datetime import datetime
from Util import Util
from m1MageProc import ImageProc
import logging

util = Util()
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

selectedPhotos = []
    
def update():
    global selectedPhotos

    with open('/vol/setting.json', 'r') as f:
        set = json.load(f)

    timeUP = set["start_time"]["update"]
    timePick = set["start_time"]["pick"]
    imgproc = ImageProc(set)
    
    swFirst = True
    lastUpdateTime = datetime.now()
    lastPickTime = datetime.now()

    print('SUB -- Start Daemon')
    
    # Flask 애플리케이션 컨텍스트 시작
    with app.app_context():  
        while True:
            # Update check
            if util.checkMoreThanSec(lastUpdateTime, timeUP) or swFirst:
                tTime = datetime.now()
                imgproc.updateCpList()
                print(f">>{util.procTime(tTime)}")
                lastUpdateTime = datetime.now()

            # Pick check
            if util.checkMoreThanSec(lastPickTime, timePick) or swFirst:
                swFirst = False
                tTime = datetime.now()
                ret = imgproc.pathRandPick()

                # 리스트를 새로 할당하지 않고 내용을 교체
                selectedPhotos.clear()  # 기존 리스트 내용을 제거
                selectedPhotos.extend(ret)  # 새로운 항목 추가

                print(f"SUB_{tTime}_Picked->",end="")
                n = 0
                for i in ret:
                    print(f"{i.split('.')[1][:3]} ", end="")
                    n += 1
                print(f">> {util.procTime(tTime)}")
                lastPickTime = datetime.now()

            time.sleep(5)



t0 = threading.Thread(target=update)
t0.daemon = True
t0.start()

@app.route('/api/images')
def list():
    return jsonify({'images': selectedPhotos})

@app.route('/photo/<int:index>')
def photo(index):
    if 0 <= index < len(selectedPhotos):
        img = selectedPhotos[index]
        response = make_response(send_file(img, conditional=False))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)