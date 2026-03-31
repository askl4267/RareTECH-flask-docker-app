from flask import Flask, request, jsonify
import pymysql
 
app = Flask(__name__)


def get_connection():
    return pymysql.connect(
        host="db",
        user="flaskuser",
        password="flaskpass",
        database="flaskdb",
        cursorclass=pymysql.cursors.DictCursor,
    )
 
@app.route("/")
def hello():
    return "Hello Docker Flask + MySQL"
 
@app.route("/db")
def display_db_version():
    """ SQLのバージョンを表示する """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            result = cursor.fetchone()
    finally:
        conn.close()
 
    return f"MySQL Version: {result}"

@app.route("/init")
def init_table():
    """ users テーブルの初期化 """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL
                )
            """)
        conn.commit()
    finally:
        conn.close()

    return jsonify({"info": "テーブルの作成が完了しました"}), 200

@app.route("/users", methods=["GET", "POST"])
def get_users():
    """ users テーブルからデータを取得する """
    conn = get_connection()
    try:
        """ GET メソッドの場合、全データの一覧を取得する """
        if request.method == "GET":
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users ORDER BY id")
                users = cursor.fetchall()
            return jsonify(users)

        """ POST　メソッドの場合、ボディに含まれるIDに一致するデータを取得する """
        data = request.get_json()

        if not data:
            return jsonify({"error": "リクエストボディが空です"}), 400

        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "name は必須です"}), 400

        clean_name = name.strip()

        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (name) VALUES (%s)", (clean_name,))
            conn.commit()
            name_id = cursor.lastrowid

        return jsonify({"info": f"{clean_name}を追加しました。 idは、{name_id}です。"}), 201
    finally:
        conn.close()
 
if __name__ == "__main__":
    app.run(host="0.0.0.0")
