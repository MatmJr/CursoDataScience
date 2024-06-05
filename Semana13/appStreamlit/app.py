import streamlit as st
import pandas as pd
import requests
from io import StringIO
import re
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Criação do dataFrame dos alunos
file_id = '1S5Nl793vcL5ZPTGjzKaIEbwbLaDplvIP'
url = f"https://drive.google.com/uc?id={file_id}"

try:
    response = requests.get(url)
    response.raise_for_status()
    csv_raw = StringIO(response.text)
    data = pd.read_csv(csv_raw)
except requests.RequestException as e:
    st.error(f"Erro ao acessar o arquivo: {e}")

data = data.set_index("PassengerId")

def extract_title(name):
    title_search = re.search(' ([A-Za-z]+)\.', name)
    if title_search:
        return title_search.group(1)
    return ""

data['Title'] = data['Name'].apply(extract_title)
data['Age'] = data.groupby(['Sex', 'Pclass'])['Age'].transform(lambda x: x.fillna(x.median()))
data['Embarked'] = data['Embarked'].fillna('S')

for num in [1, 2, 3]:
    if num == 1:
        data.loc[data['Pclass'] == 1, 'Cabin'] = data.loc[data['Pclass'] == 1, 'Cabin'].fillna('ABC')
    elif num == 2:
        data.loc[data['Pclass'] == 2, 'Cabin'] = data.loc[data['Pclass'] == 2, 'Cabin'].fillna('DE')
    elif num == 3:
        data.loc[data['Pclass'] == 3, 'Cabin'] = data.loc[data['Pclass'] == 3, 'Cabin'].fillna('FG')
        
label_encoder_sex = LabelEncoder().fit(data['Sex'])
label_encoder_cabin = LabelEncoder().fit(data['Cabin'])
label_encoder_title = LabelEncoder().fit(data['Title'])
label_encoder_embarked = LabelEncoder().fit(data['Embarked'])

df_encoded = data.copy()
df_encoded['Sex'] = label_encoder_sex.transform(data['Sex'])
df_encoded['Cabin'] = label_encoder_cabin.transform(data['Cabin'])
df_encoded['Title'] = label_encoder_title.transform(data['Title'])
df_encoded['Embarked'] = label_encoder_embarked.transform(data['Embarked'])

df_encoded = df_encoded.drop(['Name', 'Ticket'], axis=1)
x_train, x_test, y_train, y_test = train_test_split(df_encoded.drop(['Survived'], axis=1),
                                                     df_encoded['Survived'],
                                                     test_size=0.3,
                                                     random_state=1234)

rf = RandomForestClassifier(n_estimators=1000, criterion='gini', max_depth=5)
rf.fit(x_train, y_train)

prob = rf.predict_proba(df_encoded.drop('Survived', axis=1))[:, 1]
cla = rf.predict(df_encoded.drop('Survived', axis=1))

data['Probability'] = prob
data['Classification'] = cla

def prever_sobrevivencia(model, attributes, df_template):
    attributes['Cabin'] = 0
    attributes['Title'] = 0
    
    df = pd.DataFrame([attributes])
    columns_to_use = df_template.drop(['Survived', 'Probability', 'Classification', 'Name', 'Ticket'], axis=1, errors='ignore').columns
    df = df.reindex(columns=columns_to_use, fill_value=0)
    
    probabilidade = model.predict_proba(df)[:, 1][0]
    classificacao = model.predict(df)[0]
    
    return probabilidade, classificacao

# Streamlit App
st.title("Previsão de Sobrevivência - Dataset Titanic")

with st.form(key='survival_form'):
    # Inputs
    pclass = st.selectbox("Classe do Passageiro", [1, 2, 3])
    sex = st.selectbox("Sexo", ["male", "female"])
    age = st.number_input("Idade", min_value=0, max_value=100, value=25)
    sibsp = st.number_input("Número de Irmãos/Cônjuges a Bordo", min_value=0, max_value=10, value=0)
    parch = st.number_input("Número de Pais/Filhos a Bordo", min_value=0, max_value=10, value=0)
    fare = st.number_input("Tarifa", min_value=0.0, value=32.0)
    embarked = st.selectbox("Porto de Embarque", ["C", "Q", "S"])
    
    submit_button = st.form_submit_button(label='Prever Sobrevivência')

if submit_button:
    attributes = {
        'Pclass': pclass,
        'Sex': label_encoder_sex.transform([sex])[0],
        'Age': age,
        'SibSp': sibsp,
        'Parch': parch,
        'Fare': fare,
        'Embarked': label_encoder_embarked.transform([embarked])[0]
    }

    probabilidade, classificacao = prever_sobrevivencia(rf, attributes, df_encoded)
    st.write(f"Probabilidade de Sobrevivência: {probabilidade:.2f}")
    st.write(f"Classificação: {'Sobreviveu' if classificacao == 1 else 'Não Sobreviveu'}")
