from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from db import get_connection
import random

app = Flask(__name__, template_folder="templates")
app.secret_key = "supersecretkey"

@app.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    if not email or not username or not password:
        return jsonify({"success": False, "message": "모든 필드를 입력하세요."}), 400

    conn = get_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "이미 등록된 이메일입니다."}), 400
        cursor.execute(
            "INSERT INTO users (email, username, password, high_score) VALUES (%s, %s, %s, 0)",
            (email, username, password)
        )
        conn.commit()
        return jsonify({"success": True, "message": "회원가입 성공!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/user/login", methods=["POST"])
def login():
    data = request.form
    email = data.get("email")
    password = data.get("password")

    conn = get_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        if user:
            session["username"] = user[0]
            return jsonify({"success": True, "redirect": url_for("game_page")}), 200
        else:
            return jsonify({"success": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login_page"))

@app.route("/game")
def game_page():
    if "username" in session:
        return render_template("game.html")
    return redirect(url_for("login_page"))

@app.route("/start_game", methods=["POST"])
def start_game():
    return jsonify({"success": True, "redirect": url_for("game_page")})

@app.route("/game_data")
def game_data():
    return jsonify({"food": {"x": random.randint(0, 29) * 20, "y": random.randint(0, 29) * 20}})

@app.route("/get_high_score")
def get_high_score():
    if "username" not in session:
        return jsonify({"high_score": 0})

    username = session["username"]
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT high_score FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        return jsonify({"high_score": result[0] if result else 0})
    except Exception:
        return jsonify({"high_score": 0})
    finally:
        cursor.close()
        conn.close()

@app.route("/update_high_score", methods=["POST"])
def update_high_score():
    if "username" not in session:
        return jsonify({"success": False}), 401

    username = session["username"]
    new_score = request.json.get("score")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT high_score FROM users WHERE username = %s", (username,))
        current = cursor.fetchone()
        if current is None:
            return jsonify({"success": False, "message": "User not found"}), 404
        if new_score > current[0]:
            cursor.execute("UPDATE users SET high_score = %s WHERE username = %s", (new_score, username))
            conn.commit()
        return jsonify({"success": True, "high_score": max(new_score, current[0])})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/ranking")
def ranking():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username, high_score FROM users ORDER BY high_score DESC LIMIT 10")
        rows = cursor.fetchall()
        return jsonify({"ranking": [{"username": row[0], "score": row[1]} for row in rows]})
    except Exception as e:
        return jsonify({"ranking": [], "error": str(e)})
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
