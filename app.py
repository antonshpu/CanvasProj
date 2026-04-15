from flask import Flask, request, jsonify, session, render_template, redirect
import sqlite3

app = Flask(__name__)

app.secret_key = 'TimTimTimSahur'

def compute_final_grades(node, student_row):
    name, max_points, children, pos, weight = node
    if not children:##i.e it is a skill (HTML, CSS, ...)
        raw_score = student_row.get(name, 0)
        if(max_points == 0):
            return 0 ## no points for this skill
        return (raw_score/max_points) * (weight/100)
    else:##i.e. it is a category that contains skills
        total = 0
        for child in children:
            total += compute_final_grades(child, student_row)
        
        # scale the sum of the weightest children by the parents given percentage to the parent
        return total * (weight / 100) if name != "Master" else total * 100

@app.route('/')
@app.route('/main/<path:subpath>')
def catch_all(subpath=None):
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('main.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('app.db')
        cur = conn.cursor()
        cur.execute("SELECT password, prof_id FROM prof_users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()

        if row and row[0] == password:
            session['logged_in'] = row[1] ## nonempty prof id
            return redirect('/')
        
        return "wrong username or password"

@app.route('/api/logout', methods=['POST'])
def logout():
    if request.method=='POST':
        session['logged_in'] = False
        return redirect('/')

@app.route('/api/courses')
def class_selector():
    prof_id = session.get('logged_in')
    conn = sqlite3.connect('app.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT pc.id, pc.course_code, cn.name 
        FROM prof_courses pc
        JOIN course_names cn ON pc.course_code = cn.code
        WHERE pc.prof_id = ?
    """, (prof_id,))
    rows = cur.fetchall()
    conn.close()

    current_courses = {str(r[0]): {"code": r[1], "name": r[2]} for r in rows}
    return jsonify(current_courses)

def course_dict_from_db():
    conn = sqlite3.connect('app.db')
    cur = conn.cursor()
    
    cur.execute("SELECT code, name FROM course_names")
    rows = cur.fetchall()
    
    conn.close()
    
    return {code: name for code, name in rows}

@app.route('/api/add_course', methods=['POST'])
def add_course():
    data = request.get_json()
    course_code = data.get('course_code', '').strip().upper() # map this to a name

    #user_id = session.get('user_id') # not used atm

    course_codes_to_names = course_dict_from_db()

    if course_code not in course_codes_to_names: # error case
        return jsonify(["Course does not exist"])
    
    new_id = session.get('id_counter', 0) + 1
    session['id_counter'] = new_id

    conn = sqlite3.connect('app.db')
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO prof_courses (id, prof_id, course_code) 
        VALUES (?, ?, ?)
    """, (new_id, session.get('logged_in'), course_code)) # not secure to use the session cookie like this, but the second index is prof_id
    
    conn.commit()
    conn.close()
    
    return jsonify(["Succesful course creation"])

@app.route('/api/remove_course', methods=['POST'])
def remove_course():
    data = request.get_json()
    course_id = data.get('id')
    prof_id = session.get('logged_in')

    conn = sqlite3.connect('app.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM prof_courses WHERE prof_id = ? AND id = ?", (prof_id, course_id))
    rows_affected = conn.total_changes
    conn.commit()
    conn.close()

    return jsonify(["Succesful course removal"])
    

@app.route('/api/select_course', methods=['GET', 'POST'])
def select_course():
    if (request.method == 'POST'):
        data = request.get_json()
        course_code = data.get('course_code', '').strip().upper()
        course_id = data.get('id')
        prof_id = session.get('logged_in')

        conn = sqlite3.connect('app.db')
        cur = conn.cursor()
        cur.execute("SELECT course_code FROM prof_courses WHERE prof_id = ? AND id = ?", (prof_id, course_id))
        row = cur.fetchone()
        conn.close()

        if row:
            session['course_editing'] = course_code
            session['course_editing_id'] = course_id
            return jsonify(["Successful course selection"])
        return jsonify(["Course not found"]), 404
    else:
        current = session.get('course_editing', 'NONE')
        current_id = session.get('course_editing_id', '-1')
        return jsonify({"course_editing": current, "course_editing_id": current_id})
    
import json

@app.route('/api/grade_schema', methods=['GET', 'POST'])
def grade_schema():
    class_id = session.get('course_editing_id')
    
    if request.method == 'POST':
        user_changes = request.get_json()
        
        conn = sqlite3.connect('app.db')
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO course_schemas (course_id, schema_diagram)
            VALUES (?, ?)
        """, (class_id, json.dumps(user_changes)))
        conn.commit()
        conn.close()

        return jsonify(["Schema updated"])
    
    conn = sqlite3.connect('app.db')
    cur = conn.cursor()
    cur.execute("SELECT schema_diagram FROM course_schemas WHERE course_id = ?", (class_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return jsonify(json.loads(row[0]))
    
    return jsonify(["Master", 100, [], [300, 500], 100])


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

    # pull the list data to use

    conn = sqlite3.connect('app.db')
    cur = conn.cursor()
    
    cur.execute("SELECT schema_diagram FROM course_schemas WHERE course_id = ?", (class_id,))
    row = cur.fetchone()
    conn.close()

    schema = json.loads(row[0]) # converts to list form from the sql text so we can parse easy

    results = []

    for row in rows:
        student = dict(row)
    
        if schema:#there is a schema defined
            final_grade = compute_final_grades(schema, student)
        else:#no schema yet
            final_grade = 0
        student['final_grade'] = final_grade;#add final grade to the data
        results.append(student)

    return jsonify(results)

def init_db():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    course_codes_to_names = {
        "CSCA67": "Discrete Mathematics",
        "MATA22": "Linear Algebra I For Mathematical Sciences",
        "MATA37": "Calculus II For Mathematical Sciences",
        "CSCB20": "Introduction To Databases",
        "CSCA08": "Introduction to Computer Science I",
        "CSCA48": "Introduction to Computer Science II",
        "CSCB07": "Software Design",
    }

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS course_names (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prof_users (
            prof_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prof_courses (
        id INTEGER PRIMARY KEY,
        prof_id INTEGER NOT NULL,
        course_code TEXT NOT NULL,
        FOREIGN KEY (prof_id) REFERENCES prof_users (prof_id)
        )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS course_schemas (
        course_id INTEGER PRIMARY KEY,
        schema_diagram TEXT NOT NULL,
        FOREIGN KEY (course_id) REFERENCES prof_courses (prof_id)
    )
    """)

    #clear previous data
    cur.execute("DELETE FROM course_names;")
    cur.execute("DELETE FROM prof_users;")
    cur.execute("DELETE FROM course_schemas;")
    cur.execute("DELETE FROM users;")#we need this bc of unique constraint for now

    cur.execute("""
    INSERT INTO prof_users (username, password, prof_id) 
    VALUES (?, ?, ?)
    """, ("tim_prof", "password", 1)) 

    #testing input into users
    cur.execute("""
    INSERT INTO users (crowdmark_id, score_url, email, first_name, last_name, student_id, section, RM, ERD, RA, SQL_DDL, SQL_Base, SQL_Adv, HTML, CSS)
    VALUES
    (1, 'url1', 'tim@example.com', 'Tim', 'Tester', '1000000000', 'L01', 2, 1, 3, 2, 2, 1, 1, 1),
    (2, 'url2', 'amy@example.com', 'Amy', 'Anderson', '1000000001', 'L01', 2, 1, 2, 2, 2, 1, 3, 2),
    (3, 'url3', 'bob@example.com', 'Bob', 'Brown', '1000000002', 'L02', 2, 1, 2, 2, 3, 2, 3, 2),
    (4, 'url4', 'sam@example.com', 'Sam', 'Hello', '1000000003', 'L03', 2, 0, 2, 0, 3, 2, 0, 2),
    (5, 'url5', 'nosql_grades@example.com', 'sql hater', 'f', '1000000004', 'L01', 2, 0, 2, 0, 0, 0, 0, 2);
""") # this is a global list of users, can be changed for real implementation
    
    cur.executemany(
        "INSERT INTO course_names (code, name) VALUES (?, ?)",
        list(course_codes_to_names.items())
    )
    
    conn.commit()
    
    conn.close()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)