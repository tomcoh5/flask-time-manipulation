import datetime
from flask import Flask
import os.path
import datetime
app = Flask(__name__)
time_file = "/mydata/time.txt"


@app.route("/")
def main_page():
    if os.path.exists(time_file):
        with open(time_file, 'r') as f:
            amount_of_lines = len(f.readlines())
            seconds_to_sub = amount_of_lines * 5
            time_sub = datetime.datetime.now() - datetime.timedelta(seconds=seconds_to_sub)
            return str(time_sub)
    else:
        return str(datetime.datetime.now())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
