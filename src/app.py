import json
from db import db, Courses, Users, Assignment
from flask import Flask, request


app = Flask(__name__)

db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code

# your routes here

@app.route("/")
@app.route("/api/courses/")
def get_courses():
    """returns all courses

    Returns:
        json: json of all courses
    """
    courses = [course.serialize() for course in Courses.query.all()]
    return success_response({"courses": courses})


@app.route("/api/courses/", methods= ["POST"])
def create_course():
    """endpoint for creating a course
    """
    body = json.loads(request.data)
    code = body.get("code")
    name = body.get("name")
    if code is None:
        return failure_response("Provide course code", 400)
    if name is None:
        return failure_response("Provide course name", 400)
    course = Courses(
        code = body.get("code"), 
        name = body.get("name")
    )
    db.session.add(course)
    db.session.commit()
    return success_response(course.serialize(), 201)


@app.route("/api/courses/<int:course_id>/")
def get_specific_course(course_id):
    """endpoint for getting specific course

    Args:
        course_id (int): id of the course to retrieve

    """
    course = Courses.query.filter_by(id = course_id).first()
    if course is None:
        return failure_response("Course not found")
    return success_response(course.serialize())


@app.route("/api/courses/<int:course_id>/", methods = ["DELETE"])
def delete_course(course_id):
    """endpoint for deleting specific course

    Args:
        course_id (int): id of the course to delete
    """
    course = Courses.query.filter_by(id = course_id).first()
    if course is None:
        return failure_response("Course not found")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())
    

@app.route("/api/users/", methods = ["POST"])
def create_user():
    """endpoint for creating user
    """
    body = json.loads(request.data)
    name = body.get("name"),
    netid = body.get("netid")
    if netid is None:
        return failure_response("Provide user netid", 400)
    if name is None:
        return failure_response("Provide user name", 400)
    user = Users(
        name = body.get("name"),
        netid = body.get("netid")
    )
    db.session.add(user)
    db.session.commit()
    return success_response(user.serialize(), 201)


@app.route("/api/users/<int:user_id>/")
def get_specific_user(user_id):
    """endpoint for getting specific user
    """
    user = Users.query.filter_by(id = user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.serialize())


@app.route("/api/courses/<int:id>/add/", methods = ["POST"])
def add_user_course(id):
    """endpoint for adding user to course

    Args:
        id (int): course id
    """
    course = Courses.query.filter_by(id = id).first()
    if course is None:
        return failure_response("Course not found")
    body = json.loads(request.data)
    user_id = body.get("user_id")
    user = Users.query.filter_by(id = user_id).first()
    if user is None:
        return failure_response("User not found")
    type = body.get("type")
    if type is None:
        return failure_response("Provide type of user", 400)
    if type == "student":
        course.students.append(user)
    elif type == "instructor":
        course.instructors.append(user)
    db.session.commit()
    return success_response(course.serialize())
        

@app.route("/api/courses/<int:id>/assignment/", methods = ["POST"])
def add_assignment(id):
    """endpoint for adding a course assignment

    Args:
        id (int): course id
    """
    course = Courses.query.filter_by(id = id).first()
    if course is None:
        return failure_response("Course not found")
    body = json.loads(request.data)
    title = body.get("title")
    due_date = body.get("due_date")
    if title is None:
        return failure_response("Provide title for assignment", 400)
    if due_date is None:
        return failure_response("Provide due date for assignment", 400)
    assignment = Assignment(
        title = title,
        due_date = due_date, 
        course_id = id
    )
    db.session.add(assignment)
    db.session.commit()
    return success_response(assignment.serialize(), 201)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
