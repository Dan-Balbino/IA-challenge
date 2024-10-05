from flask import Flask, render_template, request
from AI import AI_request, AI_predict
import threading

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/get", methods = ["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    return AI_request(input)


if __name__ == "__main__":
    # thread_mensagem = threading.Thread(target = exibir_mensagem)
    # thread_mensagem.daemon = True
    # thread_mensagem.start()
     
    app.run(debug=True)
    
    
