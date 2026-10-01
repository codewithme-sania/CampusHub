from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_connection, create_tables


app = Flask(__name__)
CORS(app)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def is_valid_email(email):
    return (
        "@" in email
        and "." in email.split("@")[-1]
        and " " not in email
    )


def is_valid_url(url):
    if not url:
        return True

    return (
        url.startswith("http://")
        or url.startswith("https://")
    )


# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "project": "CampusHub",
        "message": "CampusHub backend is running!",
        "status": "success"
    })


# =========================================================
# API TEST
# =========================================================

@app.route("/api/test", methods=["GET"])
def api_test():

    return jsonify({
        "project": "CampusHub",
        "message": "CampusHub API is working!",
        "status": "success"
    })


# =========================================================
# SIGNUP
# =========================================================

@app.route("/api/signup", methods=["POST"])
def signup():

    data = request.get_json() or {}

    name = clean(data.get("name"))
    email = clean(data.get("email")).lower()
    college = clean(data.get("college"))
    password = clean(data.get("password"))

    if not name:
        return jsonify({
            "success": False,
            "message": "Name is required."
        }), 400

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400

    if not college:
        return jsonify({
            "success": False,
            "message": "College is required."
        }), 400

    if not password:
        return jsonify({
            "success": False,
            "message": "Password is required."
        }), 400

    if len(name) < 2:
        return jsonify({
            "success": False,
            "message": "Name must contain at least 2 characters."
        }), 400

    if not is_valid_email(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 6 characters."
        }), 400

    connection = get_connection()

    try:

        existing_user = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:

            return jsonify({
                "success": False,
                "message": "Email already registered."
            }), 409

        hashed_password = generate_password_hash(password)

        cursor = connection.execute("""
            INSERT INTO users
            (name, email, college, password)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            college,
            hashed_password
        ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Account created successfully!",
            "user_id": cursor.lastrowid
        }), 201

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# LOGIN
# =========================================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json() or {}

    email = clean(data.get("email")).lower()
    password = clean(data.get("password"))

    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    if not is_valid_email(email):

        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    connection = get_connection()

    try:

        user = connection.execute("""
            SELECT
                id,
                name,
                email,
                college,
                password,
                branch,
                year,
                skills
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        if not user:

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
                "college": user["college"],
                "branch": user["branch"],
                "year": user["year"],
                "skills": user["skills"]
            }
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# GET PROFILE
# =========================================================

@app.route("/api/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):

    connection = get_connection()

    try:

        user = connection.execute("""
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
        """, (user_id,)).fetchone()

        if not user:

            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        return jsonify({
            "success": True,
            "user": dict(user)
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# UPDATE PROFILE
# =========================================================

@app.route("/api/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):

    data = request.get_json() or {}

    name = clean(data.get("name"))
    college = clean(data.get("college"))
    branch = clean(data.get("branch"))
    year = clean(data.get("year"))
    skills = clean(data.get("skills"))

    if not name or not college:

        return jsonify({
            "success": False,
            "message": "Name and college are required."
        }), 400

    if len(name) < 2:

        return jsonify({
            "success": False,
            "message": "Name must contain at least 2 characters."
        }), 400

    connection = get_connection()

    try:

        user = connection.execute(
            "SELECT id FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:

            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        connection.execute("""
            UPDATE users
            SET
                name = ?,
                college = ?,
                branch = ?,
                year = ?,
                skills = ?
            WHERE id = ?
        """, (
            name,
            college,
            branch,
            year,
            skills,
            user_id
        ))

        connection.commit()

        updated_user = connection.execute("""
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
        """, (user_id,)).fetchone()

        return jsonify({
            "success": True,
            "message": "Profile updated successfully!",
            "user": dict(updated_user)
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# POST OPPORTUNITY
# =========================================================

@app.route("/api/opportunities", methods=["POST"])
def post_opportunity():

    data = request.get_json() or {}

    title = clean(data.get("title"))
    category = clean(data.get("category"))
    description = clean(data.get("description"))
    date = clean(data.get("date"))
    location = clean(data.get("location"))
    organizer = clean(data.get("organizer"))
    application_link = clean(data.get("application_link"))

    if not title:
        return jsonify({
            "success": False,
            "message": "Opportunity title is required."
        }), 400

    if not category:
        return jsonify({
            "success": False,
            "message": "Category is required."
        }), 400

    if not description:
        return jsonify({
            "success": False,
            "message": "Description is required."
        }), 400

    if not date:
        return jsonify({
            "success": False,
            "message": "Date is required."
        }), 400

    if not location:
        return jsonify({
            "success": False,
            "message": "Location is required."
        }), 400

    if not organizer:
        return jsonify({
            "success": False,
            "message": "Organizer is required."
        }), 400

    if application_link and not is_valid_url(application_link):

        return jsonify({
            "success": False,
            "message": "Application link must start with http:// or https://"
        }), 400

    connection = get_connection()

    try:

        cursor = connection.execute("""
            INSERT INTO opportunities
            (
                title,
                category,
                description,
                date,
                location,
                organizer,
                application_link
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            category,
            description,
            date,
            location,
            organizer,
            application_link
        ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Opportunity posted successfully!",
            "opportunity_id": cursor.lastrowid
        }), 201

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# GET ALL OPPORTUNITIES
# =========================================================

@app.route("/api/opportunities", methods=["GET"])
def get_opportunities():

    connection = get_connection()

    try:

        opportunities = connection.execute("""
            SELECT
                id,
                title,
                category,
                description,
                date,
                location,
                organizer,
                application_link
            FROM opportunities
            ORDER BY id DESC
        """).fetchall()

        return jsonify({
            "success": True,
            "opportunities": [
                dict(opportunity)
                for opportunity in opportunities
            ]
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# SAVE OPPORTUNITY
# =========================================================

@app.route("/api/bookmarks", methods=["POST"])
def save_opportunity():

    data = request.get_json() or {}

    user_id = data.get("user_id")
    opportunity_id = data.get("opportunity_id")

    if not user_id or not opportunity_id:

        return jsonify({
            "success": False,
            "message": "User ID and opportunity ID are required."
        }), 400

    connection = get_connection()

    try:

        user = connection.execute(
            "SELECT id FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:

            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        opportunity = connection.execute(
            "SELECT id FROM opportunities WHERE id = ?",
            (opportunity_id,)
        ).fetchone()

        if not opportunity:

            return jsonify({
                "success": False,
                "message": "Opportunity not found."
            }), 404

        existing = connection.execute("""
            SELECT id
            FROM saved_opportunities
            WHERE user_id = ?
            AND opportunity_id = ?
        """, (
            user_id,
            opportunity_id
        )).fetchone()

        if existing:

            return jsonify({
                "success": False,
                "message": "Opportunity already saved."
            }), 409

        connection.execute("""
            INSERT INTO saved_opportunities
            (user_id, opportunity_id)
            VALUES (?, ?)
        """, (
            user_id,
            opportunity_id
        ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Opportunity saved successfully!"
        }), 201

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# GET SAVED OPPORTUNITIES
# =========================================================

@app.route("/api/bookmarks/<int:user_id>", methods=["GET"])
def get_saved_opportunities(user_id):

    connection = get_connection()

    try:

        saved = connection.execute("""
            SELECT
                o.id,
                o.title,
                o.category,
                o.description,
                o.date,
                o.location,
                o.organizer,
                o.application_link
            FROM saved_opportunities s
            JOIN opportunities o
                ON s.opportunity_id = o.id
            WHERE s.user_id = ?
            ORDER BY s.id DESC
        """, (user_id,)).fetchall()

        return jsonify({
            "success": True,
            "opportunities": [
                dict(opportunity)
                for opportunity in saved
            ]
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# REMOVE BOOKMARK
# =========================================================

@app.route(
    "/api/bookmarks/<int:user_id>/<int:opportunity_id>",
    methods=["DELETE"]
)
def remove_bookmark(user_id, opportunity_id):

    connection = get_connection()

    try:

        result = connection.execute("""
            DELETE FROM saved_opportunities
            WHERE user_id = ?
            AND opportunity_id = ?
        """, (
            user_id,
            opportunity_id
        ))

        connection.commit()

        if result.rowcount == 0:

            return jsonify({
                "success": False,
                "message": "Saved opportunity not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Opportunity removed from saved."
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# CREATE EVENT
# =========================================================

@app.route("/api/events", methods=["POST"])
def create_event():

    data = request.get_json() or {}

    title = clean(data.get("title"))
    category = clean(data.get("category"))
    description = clean(data.get("description"))
    date = clean(data.get("date"))
    location = clean(data.get("location"))
    organizer = clean(data.get("organizer"))
    registration_link = clean(data.get("registration_link"))

    if not title:

        return jsonify({
            "success": False,
            "message": "Event title is required."
        }), 400

    if not category:

        return jsonify({
            "success": False,
            "message": "Event category is required."
        }), 400

    if not description:

        return jsonify({
            "success": False,
            "message": "Event description is required."
        }), 400

    if not date:

        return jsonify({
            "success": False,
            "message": "Event date is required."
        }), 400

    if not location:

        return jsonify({
            "success": False,
            "message": "Event location is required."
        }), 400

    if not organizer:

        return jsonify({
            "success": False,
            "message": "Event organizer is required."
        }), 400

    if registration_link and not is_valid_url(registration_link):

        return jsonify({
            "success": False,
            "message": "Registration link must start with http:// or https://"
        }), 400

    connection = get_connection()

    try:

        cursor = connection.execute("""
            INSERT INTO events
            (
                title,
                category,
                description,
                date,
                location,
                organizer,
                registration_link
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            category,
            description,
            date,
            location,
            organizer,
            registration_link
        ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Event created successfully!",
            "event_id": cursor.lastrowid
        }), 201

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# GET ALL EVENTS
# =========================================================

@app.route("/api/events", methods=["GET"])
def get_events():

    connection = get_connection()

    try:

        events = connection.execute("""
            SELECT
                id,
                title,
                category,
                description,
                date,
                location,
                organizer,
                registration_link
            FROM events
            ORDER BY id DESC
        """).fetchall()

        return jsonify({
            "success": True,
            "events": [
                dict(event)
                for event in events
            ]
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        connection.close()


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    create_tables()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )

