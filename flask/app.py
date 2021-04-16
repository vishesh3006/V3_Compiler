from flask import Flask
from flask import render_template, redirect, url_for, request,jsonify

app = Flask(__name__, template_folder='template')

@app.route("/", methods = ["GET", "POST"])
def home():
    return render_template('index.html')

if __name__ == "__main__" :
    app.debug = True
    app.run()