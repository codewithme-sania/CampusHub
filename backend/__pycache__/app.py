from flask import Flask, jsonify, request
from flask_cors import CORS

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import get_connection, create_tables


app = Flask(__name__)
CORS(app)


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():
    return "CampusHub Backend is Running!"


# ==================================================
# API TEST
# ==================================================

@app.route("/api/test")
def api_test():
    return jsonify({
        "status": "success",
        "message": "CampusHub API is working!",
        "project": "CampusHub"
    })


# ==================================================
# SIGNUP
# ==================================================

@app.route("/api/signup", methods=["POST"])
def signup():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid request data."
        }), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    college = str(data.get("college", "")).strip()
    password = data.get("password", "")

    if not name or not email or not college or not password:
        return jsonify({
            "success": False,
            "message": "Please fill in all fields."
        }), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must be at least 8 characters."
        }), 400

    password_hash = generate_password_hash(password)

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO users
            (name, email, college, password)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                college,
                password_hash
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Registration successful!"
        }), 201

    except Exception as error:

        if "UNIQUE constraint failed: users.email" in str(error):

            return jsonify({
                "success": False,
                "message": "This email is already registered."
            }), 409

        app.logger.exception("Signup failed")

        return jsonify({
            "success": False,
            "message": "Something went wrong. Please try again."
        }), 500

    finally:

        connection.close()


# ==================================================
# LOGIN
# ==================================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid request data."
        }), 400

    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if not email or not isinstance(password, str) or not password:

        return jsonify({
            "success": False,
            "message": "Please enter your email and password."
        }), 400

    connection = get_connection()

    try:

        user = connection.execute(
            """
            SELECT
                id,
                name,
                email,
                college,
                branch,
                year,
                skills,
                password
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if user is None:

            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        if not check_password_hash(
            user["password"],
            password
        ):

            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        return jsonify({
            "success": True,
            "message": "Login successful!",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "college": user["college"] or "",
                "branch": user["branch"] or "",
                "year": user["year"] or "",
                "skills": user["skills"] or ""
            }
        }), 200

    except Exception:

        app.logger.exception("Login failed")

        return jsonify({
            "success": False,
            "message": "Something went wrong."
        }), 500

    finally:

        connection.close()


# ==================================================
# GET PROFILE
# ==================================================

@app.route("/api/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):

    connection = get_connection()

    try:

        user = connection.execute(
            """
            SELECT
                id,
                name,
                email,
                college,
                branch,
                year,
                skills
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        if user is None:

            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        return jsonify({
            "success": True,
            "profile": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "college": user["college"] or "",
                "branch": user["branch"] or "",
                "year": user["year"] or "",
                "skills": user["skills"] or ""
            }
        }), 200

    except Exception:

        app.logger.exception("Profile fetch failed")

        return jsonify({
            "success": False,
            "message": "Something went wrong."
        }), 500

    finally:

        connection.close()


# ==================================================
# UPDATE PROFILE
# ==================================================

@app.route("/api/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "success": False,
            "message": "Invalid request data."
        }), 400

    name = str(data.get("name", "")).strip()
    college = str(data.get("college", "")).strip()
    branch = str(data.get("branch", "")).strip()
    year = str(data.get("year", "")).strip()
    skills = str(data.get("skills", "")).strip()

    if not name:

        return jsonify({
            "success": False,
            "message": "Name cannot be empty."
        }), 400

    connection = get_connection()

    try:

        user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        if user is None:

            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        connection.execute(
            """
            UPDATE users
            SET
                name = ?,
                college = ?,
                branch = ?,
                year = ?,
                skills = ?
            WHERE id = ?
            """,
            (
                name,
                college,
                branch,
                year,
                skills,
                user_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Profile updated successfully!"
        }), 200

    except Exception:

        app.logger.exception("Profile update failed")

        return jsonify({
            "success": False,
            "message": "Something went wrong."
        }), 500

    finally:

        connection.close()


# ==================================================
# START FLASK SERVER
# ==================================================

if __name__ == "__main__":

    create_tables()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )