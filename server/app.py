from flask import Flask, render_template, request, jsonify, make_response, g
from urllib.parse import urlparse, parse_qs
from transcript_labelling import get_labelled_tscript
from mysql.connector import connect 
from dotenv import load_dotenv
import os 

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


app = Flask(__name__)

@app.route('/', methods=['GET'])
def root(): 
    return render_template('index.html')

@app.route('/api/v1/timestamps', methods=['GET'])
def api_search(): 
    print(request.data)
    url = request.args.get('link')
    # Parse the URL
    print(url)
    parsed_url = urlparse(url)

    # Get the query string part
    query_string = parsed_url.query  # 'term=flask&limit=10&tag=python&tag=web'

    # Parse the query string into a dictionary
    params = parse_qs(query_string)
    print(params)
    video_id = params['v'][0]

    conn = get_db()
    cursor = conn.cursor() 
    cursor.execute("SELECT pk FROM videos WHERE video_id = %s", (video_id,))
    video_tk = cursor.fetchone()
    
    label_timestamps = []

    if video_tk is not None:
        print("Video already exists in the database.")
        cursor.execute("SELECT start_time, label FROM labels WHERE video_fk = %s", (video_tk))
        segments = cursor.fetchall()
        label_timestamps = [{'timestamp': int(a[0]), 'label': int(a[1])} for a in segments]    
    else: 
        segments = get_labelled_tscript(video_id) 
        cursor.execute("INSERT INTO videos (video_id) VALUES (%s)", (video_id,))
        video_fk = cursor.lastrowid
        #sql = "INSERT INTO labels (start_time, transcript, video_fk, label) VALUES (%s, %s, %s, %s)"
        #cursor.executemany(sql, [(a['start'], a['text'], video_fk, a['label']) for a in segments])
        sql = "INSERT INTO labels (start_time, video_fk, label) VALUES (%s, %s, %s)"
        cursor.executemany(sql, [(a['start'], video_fk, a['label']) for a in segments])
        conn.commit()

        print("Video and labels inserted into the database.")
        label_timestamps = [{'timestamp': int(a['start']), 'label' : int(a['label'])} for a in segments]
    return jsonify(label_timestamps)

@app.route('/api/test', methods=['GET'])
def api_test(): 
    response = make_response(jsonify({"status": "success"}), 200)
    return response

def get_db():
    if 'db' not in g:
        g.db = connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 3306),
            user=os.getenv("DB_USER", "user"),
            password=os.getenv("DB_PASSWORD", "password"), 
            database=os.getenv("DB_NAME", "skippy_youtube_db")
            )
        
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()