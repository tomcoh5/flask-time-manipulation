from flask import Flask , render_template
import datetime
import os 
app = Flask(__name__)
list_of_num = []
time_file = "/mydata/time.txt"

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/", methods=['POST'])
def main_page_req():
    with open(time_file, 'a') as myfile:
        myfile.write(str("1") + "\n")
    return render_template('index.html');


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
