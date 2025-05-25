from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# 讀取所有電影類型
genre_df = pd.read_csv("Genre.csv")
genre_list = genre_df["genre"].dropna().unique().tolist()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        happy_genres = [request.form.get(f'happy{i}', 'default') for i in range(1, 4)]
        mad_genres = [request.form.get(f'mad{i}', 'default') for i in range(1, 4)]
        sorrowful_genres = [request.form.get(f'sorrowful{i}', 'default') for i in range(1, 4)]

        return f"""<h2>歡迎 {username}！</h2>
                   <p>你在 Happy 情緒時想看：{happy_genres}</p>
                   <p>你在 Mad 情緒時想看：{mad_genres}</p>
                   <p>你在 Sorrowful 情緒時想看：{sorrowful_genres}</p>"""

    return render_template('user.html', genres=genre_list)

if __name__ == '__main__':
    app.run(debug=True)
