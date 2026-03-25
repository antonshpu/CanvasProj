from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Flsassh Template"

print("erorr testy 2")

print("hello c")

print("hello c")

if __name__ == "__main__":
    app.run(debug=True)