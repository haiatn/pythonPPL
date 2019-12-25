from flask import Flask
from flask import request
from ass2 import mybackend as db
app = Flask(__name__)

@app.route('/', methods=["GET"])
def querySearch():
    startlocation = request.args.get('startlocation')
    timeduration = request.args.get('timeduration')
    k = request.args.get('k')
    error = db.checkUserInput(startlocation,timeduration,k)
    if error == None:
        resultList = db.Database().getRecommendations(startlocation, timeduration, k)
        if len(resultList) == 0:
            return "no results found"
        else:
            return str([x[0] for x in resultList])
    else:
        return error


if __name__ == '__main__':
    print("server on 5000")
    app.run(port=int("5000"))