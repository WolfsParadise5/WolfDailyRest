#Programming of the REST API
import smtplib
import os
from dotenv import load_dotenv
from flask import Flask, request
from pymongo import MongoClient
from flask_cors import CORS
from email.mime.text import MIMEText

load_dotenv()

#Get all required variable
db_username = os.getenv("USERNAME_DB") 
db_password = os.getenv("PASSWORD_DB") 
db_clusterName =  os.getenv("CLUSTER") 
db_name = os.getenv("NAME_DB")
mailgun_user = os.getenv("MAILCODE")
mailgun_pass = os.getenv("MAILGUN_APIKEY") 
 

app = Flask(__name__)
CORS(app)


#Set up PyMongo
cluster = MongoClient("mongodb+srv://" + db_username  + ":"+ db_password + ".@" + db_clusterName + ".mongodb.net/" + db_name + "?retryWrites=true&w=majority")
db = cluster["BlogPosts"]
collection = db["BlogPosts"]

dbproj = cluster["Projects"]
collectionProj = dbproj["Project"]
collectionProgress = dbproj["Progress"]

dbaux = cluster["UsefulData"]
collectionSuggestions = dbaux["Suggestions"]

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*" # <- You can change "*" for a domain for example "http://localhost"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
    return response

@app.route("/")
def homepage():
    return {"Greeting":"Welcome to the soon lagoon, newcomer!"}

#Blog
@app.route("/posts", methods=['POST'])
def add_post():
    post = {"_id": request.json['_id'],"postname": request.json['title'],"thumbnailLocation": request.json['thumbnailURL'],"content": request.json['body'],"authorName": request.json['author']}
    collection.insert_one(post)
    print("Post successful!")
    return {"id":200}

@app.route("/posts", methods=['GET'])
def get_posts():
    result = collection.find({})
    returnlist = []
    for i in result:
        returnlist.append(i)
    returndata = {"data": returnlist}
    
    return returndata

#Projects
@app.route("/projects", methods=['POST'])
def add_project():
    post = {"_id": request.json['_id'],"postname": request.json['title'],"thumbnailLocation": request.json['thumbnailURL']}
    collectionProj.insert_one(post)
    print("Post successful!")
    return {"id":200}

@app.route("/projects", methods=['GET'])
def get_projects():
    result = collectionProj.find({})
    returnlist = []
    for i in result:
        returnlist.append(i)
    returndata = {"data": returnlist}
    
    return returndata


@app.route("/projects/progress", methods=['POST'])
def add_progress():
    post = {"_id": request.json['_id'],"postname": request.json['title'],"projectTitle": request.json['projectTitle'],"thumbnailLocation": request.json['thumbnailURL'],"content": request.json['body'],"authorName": request.json['author']}
    collectionProgress.insert_one(post)
    print("Post successful")
    return {"id":200}

#Suggestions
@app.route("/suggestions", methods=['GET'])
def recieve_suggestions():
    result = collectionSuggestions.find({})
    returnlist = []
    for i in result:
        returnlist.append(i)
    returndata = {"data": returnlist}
    
    return returndata

@app.route("/suggestions", methods=['POST'])
def send_suggestions():
    idname = request.json['id']
    name = request.json['name']
    suggestion = request.json['suggestion']
    email = request.json['email']

    post = {"_id":idname, "name":name, "suggestion":suggestion, "email":email}
    collectionSuggestions.insert_one(post)
    print("Post successful")

    #automated email send
    msg = MIMEText('Name: ' + name + "\nSuggestion: " + suggestion + "\nE-mail: " + email)
    msg['Subject'] = "New suggestion from WolfDaily!"
    msg['From']    = "foo@"+ mailgun_user +".mailgun.org"
    msg['To']      = email

    s = smtplib.SMTP('smtp.mailgun.org', 587)

    s.login('postmaster@' + mailgun_user + '.mailgun.org', mailgun_pass)
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()
    return {"id":200}

if __name__ == "__main__":
    app.run(debug=True)