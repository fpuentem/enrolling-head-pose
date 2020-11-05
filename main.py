# main.py
# import the necessary packages
from flask import Flask, render_template, Response, json
from libs.camera import VideoCamera
import time
app = Flask(__name__)


face_det = False

status_of_registration = False

TOTAL_OF_PICTURES_ = 17

pictures_taken_per_side = None
pic_taken = 0

path_of_current_person = ""

@app.route('/')
def index():
    # rendering webpage
    return render_template('index.html')

@app.route('/home')
def home():
    return "<h1>Face Enrolling - VisioTech</h1>"

def gen(camera):
    global face_det
    global status_of_registration
    global pictures_taken_per_side
    global pic_taken
    global path_of_current_person
    time.sleep(0.5)
    
    while True:
        frame = camera.get_frame()
        status_of_registration = camera.get_flag_status_of_pictures()
        pictures_taken_per_side, pic_taken = camera.get_status_of_pictures()
        path_of_current_person = camera.current_folder
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
               
@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
                
@app.route('/status_of_pictures', methods=['GET'])
def status_of_pictures():   
    return {"status": "{}".format(status_of_registration)}, 201

@app.route('/taken_pictures', methods=['GET'])
def taken_pictures():
    data = {"pictures_taken" : pic_taken, "picture_total" : TOTAL_OF_PICTURES_,
            "pictures_per_side": pictures_taken_per_side}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/current_path', methods=['GET'])
def current_path():
    data = {"path" : path_of_current_person}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response
if __name__ == '__main__':
    # defining server ip address and port
    app.run(host='0.0.0.0',port='5000', debug=True)