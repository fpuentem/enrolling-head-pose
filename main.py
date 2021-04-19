# main.py
# import the necessary packages
from flask import Flask, render_template, Response, json, request
from libs.camera import VideoCamera

from datetime import datetime
import time
import csv
import subprocess
import json
import logging
import datetime

app = Flask(__name__)


# face_det = False

status_of_registration = False

TOTAL_OF_PICTURES_ = 12

pictures_taken_per_side = None
pic_taken = 0

path_of_current_person = ""

# writing to csv file  
FILENAME = './pictures/person_0/names.txt'

@app.route('/')
def index():
    # rendering webpage
    return render_template('index.html')

@app.route('/home')
def home():
    return "<h1>Face Enrolling - VisionTech</h1>"

def gen(camera):
    # global face_det
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
                
@app.route('/pictures', methods=['GET'])
def taken_pictures():
    data = {"pictures_taken" : pic_taken, "picture_total" : TOTAL_OF_PICTURES_,
            "pictures_per_side": pictures_taken_per_side, "status":status_of_registration}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/name/<name>', methods=['POST'])
def set_name(name):
    fields = ['name', 'path', 'date']
    # time stamp 
    now = datetime.now() # current date and time
    date_time = now.strftime("%m/%d/%Y %H:%M:%S")

    # my data rows as dictionary objects  
    mydict =[{'name': name, 'path': path_of_current_person, 'date': date_time}]

    with open(FILENAME, 'w') as csvfile:  
        # creating a csv dict writer object     
        writer = csv.DictWriter(csvfile, fieldnames = fields)  
            
        # writing headers (field names)  
        writer.writeheader()  
            
        # writing data rows  
        writer.writerows(mydict)

    response = app.response_class(
        response=json.dumps(mydict[0]),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/name', methods=['GET'])
def get_name():
    with open(FILENAME, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            print(f'\t{row["name"]} pictures in {row["path"]}, taken date: {row["date"]}.')
            line_count += 1
        print(f'Processed {line_count} lines.')
    
    if(row["name"] == "None" or row["path"] == "None"):
        # return {"status": "ERROR"}, 401
        data = {"name" : None, "path" : None, "date" : None}
        response = app.response_class(
            response=json.dumps(data),
            status=400,
            mimetype='application/json'
        )                    
    else: 
        data = {"name" : row["name"], "path" : row["path"], "date" : row["date"]}
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )

    return response

@app.route('/listdb', methods=['GET'])
def people():
    r = subprocess.Popen(['./programs/FaceMe_Sample_DB', '--listdb'],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT)

    stdout, _ = r.communicate()    

    msg = stdout.decode('utf-8')
    msg_list = msg.split('\n')

    names = msg_list[2:]

    num_people = int(msg_list[0].split(' ')[4])
    num_faces = int(msg_list[0].split(' ')[6])
    
    # Response pattern 
    data = {"name" : names, "message":msg, "people": num_people, "faces": num_faces}
    
    response = app.response_class(
        response = json.dumps(data),
        status = 200,
        mimetype = 'application/json'
        )
    
    return response

@app.route('/license/<key_license>', methods=['GET', 'POST', 'DELETE'])
def license(key_license):
    if request.method == 'GET':
        """return the information for <key_license>"""
        r = subprocess.Popen(['./programs/FaceMeLicenseCheck', '--license', key_license],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT)

        stdout, _ = r.communicate()    
        msg = stdout.decode('utf-8')
        # Here, further processing 

        return {"status": "OK - GET", "message":msg}, 201 

    if request.method == 'POST':
        """modify/update the information for <key_license>"""
        r = subprocess.Popen(['./programs/FaceMeSDKVideoSampleTool', 'activate', key_license],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT)

        stdout, _ = r.communicate()    
        msg = stdout.decode('utf-8')
        # Here, further processing 

        return {"status": "OK - POST", "message":msg}, 201 

    if request.method == 'DELETE':
        """deactivate license key"""
        r = subprocess.Popen(['./programs/FaceMeSDKVideoSampleTool', 'deactivate', key_license],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT)

        stdout, _ = r.communicate()    
        msg = stdout.decode('utf-8')
        # Here, further processing 
        return {"status": "OK - DELETE", "message":msg}, 201 

    else:
        return {"status": "ERROR"}, 401

if __name__ == '__main__':
    # defining server ip address and port
    app.run(host='0.0.0.0',port='5000', debug=True)