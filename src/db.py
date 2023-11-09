from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

student_assoc = db.Table("students_assoc", db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
    db.Column("users_id", db.Integer, db.ForeignKey("users.id"))
)

instructors_assoc = db.Table("instructors_assoc", db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
    db.Column("users_id", db.Integer, db.ForeignKey("users.id"))
)

class Courses(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    students = db.relationship("Users", secondary = student_assoc, back_populates = "courses")
    instructors = db.relationship("Users", secondary = instructors_assoc, back_populates = "courses_instructor") 
    assignments = db.relationship("Assignment", cascade = "delete")
    
    def __init__(self, **kwargs):
        self.code = kwargs.get("code")
        self.name = kwargs.get("name")
        
        
    def serialize(self):
        return{
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [assignment.simple_assignment_serialize() for assignment in self.assignments],
            "instructors": [instructor.simple_user_serialize() for instructor in self.instructors],
            "students": [student.simple_user_serialize() for student in self.students]
        }
        
    
    def simple_serialize(self):
        return{
            "id": self.id,
            "code": self.code,
            "name": self.name
        }
        

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    netid = db.Column(db.String, nullable = False)
    courses = db.relationship("Courses", secondary = student_assoc, back_populates = "students")
    courses_instructor = db.relationship("Courses", secondary = instructors_assoc, back_populates = "instructors")
    
    
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.netid = kwargs.get("netid")
        
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name, 
            "netid": self.netid,
            "courses": [course.simple_serialize() for course in self.courses or self.courses_instructor]
        }
        
    def simple_user_serialize(self):
        """
        serialize a users object without the courses field
        """
        return {
            "id": self.id,
            "name": self.name, 
            "netid": self.netid
        }


class Assignment(db.Model):
    __tablename__ = "assignment"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    due_date = db.Column(db.Integer, nullable = False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable = False)
    
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.due_date = kwargs.get("due_date")
        self.course_id = kwargs.get("course_id")

    def serialize(self):
        
        course = Courses.query.filter_by(id = self.course_id).first()
        
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
            "course": course.simple_serialize()
            
        }
        
    def simple_assignment_serialize(self):
        return {
            "id": self.id, 
            "title": self.title,
            "due_date": self.due_date
        }
