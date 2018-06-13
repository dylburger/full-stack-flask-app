from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


@app.before_first_request
def setup():
    db.create_all()


@app.route('/')
def homepage():
    students = Student.query.all()
    print(students)
    return render_template('index.html', students=students)


@app.route('/student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        try:
            name = request.form['student']
            student = Student(name=name)
            db.session.add(student)
            db.session.commit()
        except Exception as e:
            print(f'Exception when adding student: {str(e)}')

    return redirect(url_for('homepage'))


if __name__ == "__main__":
    app.run(debug=True)
