import executor_utils as eu
import json
import sys

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/build_and_run", methods=["POST"])
def build_and_run():
    data = json.loads(request.data)

    if 'code' not in data or 'lang' not in data:
        return 'You should provide both code and lang'

    code = data['code']
    lang = data['lang']

    print 'API got called with code: %s in %s' % (code, lang)

    result = eu.build_and_run(code, lang)
    return jsonify(result)

if __name__ == "__main__":
    port = int(sys.argv[1])

    # debug=True will restart when there's code change
    eu.load_image()
    app.run(port=port) #, debug=True, threaded=True
