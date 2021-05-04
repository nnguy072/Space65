from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from riotwatcher import LolWatcher, ApiError

app = Flask(__name__, instance_relative_config=True)
#app.config.from_object('config')
app.config.from_pyfile('config.py')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

lol_watcher = LolWatcher(app.config["RIOT_API_KEY"])
my_region = 'na1'

@app.route('/')
@cross_origin()
def hello_world():
  return 'Hello, World!'

@app.route('/test', methods=['POST'])
@cross_origin()
def hello_world_test():
  return jsonify(request.json)

@app.route('/my_summoner', methods=['GET'])
@cross_origin()
def get_summoner_info():
  summoner_name = request.args.get("summonerName")
  me = lol_watcher.summoner.by_name(my_region, summoner_name)
  return me
