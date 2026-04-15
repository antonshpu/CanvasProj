from flask import Flask, request, jsonify, session, render_template
import sqlite3

app = Flask(__name__)

app.secret_key = 'TimTimTimSahur'

course_codes_to_names = {
    "CSCA67": "Discrete Mathematics",
    "MATA22": "Linear Algebra I For Mathematical Sciences",
    "MATA37": "Calculus II For Mathematical Sciences",
    "CSCB20": "Introduction To Databases",
}

def compute_final_grades(node, student_row):
    name, max_points, children, pos, weight = node;
    if not children:##i.e it is a skill (HTML, CSS, ...)
        raw_score = student_row.get(name, 0);
        if(max_points == 0):
            return 0 ## no points for this skill
        return (raw_score / max_points) * weight
    else:##i.e. it is a category that contains skills
        total = 0;
        for child in children:
            total += compute_final_grades(child, student_row)
    return total;

@app.route('/')
@app.route('/main/<path:subpath>')
def catch_all(subpath=None):
    if not session.get('logged_in'):
        return render_template('login.html')
    current_courses = session.get('current_courses', {})
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password');
        if(password == "TimTimTimSahur"):
            session['logged_in'] = True;
            return render_template('main.html')
        return "wrong password, are you a hacker?!"
    else:
        return render_template("login.html")

@app.route('/api/courses')
def class_selector():
    current_courses = session.get('current_courses', {})
    return jsonify(current_courses) # we want to port these to JS for easy of use esp when sql..


@app.route('/api/add_course', methods=['POST'])
def add_course():
    data = request.get_json()
    course_code = data.get('course_code', '').strip().upper() # map this to a name

    #user_id = session.get('user_id') # not used atm

    if course_code not in course_codes_to_names: # error case
        return jsonify(["Course does not exist"])
    
    courses = session.get('current_courses', {})
    
    new_id = session.get('id_counter', 0) + 1
    session['id_counter'] = new_id

    str_v_id = str(new_id)
    courses[str_v_id] = {"code": course_code, "name": course_codes_to_names[course_code]}
    
    session['current_courses'] = courses
    
    return jsonify(["Succesful course creation"])

@app.route('/api/remove_course', methods=['POST'])
def remove_course():
    data = request.get_json()
    course_code = data.get('course_code', '').strip().upper() # map this to a name
    course_id = str(data.get('id'))

    #user_id = session.get('user_id') # not used atm
    
    courses = session.get('current_courses', {})

    popped = False

    if course_id in courses:
        courses.pop(course_id)
        popped = True
    
    session['current_courses'] = courses

    if popped:
        return jsonify(["Succesful course removal"])
    
    return jsonify(["Error in removing course"]), 404
    

@app.route('/api/select_course', methods=['GET', 'POST'])
def select_course():
    if (request.method == 'POST'):
        data = request.get_json()
        course_code = data.get('course_code', '').strip().upper()
        course_id = data.get('id')
        
        session['course_editing'] = course_code
        session['course_editing_id'] = course_id
    
        return jsonify(["Successful course selection"])
    else:
        current = session.get('course_editing', 'NONE')
        current_id = session.get('course_editing_id', '-1')
        return jsonify({"course_editing": current, "course_editing_id": current_id})
    
@app.route('/api/grade_schema', methods=['GET', 'POST'])
def grade_schema():
    class_id = str(session.get('course_editing_id'))
    all_schemas = session.get('course_schemas', {})

    if request.method == 'POST':
        user_changes = request.get_json()

        all_schemas[class_id] = user_changes
        session['course_schemas'] = all_schemas

        print(user_changes)

        return jsonify(["Schema updated"])
    
    default = ["Master", 100, [], [300, 500], 100]
    return jsonify(all_schemas.get(class_id, default))


#profs can see users data from here
@app.route('/api/grades')
def get_grades():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute("SELECT * FROM users").fetchall()
    
    print("ROWS:", rows)
    
    conn.close()

    class_id = str(session.get('course_editing_id'))
    schema = session.get('course_schemas', {}).get(class_id)

    results = [];

    for row in rows:
        student = dict(row);
    
        if schema:#there is a schema defined
            final_grade = compute_final_grades(schema, student);
        else:#no schema yet
            final_grade = 0;
        student['final_grade'] = final_grade;#add final grade to the data
        results.append(student);


    return jsonify(results);

def init_db():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        crowdmark_id INTEGER PRIMARY KEY,
        score_url TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        student_id TEXT NOT NULL UNIQUE,
        section TEXT NOT NULL,
        RM DECIMAL(5, 2) DEFAULT 0.00,
        ERD DECIMAL(5, 2) DEFAULT 0.00,
        RA DECIMAL(5, 2) DEFAULT 0.00,
        SQL_DDL DECIMAL(5, 2) DEFAULT 0.00,
        SQL_Base DECIMAL(5, 2) DEFAULT 0.00,
        SQL_Adv DECIMAL(5, 2) DEFAULT 0.00,
        HTML DECIMAL(5, 2) DEFAULT 0.00,
        CSS DECIMAL(5, 2) DEFAULT 0.00
    );
                """)
    #clear previous data
    cur.execute("DELETE FROM users;")#we need this bc of unique constraint for now

    #testing input into users
    cur.execute("""
                INSERT INTO users (crowdmark_id, score_url, email, first_name, last_name, student_id, section, RM, ERD, RA, SQL_DDL, SQL_Base, SQL_Adv, HTML, CSS)
    VALUES
    (1, 'url1', 'tim@example.com', 'Tim', 'Tester', '1000000000', 'L01', 85.5, 90.0, 88.5, 92.0, 80.0, 75.5, 88.0, 91.0),
    (2, 'url2', 'amy@example.com', 'Amy', 'Anderson', '1000000001', 'L01', 92.0, 88.5, 95.0, 89.5, 87.0, 92.5, 94.0, 90.0),
    (3, 'url3', 'bob@example.com', 'Bob', 'Brown', '1000000002', 'L02', 78.5, 82.0, 80.5, 85.0, 79.0, 81.5, 76.0, 83.0);
            """)
    
    conn.close()

print("changes")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)