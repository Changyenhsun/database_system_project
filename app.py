from flask import Flask, render_template, request, jsonify, redirect, url_for
import pymysql


app = Flask(__name__)

# 資料庫連線設定
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='iris0904',
    database='drama_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# 撈出所有類型（ID + 名稱）
cursor = conn.cursor()
cursor.execute("SELECT GenreID, GenreName FROM Genre")
genre_list = cursor.fetchall()
latest_recommend_data = {}
# 預設類型對應表
default_genres = {
    'Happy': ['Comedy', 'Music', 'Family'],
    'Angry': ['Action', 'Thriller', 'Crime'],
    'Sad': ['Drama', 'Romance', 'Animation']
}
def get_default_ids(names):
    name_set = set(n.strip().lower() for n in names)
    return [g['GenreID'] for g in genre_list if g['GenreName'].strip().lower() in name_set]


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']

        # 取出使用者選的 genre ID（或使用預設）
        def extract_genres(prefix, default_names):
            ids = [int(g) for g in [request.form.get(f'{prefix}{i}') for i in range(1, 4)] if g and g != 'default']
            return ids if ids else get_default_ids(default_genres[default_names])

        happy_genres = extract_genres('happy', 'Happy')
        mad_genres = extract_genres('mad', 'Angry')
        sad_genres = extract_genres('sorrowful', 'Sad')

        # 將資訊 encode 成 URL query string
        global latest_recommend_data
        latest_recommend_data = {
            'username': username,
            'happy': ','.join(map(str, happy_genres)),
            'mad': ','.join(map(str, mad_genres)),
            'sad': ','.join(map(str, sad_genres))
        }

        return redirect(url_for('recommend_page'))

    # GET：載入 user.html
    happy_defaults = get_default_ids(default_genres['Happy'])
    angry_defaults = get_default_ids(default_genres['Angry'])
    sad_defaults = get_default_ids(default_genres['Sad'])

    return render_template('user.html',
                           genres=genre_list,
                           happy_defaults=happy_defaults,
                           angry_defaults=angry_defaults,
                           sad_defaults=sad_defaults)

@app.route('/recommend')
def recommend_page():
    if not latest_recommend_data:
        return redirect(url_for('login')) 
    
    username = request.args.get('username', '使用者')
    happy_ids = [int(x) for x in request.args.get('happy', '').split(',') if x.isdigit()]
    mad_ids = [int(x) for x in request.args.get('mad', '').split(',') if x.isdigit()]
    sad_ids = [int(x) for x in request.args.get('sad', '').split(',') if x.isdigit()]

    # 若沒有資料就用預設值（容錯）
    happy_ids = happy_ids or get_default_ids(default_genres['Happy'])
    mad_ids = mad_ids or get_default_ids(default_genres['Angry'])
    sad_ids = sad_ids or get_default_ids(default_genres['Sad'])

    happy_recommend = get_recommendations(happy_ids, [3, 3, 4])
    mad_recommend = get_recommendations(mad_ids, [3, 3, 4])
    sad_recommend = get_recommendations(sad_ids, [3, 3, 4])

    recommendations = {
        'Happy': happy_recommend,
        'Angry': mad_recommend,
        'Sad': sad_recommend
    }

    return render_template('recommend.html', username=username, recommendations=recommendations)

@app.route('/mylist')
def my_list_page():
    return render_template("mylist.html")

@app.route('/search', methods=['GET', 'POST'])
def complex_search():
    if request.method == 'POST':
        genre_id = request.form.get('genre')
        director_name = request.form.get('director')
        actor_name = request.form.get('actor')

        genre_id = int(genre_id) if genre_id and genre_id != 'default' else None
        director_name = director_name.strip() if director_name else None
        actor_name = actor_name.strip() if actor_name else None

        cursor = conn.cursor()

        genre_name = None
        if genre_id:
            cursor.execute("SELECT GenreName FROM Genre WHERE GenreID = %s", (genre_id,))
            genre_row = cursor.fetchone()
            genre_name = genre_row['GenreName'] if genre_row else None
            
        director_id = None
        if director_name:
            cursor.execute("SELECT DirectorID FROM Director WHERE DirectorName COLLATE utf8mb4_general_ci LIKE %s", (f"%{director_name.strip()}%",))
            result = cursor.fetchone()
            if result is not None:
                director_id = result['DirectorID']

        actor_id = None
        if actor_name:
            cursor.execute("SELECT ActorID FROM Actor WHERE ActorName COLLATE utf8mb4_general_ci LIKE %s", (f"%{actor_name.strip()}%",))
            result = cursor.fetchone()
            if result is not None:
                actor_id = result['ActorID']

        # print("使用者輸入條件：")
        # print("Genre ID:", genre_id)
        # print("Director ID:", director_id)
        # print("Actor ID:", actor_id)

        query = """
            SELECT DISTINCT D.Title
            FROM Drama D
            WHERE (%s IS NULL OR EXISTS (
                SELECT 1 FROM Drama_Genre DG
                WHERE DG.drama_id = D.DramaID AND DG.genre_id = %s
            ))
            AND (%s IS NULL OR EXISTS (
                SELECT 1 FROM Drama_Director DD
                WHERE DD.DramaID = D.DramaID AND DD.DirectorID = %s
            ))
            AND (%s IS NULL OR EXISTS (
                SELECT 1 FROM Drama_Actor DA
                WHERE DA.DramaID = D.DramaID AND DA.ActorID = %s
            ));
        """

        values = (genre_id, genre_id, director_id, director_id, actor_id, actor_id)

        cursor.execute(query, values)
        results = cursor.fetchall()

        return render_template('search_result.html', results=results, genre_name=genre_name)

    # GET 方法：載入 genre 下拉選單
    cursor = conn.cursor()
    cursor.execute("SELECT GenreID, GenreName FROM Genre")
    genre_list = cursor.fetchall()
    return render_template('search.html', genres=genre_list)

@app.route('/autocomplete/director')
def autocomplete_director():
    q = request.args.get('q', '')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT DirectorName FROM Director
        WHERE DirectorName LIKE %s
        LIMIT 10
    """, (q + '%',))
    result = [row['DirectorName'] for row in cursor.fetchall()]
    return jsonify(result)

@app.route('/autocomplete/actor')
def autocomplete_actor():
    q = request.args.get('q', '')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT ActorName FROM Actor
        WHERE ActorName LIKE %s
        LIMIT 10
    """, (q + '%',))
    result = [row['ActorName'] for row in cursor.fetchall()]
    return jsonify(result)

def get_recommendations(genre_ids, split):
    result = []
    cursor = conn.cursor()
    for genre_id, count in zip(genre_ids, split):
        cursor.execute("""
            SELECT Title, G.GenreName
            FROM Drama D
            JOIN Genre G ON D.GenreID = G.GenreID
            WHERE G.GenreID = %s
            ORDER BY RAND() LIMIT %s
        """, (genre_id, count))
        rows = cursor.fetchall()
        result.extend(rows)
    return result

if __name__ == '__main__':
    app.run(debug=True)
