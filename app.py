from flask import Flask, request, jsonify, session, render_template

app = Flask(__name__)

app.secret_key = 'TimTimTimSahur'

# switch to sql stuff pls

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
    return render_template('main.html')

# this resets the path to whatever you were on
# when you reload the page
@app.route('/main/<path:subpath>')
def catch_all(subpath=None):
    return render_template('main.html')

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

if __name__ == "__main__":
    app.run(debug=True)