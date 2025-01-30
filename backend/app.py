from flask import Flask, jsonify
from main import main_result

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from the default page of the server."

@app.route("/analysis/<string:claims>")
def give_analysis(claims):
    result = main_result(str(claims))    
    return jsonify({"result": result})


if __name__=="__main__":
    app.run(host="0.0.0.0", port=5001)