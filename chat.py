from flask import Blueprint, jsonify, request
from database import (
    get_all_students,
    get_student_by_id,
    get_students_by_major,
    get_students_by_city,
    get_top_students
)

chat_bp = Blueprint("chat", __name__)


# ─────────────────────────────────────────
# REST ENDPOINTS
# ─────────────────────────────────────────

@chat_bp.route("/students", methods=["GET"])
def all_students():
    data = get_all_students()
    return jsonify({"total": len(data), "students": data}), 200


@chat_bp.route("/students/<int:student_id>", methods=["GET"])
def student_by_id(student_id):
    student = get_student_by_id(student_id)
    if student:
        return jsonify(student), 200
    return jsonify({"error": "Student not found"}), 404


@chat_bp.route("/students/major/<string:major>", methods=["GET"])
def students_by_major(major):
    data = get_students_by_major(major)
    return jsonify({"major": major, "total": len(data), "students": data}), 200


@chat_bp.route("/students/city/<string:city>", methods=["GET"])
def students_by_city(city):
    data = get_students_by_city(city)
    return jsonify({"city": city, "total": len(data), "students": data}), 200


@chat_bp.route("/students/top/<int:limit>", methods=["GET"])
def top_students(limit):
    data = get_top_students(limit)
    return jsonify({"top": limit, "students": data}), 200


# ─────────────────────────────────────────
# REALTIME CHATBOT ENDPOINT
# ─────────────────────────────────────────

@chat_bp.route("/chat", methods=["POST"])
def chat():
    body = request.get_json()

    if not body or "message" not in body:
        return jsonify({"error": "Please send a JSON body with a 'message' field"}), 400

    user_message = body["message"].lower().strip()

    # Intent: total count
    if any(word in user_message for word in ["how many students", "total students", "count students", "number of students"]):
        data = get_all_students()
        return jsonify({
            "user": body["message"],
            "bot": f"There are a total of {len(data)} students enrolled."
        }), 200

    # Intent: top N students
    elif "top" in user_message and ("student" in user_message or "gpa" in user_message):
        numbers = [int(s) for s in user_message.split() if s.isdigit()]
        limit = numbers[0] if numbers else 3
        data = get_top_students(limit)
        result = "\n".join([
            f"{i+1}. {s['FirstName']} {s['LastName']} - GPA: {s['GPA']} ({s['Major']})"
            for i, s in enumerate(data)
        ])
        return jsonify({
            "user": body["message"],
            "bot": f"Top {limit} students by GPA:\n{result}",
            "data": data
        }), 200

    # Intent: highest GPA
    elif any(word in user_message for word in ["highest gpa", "best gpa", "topper", "top student", "rank 1", "first rank"]):
        data = get_top_students(1)
        s = data[0]
        return jsonify({
            "user": body["message"],
            "bot": f"The student with the highest GPA is {s['FirstName']} {s['LastName']} with a GPA of {s['GPA']} in {s['Major']}."
        }), 200

    # Intent: lowest GPA
    elif any(word in user_message for word in ["lowest gpa", "least gpa", "bottom student", "worst gpa"]):
        data = get_all_students()
        s = min(data, key=lambda x: x["GPA"])
        return jsonify({
            "user": body["message"],
            "bot": f"The student with the lowest GPA is {s['FirstName']} {s['LastName']} with a GPA of {s['GPA']} in {s['Major']}."
        }), 200

    # Intent: average GPA
    elif any(word in user_message for word in ["average gpa", "avg gpa", "mean gpa"]):
        data = get_all_students()
        avg = round(sum(s["GPA"] for s in data) / len(data), 2)
        return jsonify({
            "user": body["message"],
            "bot": f"The average GPA of all students is {avg}."
        }), 200

    # Intent: all students
    elif any(word in user_message for word in ["all students", "show students", "list students", "fetch students", "all data", "show all"]):
        data = get_all_students()
        result = "\n".join([
            f"{s['StudentID']}. {s['FirstName']} {s['LastName']} - {s['Major']} - GPA: {s['GPA']} - {s['City']}"
            for s in data
        ])
        return jsonify({
            "user": body["message"],
            "bot": f"Here are all {len(data)} students:\n{result}",
            "data": data
        }), 200

    # Intent: search by city
    elif "city" in user_message or any(city in user_message for city in ["new york", "chicago", "seattle", "austin", "miami", "boston", "denver", "san francisco", "atlanta", "portland"]):
        cities = ["new york", "chicago", "seattle", "austin", "miami", "boston", "denver", "san francisco", "atlanta", "portland"]
        matched_city = next((c for c in cities if c in user_message), None)
        if matched_city:
            data = get_students_by_city(matched_city)
            if data:
                result = "\n".join([f"- {s['FirstName']} {s['LastName']} - {s['Major']} - GPA: {s['GPA']}" for s in data])
                return jsonify({
                    "user": body["message"],
                    "bot": f"Found {len(data)} student(s) from {matched_city.title()}:\n{result}",
                    "data": data
                }), 200
            return jsonify({"user": body["message"], "bot": f"No students found from {matched_city.title()}."}), 200

    # Intent: search by major
    elif "major" in user_message or any(m in user_message for m in ["computer science", "mathematics", "physics", "biology", "engineering", "psychology", "history", "chemistry", "economics", "art"]):
        majors = ["computer science", "mathematics", "physics", "biology", "engineering", "psychology", "history", "chemistry", "economics", "art"]
        matched_major = next((m for m in majors if m in user_message), None)
        if matched_major:
            data = get_students_by_major(matched_major)
            if data:
                result = "\n".join([f"- {s['FirstName']} {s['LastName']} - GPA: {s['GPA']} - {s['City']}" for s in data])
                return jsonify({
                    "user": body["message"],
                    "bot": f"Found {len(data)} student(s) in {matched_major.title()}:\n{result}",
                    "data": data
                }), 200
            return jsonify({"user": body["message"], "bot": f"No students found in {matched_major.title()}."}), 200

    # Intent: find by student ID
    elif any(word in user_message for word in ["id", "find student", "search student", "student number"]):
        numbers = [int(s) for s in user_message.split() if s.isdigit()]
        if numbers:
            student = get_student_by_id(numbers[0])
            if student:
                return jsonify({
                    "user": body["message"],
                    "bot": f"Found: {student['FirstName']} {student['LastName']} | Major: {student['Major']} | GPA: {student['GPA']} | City: {student['City']} | Age: {student['Age']}",
                    "data": student
                }), 200
            return jsonify({"user": body["message"], "bot": f"No student found with ID {numbers[0]}."}), 404
        return jsonify({"user": body["message"], "bot": "Please provide a student ID. Example: 'Find student with ID 3'"}), 200

    # Intent: GPA above threshold
    elif "above" in user_message and "gpa" in user_message:
        numbers = [float(s) for s in user_message.split() if s.replace('.', '', 1).isdigit()]
        if numbers:
            threshold = numbers[0]
            data = get_all_students()
            filtered = [s for s in data if s["GPA"] >= threshold]
            if filtered:
                result = "\n".join([f"- {s['FirstName']} {s['LastName']} - GPA: {s['GPA']}" for s in filtered])
                return jsonify({
                    "user": body["message"],
                    "bot": f"Found {len(filtered)} student(s) with GPA above {threshold}:\n{result}",
                    "data": filtered
                }), 200
            return jsonify({"user": body["message"], "bot": f"No students found with GPA above {threshold}."}), 200

    # Intent: GPA below threshold
    elif "below" in user_message and "gpa" in user_message:
        numbers = [float(s) for s in user_message.split() if s.replace('.', '', 1).isdigit()]
        if numbers:
            threshold = numbers[0]
            data = get_all_students()
            filtered = [s for s in data if s["GPA"] <= threshold]
            if filtered:
                result = "\n".join([f"- {s['FirstName']} {s['LastName']} - GPA: {s['GPA']}" for s in filtered])
                return jsonify({
                    "user": body["message"],
                    "bot": f"Found {len(filtered)} student(s) with GPA below {threshold}:\n{result}",
                    "data": filtered
                }), 200
            return jsonify({"user": body["message"], "bot": f"No students found with GPA below {threshold}."}), 200

    # Intent: hello/hi/help
    elif any(word in user_message for word in ["hi", "hello", "hey", "help"]):
        return jsonify({
            "user": body["message"],
            "bot": (
                "Hello! I am your Student Database Chatbot. Here is what I can help you with:\n\n"
                "- 'How many students are there?'\n"
                "- 'Show all students'\n"
                "- 'Top 3 students by GPA'\n"
                "- 'Who has the highest GPA?'\n"
                "- 'Who has the lowest GPA?'\n"
                "- 'What is the average GPA?'\n"
                "- 'Students from Seattle'\n"
                "- 'Students in Physics'\n"
                "- 'Find student with ID 3'\n"
                "- 'Students with GPA above 3.5'\n"
                "- 'Students with GPA below 3.3'"
            )
        }), 200

    # Default
    return jsonify({
        "user": body["message"],
        "bot": (
            "I did not understand that. Try asking:\n"
            "- 'How many students are there?'\n"
            "- 'Top 3 students by GPA'\n"
            "- 'Who has the highest GPA?'\n"
            "- 'Average GPA'\n"
            "- 'Students from Boston'\n"
            "- 'Students in Chemistry'\n"
            "- 'Students with GPA above 3.5'\n"
            "- 'Find student with ID 2'"
        )
    }), 200