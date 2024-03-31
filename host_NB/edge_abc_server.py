from flask import Flask
import requests
import os

app = Flask(__name__)

@app.route('/')
def get_data():

    if not os.path.exists("data.txt"):     
        url = "http://11.11.11.11:1234/get_data"
        download_file(url, "data.txt")

    with open("data.txt", 'r') as file:
        content = file.read()

    return content

def download_file(url, filename):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
            print("File downloaded successfully as", filename)
        else:
            print("Failed to download file. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", str(e))



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
