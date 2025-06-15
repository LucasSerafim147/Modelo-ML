import pandas as pd
from pymongo import MongoClient
from xgboost import XGBClassifier
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
import random

# 🔗 Conexão com MongoDB
client = MongoClient("mongodb+srv://fariassrafaella:qoQ2wBQg3PTud6tv@odx-pericias.zoribdu.mongodb.net/odx-pericias?retryWrites=true&w=majority&appName=odx-pericias")
db = client["odx-pericias"]
cases = list(db["cases"].find({}, {"_id": 0}))
vitimas = list(db["vitimas"].find({}, {"_id": 0}))

print(f"Total de casos: {len(cases)}")
print(f"Total de vítimas: {len(vitimas)}")

# 🔁 Associação simulada entre casos e vítimas
dados_combinados = []
for caso in cases:
    if not vitimas:
        continue
    vitima = random.choice(vitimas)

    try:
        dados_combinados.append({
            "idade": vitima.get("idadeAproximada"),
            "sexo": vitima.get("sexo"),
            "cidade": caso.get("cidade"),
            "estado": caso.get("estado"),
            "tipo_do_caso": caso.get("titulo")  # ou use `descricao` ou `status` se preferir
        })
    except Exception as e:
        print(f"Erro ao montar dados: {e}")
        continue

df = pd.DataFrame(dados_combinados)
df.dropna(inplace=True)

print(df.head())

# 🔤 Preparo para o modelo
X = df[["idade", "sexo", "cidade", "estado"]]
y = df["tipo_do_caso"]

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

categorical_features = ["sexo", "cidade", "estado"]
numeric_features = ["idade"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown='ignore'), categorical_features),
        ("num", "passthrough", numeric_features)
    ]
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", XGBClassifier(use_label_encoder=False, eval_metric='mlogloss'))
])

pipeline.fit(X, y_encoded)

# 💾 Salvando modelo
with open("model.pkl", "wb") as f:
    pickle.dump({
        "pipeline": pipeline,
        "label_encoder": label_encoder
    }, f)

print(" Modelo treinado e salvo com sucesso.")
