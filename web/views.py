from flask import Blueprint, request, jsonify

import pymongo


blue = Blueprint('first', __name__)


@blue.route('/getteam/', methods=['GET'])
def getteam():
    if request.method == 'GET':
        team_name = request.args.get('team_name')
        match_time = request.args.get('match_time')
        if team_name and match_time:
            db = pymongo.MongoClient('mongodb://139.196.102.231')
            result = db.ingsoccer.nba.find_one({'team_name': team_name, 'match_time': match_time})
            res = {'team_name': result['team_name'], 'match_time': result['match_time'],
                   'lineup_players': result['lineup_players'], 'injure_players': result['injure_players']}
            return jsonify(res)
        else:
            res = {'code': '000990', 'msg': '参数错误', 'data': ''}
            return jsonify(res)
