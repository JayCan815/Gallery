from flask import Flask, render_template, request,redirect,url_for,flash
from werkzeug.utils import secure_filename
from flask_json import FlaskJSON, json_response
from Bcon import GetDb
import bcrypt
import json
import jwt
import os
import urllib.request

UPLOAD_FOLDER = 'static/uploads/'
app = Flask(__name__)
FlaskJSON(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = "my secret"

ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])

global_db_con = GetDb()
JWT_TOKEN = None
JWT_Secret = None


with open("secret.txt", "r") as f:
    JWT_SECRET = f.read()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"]) 
def Index():
    images = os.listdir('static/uploads')
    return render_template("index.html", images = images)

@app.route("/loginauth", methods=["POST"])
def Login():

    
    cursor = global_db_con.cursor()
    cursor.execute("select username,password from users where username = '" + request.form["username"] + "';")
    
    res = cursor.fetchone()


    if res is None:
       return json_response(data={"message": "Username does not exist."},status='bad')
    else:

        pw = request.form["password"]
        saltedpw = bcrypt.hashpw(bytes(pw,"utf-8"),bcrypt.gensalt(10))
        

        if bcrypt.checkpw(bytes(request.form["password"],'utf-8'), bytes(res[1],'utf-8')) :
            global JWT_TOKEN
            JWT_TOKEN = jwt.encode({"user": res[0]}, JWT_SECRET, algorithm="HS256")
            return json_response(data={"jwt": JWT_TOKEN})
        else:
            return json_response(data = {"message": "Incorrect password."}, status='bad')

@app.route("/signup",methods=["POST"])
def signup():
    user =  request.form["username"]
    pw = request.form["password"]
    saltedpw = bcrypt.hashpw(bytes(pw, "utf-8"),bcrypt.gensalt(10))
    cur = global_db_con.cursor()
    cur.execute("INSERT INTO users (username,password) VALUES('"+ str(user) + "','" + saltedpw.decode("utf-8") + "');")
    global_db_con.commit()

    return json_response(data={"message": "Sign up complete."},status='good')

@app.route("/upload",methods=["POST"])
def upload():
    if 'file' not in request.files:
        flash("Invalid file format.")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash("No image selected")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('uploading.. file: ' + filename)
        flash('Upload success!')
        return redirect(url_for('Index'))
    else:
        flash('Invalid image format, only use png, jpg, jpeg, or gifs')
        return redirect(url_for('Index'))

@app.route('/displayall')
def display_all():
    
    basepath= f"static/uploads"
    dir = os.walk(basepath)
    img_list = []

    for path,subdirs,files in dir:
        for file in files:
            temp = joinPath(path +  '/', file)
            img_list.append(temp)
            return render_template('index.html',hists = img_list)
    


app.run(host='0.0.0.0',port=80)

