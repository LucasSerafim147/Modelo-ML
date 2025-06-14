from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from pymongo import MongoClient
from dataclasses import dataclass, asdict
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["meu_banco"]
colecao = db["meus_dados"]

@dataclass
class Vitima:
    etnia: str
    idade: int

@dataclass
class Caso:
    data_do_caso: str
    tipo_do_caso: str
    localizacao: str
    vittima: Vitima

    def to_dict(self):
        return {
            "data_do_caso": self.data_do_caso,
            "tipo_do_caso": self.tipo_do_caso,
            "localizacao": self.localizacao,
            "vitima": asdict(self.vittima)
        }

def gerar_dados_aleatorios(n=20):
    tipos_casos = ["Furto", "Assalto", "Violência doméstica", "Tráfico"]
    locais = ["Centro", "Bairro A", "Bairro B", "Zona Rural"]
    etnias = ["Branca", "Preta", "Parda", "Indígena", "Amarela"]
    casos = []
    base_date = datetime.now()
    
    for i in range(n):
        data_caso = (base_date - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        caso = Caso(
            data_do_caso=data_caso,
            tipo_do_caso=random.choice(tipos_casos),
            localizacao=random.choice(locais),
            vittima=Vitima(
                etnia=random.choice(etnias),
                idade=random.randint(1, 90)
            )
        )
        casos.append(caso.to_dict())
    return casos

def validar_caso_json(data):
    try:
        vitima = data["vitima"]
        assert isinstance(vitima, dict)
        assert all(k in vitima for k in ("etnia", "idade"))
        datetime.fromisoformat(data["data_do_caso"])
        assert isinstance(data["tipo_do_caso"], str)
        assert isinstance(data["localizacao"], str)
        return True
    except:
        return False

@app.route('/')
def hello():
    return "Bem-vindo à API de análise de casos criminais"

@app.route('/api/casos', methods=['GET'])
def listar_casos():
    documentos = list(colecao.find({}, {'_id': 0}))
    return jsonify(documentos), 200

@app.route('/api/casos', methods=['POST'])
def criar_caso():
    data = request.get_json()
    if not data or not validar_caso_json(data):
        abort(400, "JSON inválido ou campos faltando.")
    colecao.insert_one(data)
    return jsonify({"message": "Caso criado com sucesso"}), 201

@app.route('/api/casos/<string:data_caso>', methods=['GET'])
def buscar_caso(data_caso):
    caso = colecao.find_one({"data_do_caso": data_caso}, {'_id': 0})
    if not caso:
        abort(404, "Caso não encontrado.")
    return jsonify(caso), 200

@app.route('/api/casos/<string:data_caso>', methods=['DELETE'])
def deletar_caso(data_caso):
    resultado = colecao.delete_one({"data_do_caso": data_caso})
    if resultado.deleted_count == 0:
        abort(404, "Caso não encontrado.")
    return jsonify({"message": "Caso deletado"}), 200

if __name__ == "__main__":
    if colecao.count_documents({}) == 0:
        print("Inserindo dados iniciais...")
        dados_iniciais = gerar_dados_aleatorios(20)
        colecao.insert_many(dados_iniciais)
    app.run(debug=True)