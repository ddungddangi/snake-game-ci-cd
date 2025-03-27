from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from db import get_connection
import random

app = Flask(__name__, template_folder="templates")
app.secret_key = "supersecretkey"

# ==================================
# ✅ 1. 회원가입 기능
# ==================================

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
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"success": False, "message": "이미 등록된 이메일입니다."}), 400

        cursor.execute(
            "INSERT INTO users (email, username, password, high_score) VALUES (%s, %s, %s, 0)",
            (email, username, password)
        )
        conn.commit()
        return jsonify({"success": True, "message": "회원가입 성공!"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================================
# ✅ 2. 로그인 기능
# ==================================

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
            session["user"] = user[0]
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
    session.pop("user", None)
    return redirect(url_for("login_page"))

# ==================================
# ✅ 3. 게임 페이지 렌더링
# ==================================

@app.route("/game")
def game_page():
    if "user" in session:
        return render_template("game.html")
    else:
        return redirect(url_for("login_page"))

@app.route("/start_game", methods=["POST"])
def start_game():
    return jsonify({"success": True, "redirect": url_for("game_page")})

@app.route("/game_data")
def game_data():
    food_position = {
        "x": random.randint(0, 29) * 20,
        "y": random.randint(0, 29) * 20
    }
    return jsonify({"food": food_position})

# ==================================
# ✅ 4. 점수 관련 기능
# ==================================

@app.route("/get_high_score")
def get_high_score():
    if "user" not in session:
        return jsonify({"high_score": 0})

    username = session["user"]
    conn = get_connection()
    if conn is None:
        return jsonify({"high_score": 0})

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT high_score FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        high_score = result[0] if result else 0
        return jsonify({"high_score": high_score})
    except Exception:
        return jsonify({"high_score": 0})
    finally:
        cursor.close()
        conn.close()

@app.route("/update_high_score", methods=["POST"])
def update_high_score():
    if "user" not in session:
        return jsonify({"success": False}), 401

    username = session["user"]
    data = request.json
    new_score = data["score"]

    conn = get_connection()
    if conn is None:
        return jsonify({"success": False, "message": "DB 연결 실패"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT high_score FROM users WHERE username = %s", (username,))
        current_high_score = cursor.fetchone()[0]

        if new_score > current_high_score:
            cursor.execute("UPDATE users SET high_score = %s WHERE username = %s", (new_score, username))
            conn.commit()

        return jsonify({"success": True, "high_score": max(new_score, current_high_score)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================================
# ✅ 5. 랭킹 기능 (Top 10)
# ==================================

@app.route("/ranking")
def ranking():
    conn = get_connection()
    if conn is None:
        return jsonify({"ranking": []})

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username, high_score FROM users ORDER BY high_score DESC LIMIT 10")
        rows = cursor.fetchall()
        ranking_data = [{"username": row[0], "score": row[1]} for row in rows]
        return jsonify({"ranking": ranking_data})
    except Exception as e:
        return jsonify({"ranking": [], "error": str(e)})
    finally:
        cursor.close()
        conn.close()

# ==================================
# ✅ 6. Flask 실행
# ==================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
