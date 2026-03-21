from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Flash Template"

print("hello c")

if __name__ == "__main__":
    app.run(debug=True)