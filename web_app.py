from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", dest="port",
                    help="defines the Flask server port", type=int)
parser.add_argument("-v", "--verbose", dest="verbose",
                    help="adds verbosity", action="store_true")
parser.add_argument("-vv", "--mega-verbose", dest="vverbose",
                    help="adds maximum verbosity", action="store_true")
args = parser.parse_args().__dict__

if args["verbose"]:
    logging.basicConfig(level=logging.INFO)
elif args["vverbose"]:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.ERROR)

# Define main variables
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

port = 5000
if args["port"]:
    port = int(args["port"])

# Will store the previous data received
global current_data
current_data = None


@app.route("/api", methods=['POST'])
@cross_origin()
def receive_data():
    data = request.form.to_dict()
    global current_data

    source = data["source"]
    src = data["data"] if "data" in data.keys() else ""
    logging.debug(data)

    # request sent from the tchat
    if source == "tchat":
        if src.startswith("https://") and src.endswith(".gif"):
            current_data = data
            return "success"
        else:
            return "error"

    # request sent from the webpage
    elif source == "web":
        if current_data == None:
            return ""

        # add div attributes
        html = "<div"
        if 'audio' in current_data.keys() and len(current_data['audio']) > 0:
            html += f" audio='{current_data['audio']}'"
        html += "> "

        # add user
        if 'user' in current_data.keys() and len(current_data['user']) > 0:
            html += f" <h1>From {current_data['user']}</h1> "

        # add img
        html += f"<img src='{current_data['data']}' /> </div>"
        return html

# Web page redirections


@app.route("/")
@cross_origin()
def home():
    with open("web/index.html", "r") as file:
        return file.read()


@app.route("/jquery-3.6.3.min.js")
def jquery():
    return send_file("web/jquery-3.6.3.min.js")


@app.route("/<filename>.mp3")
def mp3(filename):
    return send_file(f"audio/{filename}.mp3")


# Run the web app
app.run(port=port)
