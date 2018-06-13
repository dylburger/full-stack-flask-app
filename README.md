## Minimal, Full Stack Flask app

This guide and associated code walk you through how to create a full stack (from SQLite to JavaScript) app with [Flask](http://flask.pocoo.org/).

### How all the pieces fit together

Understanding how all the pieces of a web application fit together can be the hardest part of learning how to create Flask apps. Let's talk about what connects to what, and how this all works from the perspective of the user.

The user sees a webpage. They have no idea what application (Flask) powers that. They have no idea that you're running SQL queries behind the scenes. This is a good thing. You can develop an app that's easy for "normal" users to use, abstracting the code / logic.

For the user to interact with the webpage, our app has to return HTML to the user's browser. So that the website looks pretty (good user experience), and so that we can develop charts and other interactivity on our page, our HTML will typically include CSS and JavaScript.

Our sample app lists all the students that are currently enrolled in our class. If we need to add a new student, we include an HTML `form` to let the user do that.

Our Flask app is at the core of all of this. This app is simple: we only have three "routes" (HTTP endpoints that we can retrieve or send data to), each of which performs a specific function:

* Our `/` endpoint - the homepage - returns our HTML page (which includes our CSS / JS) when the user makes a request to the website from a browser. Before we return the HTML, we query our database for any students in our class and format our HTML page to include the list of student names. We'll look at how this specific process works later.
* When a user adds a student and clicks the "Submit" button, our webpage makes a POST request to the `/student` endpoint of our Flask app. This endpoint takes form data passed to it - the student's name - and adds a new row to the table in our SQLite DB for that student. Then, we redirect the user back to the homepage. The student we added should appear in the list of students.
* We expose a `/data` endpoint that returns a count of students in our class.

### The Flask app

Let's cover just a couple of things about our Flask app first.

For the Flask app to work, we need to include the `Flask` class at a minimum. We also include a handful of other functions we'll use throughout our app

    from flask import Flask, jsonify, render_template, redirect, request, url_for

Since we're going to use SQLAlchemy to talk to our SQLite DB, we must also import the relevant class from there:

    from flask_sqlalchemy import SQLAlchemy

See the [`Flask-SQLAlchemy` Quickstart](http://flask-sqlalchemy.pocoo.org/2.3/quickstart/) for more information about that library.

After these imports, we're ready to create our app and configure our database connection:

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
    db = SQLAlchemy(app)

Our `app` object exposes an interface to add new routes to our Flask app, and to actually run the app. Our `db` object is the main interface to our SQLite DB.

Our database is simple. We only have a single table, which SQLAlchemy requires we model with a Python class:

    class Student(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255), nullable=False)

To make sure our database gets created if this is our first time running the app, we include this code:

    @app.before_first_request
    def setup():
        db.create_all()

`db.create_all()` will create the DB if it doesn't exist. If it does exist, we retain the existing data in the DB.

Our homepage route is relatively simple:

    @app.route('/')
    def homepage():
        students = Student.query.all()
        print(students)
        return render_template('index.html', students=students)

When users hit our site, `Student.query.all()` returns all records in our students table in our SQLite DB. We pass that to our HTML template, and `render_template()` formats the template, rendering our list of students. Functionally, `return` just returns this formatted template to the user's browser.

Our `/student` route retrieves the name of the student POSTed to the endpoint from the HTML form and adds a new row to our students table, redirecting the user to the homepage, which lists the new student among all students in the DB:

    if request.method == 'POST':
        try:
            name = request.form['student']
            student = Student(name=name)
            db.session.add(student)
            db.session.commit()
        except Exception as e:
            print(f'Exception when adding student: {str(e)}')

    return redirect(url_for('homepage'))

We include a small bit of exception handling in case we don't get any student name, have trouble connecting to the DB, etc.

Finally, our `/data` endpoint returns a count of students in our class:

    count = db.session.query(func.count(Student.id)).scalar()
    return jsonify({'count': count})

### The HTML template

By convention, HTML templates typically live in the `templates` directory. I want to focus on the `body` of the HTML here. Next, we'll discuss how to include CSS and JavaScript.

First, we want to list all the students in our class. Remember that we passed the list of students returned from our database query to the `render_template()` function in our Flask app:

    return render_template('index.html', students=students)

Flask then makes the `students` variable accessible in our HTML template using a templating language called "Jinja". Jinja extends basic HTML to allow us to:

* Reference the value of variables passed to the template
* Include conditional statements, for loops, and other control structures that allow us to conditionally render HTML, or render a list of items in our HTML.
* [Much, much more](http://jinja.pocoo.org/docs/2.10/)!

Since we want to render a list of students, for every student in our class, a `for` loop makes sense:

    <ul id="students">
    {% for student in students %}
        <li>{{ student.name }}</li>
    {% endfor %}
    </ul>

This renders an `li` element for every student in the list of students we passed to `render_template()` in our Flask code.

Conceptually, this should feel just like a Python `for` loop, even if the syntax looks weird. Practice the syntax and it will come with time.
    
Next, we provide a simple form that allows users to add new students to our class:

    <form method="POST" action="/student">
      <label for="student">Add new student:</label><input type="text" name="student">
      <input type="submit">
    </form>

The `name` attribute of our text `input` ("student") is important here. In the `/student` route of our Flask code, we reference `request.form['student']`. `request.form` is a Python dictionary that includes values corresponding to the value of each `input` in our `form`, keyed on the `name` attribute of each input.

Finally, we include an empty `span`, where we'll write the count of students in our class using JavaScript.

### Managing static assets (CSS, JS)

We need to style our HTML with CSS and include some JavaScript so that we can develop charts using Plotly. How do we tell Flask about these new static files?

[This reference](http://exploreflask.com/en/latest/static.html) reviews a couple of ways to manage these "static" assets. We'll walk through the easiest method below.

First, in the root of your project (where your `app.py` file lives), you'll need to make a `static` directory. This is included in this repo, but for new projects, run

    mkdir static

to create it. This is where you'll keep your CSS and JS.

How you keep your files ordered within this directory is up to personal preference. However, it's common to separate CSS and JavaScript into their own subdirectories. For new projects, just run

    cd static
    mkdir js css

Then, place your CSS and JavaScript files within those respective directories.

These files are in the `static` directory, but our HTML is in the `templates` directory. How do we reference these static assets from our HTML? Within the `head` tag in your HTML template, follow this convention:

    <head>
        <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/style.css') }}">
        <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    </head>

replacing the actual filename with the path to your file, within the `static` directory.

### The JavaScript

Our JavaScript uses a bit of D3 code to fetch the count of students from our `/data` endpoint, adding that count to the empty span in our HTML above.
