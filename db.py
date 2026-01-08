import mysql.connector
import hashlib
import os


# -------------------------------
# DATABASE CONNECTION
# -------------------------------
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("mysql.railway.internal"),
        user=os.getenv("root"),
        password=os.getenv("IYcCdvsZiPjwdBCAwsGhAXKupuChRvnq"),
        database=os.getenv("railway"),
        port=int(os.getenv("3306"))
    )


# -------------------------------
# PASSWORD HASHING
# -------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# -------------------------------
# USER REGISTRATION
# -------------------------------
def register_user(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    query = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """

    try:
        cursor.execute(query, (username, email, hashed_pw))
        conn.commit()
        return True
    except:
        return False
    finally:
        cursor.close()
        conn.close()


# -------------------------------
# USER LOGIN
# -------------------------------
def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    hashed_pw = hash_password(password)

    query = """
    SELECT id, username, role
    FROM users
    WHERE email = %s AND password = %s
    """

    cursor.execute(query, (email, hashed_pw))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


# -------------------------------
# SAVE PREDICTION (USER-SPECIFIC)
# -------------------------------
def save_prediction(data, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO predictions
    (user_id, age, gender, education, job_title, industry, company_size,
     experience_years, predicted_salary)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        user_id,
        data['age'],
        data['gender'],
        data['education'],
        data['job_title'],
        data['industry'],
        data['company_size'],
        data['experience_years'],
        data['predicted_salary']
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()


# -------------------------------
# USER PREDICTION HISTORY
# -------------------------------
def get_prediction_history(user_id, limit=50):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        age,
        gender,
        education,
        job_title,
        industry,
        company_size,
        experience_years,
        predicted_salary,
        created_at
    FROM predictions
    WHERE user_id = %s
    ORDER BY created_at DESC
    LIMIT %s
    """

    cursor.execute(query, (user_id, limit))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


# -------------------------------
# ADMIN: ALL PREDICTIONS
# -------------------------------
def get_all_prediction_history(limit=1000):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        user_id,
        age,
        gender,
        education,
        job_title,
        industry,
        company_size,
        experience_years,
        predicted_salary,
        created_at
    FROM predictions
    ORDER BY created_at DESC
    LIMIT %s
    """

    cursor.execute(query, (limit,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
