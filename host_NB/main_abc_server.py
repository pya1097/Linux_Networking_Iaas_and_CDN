from flask import Flask
import requests
import os

app = Flask(__name__)

@app.route('/')
def get_data():
    return "Hello world ABC"

@app.route('/get_data')
def send_file_data():
    with open('data.txt', 'r') as file:
            file_content = file.read()
    return file_content


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
