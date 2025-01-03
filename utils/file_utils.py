import json
from pathlib import Path
import hashlib
import secrets
import os
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

# Carrega as variáveis de ambiente
load_dotenv()

# Configurar o caminho base do projeto
BASE_DIR = Path(__file__).parent.parent

def load_channels():
    """
    Carrega os dados dos canais do arquivo JSON.
    Se o arquivo não existir, cria um novo com configurações padrão.
    """
    try:
        with open(BASE_DIR / 'channels.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Criar novo arquivo com dados padrão
        default_data = {
            "featured_channels": [],
            "categories": {
                "vestibular": {
                    "name": "Vestibular",
                    "description": "Canais focados em preparação para vestibular"
                },
                "informatica": {
                    "name": "Informática",
                    "description": "Canais sobre programação e computação"
                },
                "engenharia": {
                    "name": "Engenharia",
                    "description": "Canais sobre engenharia e tecnologia"
                }
            },
            "banners": {
                "cover": "",
                "promotional": []
            }
        }
        save_channels(default_data)
        return default_data

def save_channels(channels_data):
    """
    Salva os dados dos canais no arquivo JSON.
    """
    backup_file = BASE_DIR / 'channels.json.backup'
    channels_file = BASE_DIR / 'channels.json'

    # Criar backup antes de salvar
    if channels_file.exists():
        with open(channels_file, 'r', encoding='utf-8') as f:
            with open(backup_file, 'w', encoding='utf-8') as backup:
                backup.write(f.read())

    # Salvar novos dados
    with open(channels_file, 'w', encoding='utf-8') as f:
        json.dump(channels_data, f, indent=4, ensure_ascii=False)

def verify_admin_credentials(username, password):
    """
    Verifica as credenciais do admin usando as configurações do Streamlit.
    """
    correct_username = st.secrets["ADMIN_USERNAME"]
    correct_password = st.secrets["ADMIN_PASSWORD"]
    
    return username == correct_username and password == correct_password

def generate_session_token():
    """
    Gera um token de sessão seguro.
    """
    return secrets.token_hex(32)

def validate_session_token(token):
    """
    Valida se o token de sessão ainda é válido.
    """
    if not token or not hasattr(st.session_state, 'admin_session'):
        return False
    
    # Verifica se o token corresponde
    if token != st.session_state.admin_session.get('token'):
        return False
    
    # Verifica se a última atividade foi há menos de 24 horas
    last_activity = st.session_state.admin_session.get('last_activity', 0)
    if (datetime.now().timestamp() - last_activity) > 86400:  # 24 horas em segundos
        return False
    
    # Atualiza o timestamp da última atividade
    st.session_state.admin_session['last_activity'] = datetime.now().timestamp()
    return True
