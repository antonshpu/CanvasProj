from flask import Flask, request, jsonify, session, render_template
import sqlite3

app = Flask(__name__)

app.secret_key = 'TimTimTimSahur'

current_courses = [ # these will be mapped to a specific user
        {"code": "CSCA67", "name": "Discrete Mathematics"},
        {"code": "MATA22", "name": "Linear Algebra I For Mathematical Sciences"}, # this will be automated later so no dupesnm
    ]  

course_codes_to_names = {
    "CSCA67": "Discrete Mathematics",
    "MATA22": "Linear Algebra I For Mathematical Sciences",
    "MATA37": "Calculus II For Mathematical Sciences",
    "CSCB20": "Introduction To Databases",
}

@app.route('/')
def index():
    return render_template('main.html', courses=current_courses)

# this resets the path to whatever you were on
# when you reload the page
@app.route('/main/<path:subpath>')
def catch_all(subpath=None):
    return render_template('main.html', courses=current_courses)

@app.route('/api/courses')
def class_selector():

    return jsonify(current_courses) # we want to port these to JS for easy of use esp when sql..

@app.route('/api/add_course', methods=['POST'])
def add_course():
    data = request.get_json()
    course_code = data.get('course_code', '').strip().upper() # map this to a name

    #user_id = session.get('user_id') # not used atm

    if course_code not in course_codes_to_names: # error case
        return jsonify(["Course does not exist"])
    
    current_courses.append({"code": course_code, "name": course_codes_to_names[course_code]})
    
    return jsonify(["Succesful course creation"])

@app.route('/api/remove_course', methods=['POST'])
def remove_course():
    data = request.get_json()
    course_code = data.get('course_code', '').strip().upper() # map this to a name

    #user_id = session.get('user_id') # not used atm
    
    current_courses.remove({"code": course_code, "name": course_codes_to_names[course_code]})
    
    return jsonify(["Successful course removal"])

#profs can see users data from here
@app.route('/api/grades')
def get_grades():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute("SELECT * FROM users").fetchall()
    
    print("ROWS:", rows)
    
    conn.close()

    return jsonify([dict(row) for row in rows])


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
        section TEXT NOT NULL
    );
                """)

    # working for B20 format currently

    skills = ["RM", "ERD", "RA", "SQL_DDL", "SQL_Base", "SQL_Adv", "HTML", "CSS"]

    for i in skills:
        try:
            cur.execute(f"""
            ALTER TABLE users ADD COLUMN {i} DECIMAL(5, 2) DEFAULT 0.00;
                        """)
        except:
            pass


    #clear previous data
    cur.execute("DELETE FROM users;")

    #testing input into users
    cur.execute("""
                INSERT INTO users (crowdmark_id, score_url, email, first_name, last_name, student_id, section)
    VALUES
    (1, 'url1', 'tim@example.com', 'Tim', 'Tester', '1000000000', 'L01'),
    (2, 'url2', 'amy@example.com', 'Amy', 'Anderson', '1000000001', 'L01'),
    (3, 'url3', 'bob@example.com', 'Bob', 'Brown', '1000000002', 'L02');
            """)
    conn.commit()
    conn.close()

print("changes")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)