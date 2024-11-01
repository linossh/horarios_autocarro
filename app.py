import streamlit as st
import openai
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def carregar_horarios():
    with open("horarios_autocarros.json", "r") as file:
        horarios = json.load(file)
    return horarios

def obter_proxima_partida(entrada_usuario, horarios_partida, horarios_chegada):
    horarios_mapeados = [
        f"partida {partida} -> chegada {chegada}"
        for partida, chegada in zip(horarios_partida, horarios_chegada)
    ]
    
    prompt = (
        f"Baseado nos seguintes horários:\n{horarios_mapeados}\n"
        f"1. Qual é o próximo horário de partida após {entrada_usuario}?\n"
        f"2. A que horas este autocarro chegará ao destino?\n"
        f"Responda de forma clara mencionando tanto o horário de partida quanto o de chegada."
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system", 
                "content": "Você é um assistente especializado em horários de autocarros. "
                          "Use APENAS os horários fornecidos no mapeamento partida->chegada, "
                          "não faça suposições sobre durações de viagem."
            },
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def main():
    st.title("Horários de Autocarros")
    horarios = carregar_horarios()
    linhas_disponiveis = [linha["numero_linha"] for linha in horarios["linhas"]]
    
    linha_selecionada = st.selectbox("Selecione a linha do autocarro:", linhas_disponiveis)
    
    if st.button("Consultar próximo horário"):
        horario_atual = datetime.now().strftime("%H:%M")
        
        linha = next((linha for linha in horarios["linhas"] if linha["numero_linha"] == linha_selecionada), None)
        if linha:
            horarios_partida = linha["paradas"][0]["horarios"]
            horarios_chegada = linha["paradas"][-1]["horarios"]
            
            if len(horarios_partida) != len(horarios_chegada):
                st.error("Erro: Número diferente de horários de partida e chegada!")
                return
                
            informacao_horarios = obter_proxima_partida(horario_atual, horarios_partida, horarios_chegada)
            st.write(informacao_horarios)

if __name__ == "__main__":
    main()