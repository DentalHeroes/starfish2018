from flask import Blueprint
from flask import jsonify
import alert

alertApi = Blueprint('alertApi', __name__)

@alertApi.route('/')
def index():
   return jsonify(alert.sendAlert());