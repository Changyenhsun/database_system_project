from flask import Flask, render_template, request, jsonify
import pymysql
import random

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

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']

        # 安全地擷取使用者選擇的 genre ID（過濾掉 default）
        happy_genres = [int(g) for g in [request.form.get(f'happy{i}') for i in range(1, 4)] if g and g != 'default']
        mad_genres = [int(g) for g in [request.form.get(f'mad{i}') for i in range(1, 4)] if g and g != 'default']
        sorrowful_genres = [int(g) for g in [request.form.get(f'sorrowful{i}') for i in range(1, 4)] if g and g != 'default']

        recommendations = {
            'Happy': get_recommendations(happy_genres, [3, 3, 4]),
            'Angry': get_recommendations(mad_genres, [3, 3, 4]),
            'Sad': get_recommendations(sorrowful_genres, [3, 3, 4])
        }

        return render_template('recommend.html', username=username, recommendations=recommendations)

    return render_template('user.html', genres=genre_list)


@app.route('/search', methods=['GET', 'POST'])
def complex_search():
    if request.method == 'POST':
        genre = request.form.get('genre')
        director = request.form.get('director')
        actor = request.form.get('actor')
        # 根據條件進行 SQL 搜尋（可擴充）
        # 回傳查詢結果頁（例如 search_result.html）
        return f"你選了：類型 {genre}，導演 {director}，演員 {actor}"
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
