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
            data = json.load(f)
            return {
                "featured_channels": data.get("featured_channels", []),
                "banners": data.get("banners", {})
            }
    except (FileNotFoundError, json.JSONDecodeError):
        # Criar novo arquivo com dados padrão
        default_data = {
            "featured_channels": [],
            "banners": {}
        }
        save_channels(default_data)
        return default_data

def save_channels(channels_data):
    """
    Salva os dados dos canais no arquivo JSON.
    Remove qualquer credencial antes de salvar.
    """
    # Garante que apenas dados seguros sejam salvos
    safe_data = {
        "featured_channels": channels_data.get("featured_channels", []),
        "banners": channels_data.get("banners", {})
    }

    backup_file = BASE_DIR / 'channels.json.backup'
    channels_file = BASE_DIR / 'channels.json'

    # Criar backup antes de salvar
    if channels_file.exists():
        with open(channels_file, 'r', encoding='utf-8') as f:
            with open(backup_file, 'w', encoding='utf-8') as backup:
                backup.write(f.read())

    # Salvar novos dados
    with open(channels_file, 'w', encoding='utf-8') as f:
        json.dump(safe_data, f, indent=4, ensure_ascii=False)

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
