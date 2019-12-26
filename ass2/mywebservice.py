from flask import Flask
from flask import request
from ass2 import mybackend as db
app = Flask(__name__)

'''
this class represents a web-server for biking route information using the business logic in the backend. 
We receive parameters in GET requests and send them on to be analyzed by the backend. The answers will
be sent back.
'''


'''
:param startlocation is the place where the user is right now and where the start point is
:param timeduration is time he is willing to ride at this time. in minutes
:parm k - number of wanted results to choose from.

:return 

'''
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

'''
runs the server on port=5000
'''
if __name__ == '__main__':
    print("server on 5000")
    app.run(port=int("5000"))