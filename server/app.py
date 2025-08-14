from flask import Flask, render_template, request, jsonify, make_response
from urllib.parse import urlparse, parse_qs
from transcript_labelling import get_labelled_tscript
#from flask_cors import CORS 

app = Flask(__name__)
#CORS(app) 

@app.route('/', methods=['GET'])
def root(): 
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def api_search(): 
    print(request.data)
    url = request.form.get('link')
    # Parse the URL
    parsed_url = urlparse(url)

    # Get the query string part
    query_string = parsed_url.query  # 'term=flask&limit=10&tag=python&tag=web'

    # Parse the query string into a dictionary
    params = parse_qs(query_string)
    print(params)
    video_id = params['v'][0]
    segments = get_labelled_tscript(video_id) 
    label_timestamps = [{'timestamp': int(a['start']), 'label' : int(a['label'])} for a in segments]
    return jsonify(label_timestamps)


@app.route('/api/test', methods=['GET'])
def api_test(): 
    response = make_response(jsonify({"status": "success"}), 200)
    #response.headers.add("Access-Control-Allow-Origin", "*")
    return response
