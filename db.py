import os
import pymysql

# MySQL/MariaDB 연결 설정
db_config = {
    "host": os.environ.get("DB_HOST", "db"),
    "user": os.environ.get("DB_USER", "user"),
    "password": os.environ.get("DB_PASSWORD", "password"),
    "database": os.environ.get("DB_DATABASE", "mariadb"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "charset": "utf8mb4"
}

# ✅ MySQL 연결 함수 (데이터베이스 연결만 수행)
def get_connection():
    try:
        connection = pymysql.connect(**db_config)
        print("✅ MariaDB 연결 성공!")
        return connection
    except Exception as e:
        print(f"❌ MariaDB 연결 오류 발생: {e}")
        return None


def create_users_table():
    """ users 테이블을 생성하는 함수 """
    conn = get_connection()
    if conn is None:
        print("❌ 데이터베이스 연결 실패! 테이블을 생성할 수 없습니다.")
        return
    
    try:
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50),
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            high_score INT DEFAULT 0
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ users 테이블 생성 완료!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 테이블 생성 오류 발생: {e}")


def insert_user(username, email):
    """ users 테이블에 사용자 추가하는 함수 """
    conn = get_connection()
    if conn is None:
        print("❌ 데이터베이스 연결 실패! 데이터를 삽입할 수 없습니다.")
        return
    
    try:
        cursor = conn.cursor()
        insert_query = "INSERT INTO users (username, email) VALUES (%s, %s)"
        cursor.execute(insert_query, (username, email))
        conn.commit()
        print(f"✅ 사용자 추가 완료: {username}, {email}")

        cursor.close()
        conn.close()

    except pymysql.IntegrityError:
        print("⚠ 이미 존재하는 이메일입니다.")
    except Exception as e:
        print(f"❌ 데이터 삽입 오류 발생: {e}")
