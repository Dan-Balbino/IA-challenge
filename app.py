# ------------- Importações --------------
from flask import Flask, render_template, jsonify, request
from AI import AI_request, AI_predict, AI_pdf
# ----------------------------------------

"""
Alterar banco de dados: AI_functions
Alterar tabela: AI_specs, linha 162
"""

app = Flask(__name__) 

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/get", methods = ["GET", "POST"])
def chat():
    input = request.form["msg"]
    
    if "pdf" in input.lower():
        AI_pdf(input)
        return jsonify(url=f'relatório.pdf')
    else:
        return AI_request(input)

@app.route("/auto", methods = ["GET"])
def automatic_message():
    return AI_predict()

if __name__ == "__main__":
    app.run(debug=True)
