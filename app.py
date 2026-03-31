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

@app.route("/users", methods=["GET"])
def get_users():
    """ users テーブルから全データを取得する """
    conn = get_connection()
    try:
        if request.method == "GET":
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users ORDER BY id")
                users = cursor.fetchall()
            return jsonify(users)
    finally:
        conn.close()

@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    """ 特定のIDのユーザー情報を取得する """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
            user = cursor.fetchone()
        return jsonify(user)
    finally:
        conn.close()

@app.route("/users", methods=["POST"])
def add_user():
    """ ユーザーのデータを追加する """
    conn = get_connection()
    try:
        name = request.form.get("name")

        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "name は必須です"}), 400

        clean_name = name.strip()

        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (name) VALUES (%s)", (clean_name,))
            conn.commit()
            name_id = cursor.lastrowid

        return jsonify({"info": f"{clean_name}を追加しました。 idは、{name_id}です"}), 201
    finally:
        conn.close()

@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    """ 特定のIDのユーザーを削除する """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (id,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"error": f"id={id} のユーザーは存在しません"}), 404

        return jsonify({"info": f"id={id} のユーザーを削除しました"}), 200
    
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
