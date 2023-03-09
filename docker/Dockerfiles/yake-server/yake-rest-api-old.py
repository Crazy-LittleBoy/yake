"""
Credits @arianpasquali
https://gist.githubusercontent.com/arianpasquali/16b2b0ab2095ee35dbede4dd2f4f8520/raw/ba4ea7da0d958fc4b1b2e694f45f17cc71d8238d/yake_rest_api.py

The simple example serving YAKE as a rest api.

instructions:

 pip install flasgger
 pip install git+https://github.com/LIAAD/yake

 python yake_rest_api.py

open http://127.0.0.1:5000/apidocs/
"""

from flasgger import Swagger
from flask import Flask, jsonify, request

try:
    import simplejson as json
except ImportError:
    import json
try:
    from http import HTTPStatus
except ImportError:
    import httplib as HTTPStatus

import yake

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Yake API Explorer',
    'uiversion': 3
}
swagger = Swagger(app)


@swagger.validate('content')
@app.route('/yake/', methods=['POST'])
def handle_yake():
    try:
        assert request.json["text"], "Invalid text"
        assert len(request.json["language"]) == 2, "Invalid language code"
        assert int(request.json["max_ngram_size"]), "Invalid max_ngram_size, Suggested max_ngram_size setting of 1 or 2 or 3"
        assert int(request.json["number_of_keywords"]), "Invalid number_of_keywords"
        assert int(request.json["windows_size"]), "Invalid windows_size, Suggested windows_size setting of 1 or 2"

        text = request.json["text"]
        language = request.json["language"]
        max_ngram_size = int(request.json["max_ngram_size"])
        number_of_keywords = int(request.json["number_of_keywords"])
        windows_size = int(request.json["windows_size"])

        my_yake = yake.KeywordExtractor(lan=language,
                                        n=max_ngram_size,
                                        top=number_of_keywords,
                                        dedupLim=-1,
                                        windowsSize=windows_size
                                        )

        keywords = my_yake.extract_keywords(text)
        result = [{"keyword": x[0], "score": x[1]} for x in keywords]

        return jsonify(result), HTTPStatus.OK
    except IOError as e:
        return jsonify("Language not supported"), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify(str(e)), HTTPStatus.BAD_REQUEST





if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
