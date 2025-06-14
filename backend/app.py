from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Bem-vindo à API de análise de casos criminais"

if __name__ == '__main__':
    app.run(debug=True)