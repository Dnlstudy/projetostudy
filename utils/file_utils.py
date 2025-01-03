import json
from pathlib import Path
import hashlib
import secrets
import os
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st
from pymongo import MongoClient

# Carrega as variáveis de ambiente
load_dotenv()

# Configurar o caminho base do projeto
BASE_DIR = Path(__file__).parent.parent

def get_database():
    """
    Conecta ao MongoDB Atlas usando as credenciais do Streamlit Secrets.
    """
    if 'mongo_client' not in st.session_state:
        try:
            mongo_uri = st.secrets["MONGODB_URI"]
            client = MongoClient(mongo_uri)
            st.session_state.mongo_client = client
        except Exception as e:
            st.error(f"Erro ao conectar com o banco de dados: {str(e)}")
            return None
    
    return st.session_state.mongo_client.studyflix

def load_channels():
    """
    Carrega os dados dos canais do MongoDB.
    Se não existir, cria com configurações padrão.
    """
    try:
        # Use session state as a cache
        if 'channels_data' in st.session_state:
            return st.session_state.channels_data

        db = get_database()
        if not db:
            raise Exception("Não foi possível conectar ao banco de dados")

        # Tenta carregar os dados
        data = db.channels.find_one({"_id": "main"})
        
        if not data:
            # Criar dados padrão
            default_data = {
                "_id": "main",
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
            db.channels.insert_one(default_data)
            st.session_state.channels_data = default_data
            return default_data

        # Remove o _id do MongoDB antes de retornar
        if "_id" in data:
            del data["_id"]
        
        st.session_state.channels_data = data
        return data

    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

def save_channels(channels_data):
    """
    Salva os dados dos canais no MongoDB.
    """
    try:
        db = get_database()
        if not db:
            raise Exception("Não foi possível conectar ao banco de dados")

        # Adiciona o _id para o MongoDB
        data_to_save = channels_data.copy()
        data_to_save["_id"] = "main"

        # Salva no MongoDB
        db.channels.replace_one({"_id": "main"}, data_to_save, upsert=True)
        
        # Atualiza o cache
        st.session_state.channels_data = channels_data
        
        st.success("Dados salvos com sucesso!")
        
    except Exception as e:
        st.error(f"Erro ao salvar dados: {str(e)}")

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

def git_push_changes(file_path, commit_message):
    """
    Faz commit e push das alterações no arquivo para o GitHub.
    """
    try:
        # Configura o git com as credenciais
        subprocess.run(['git', 'config', 'user.email', st.secrets["GIT_EMAIL"]], cwd=BASE_DIR)
        subprocess.run(['git', 'config', 'user.name', st.secrets["GIT_USERNAME"]], cwd=BASE_DIR)
        
        # Add, commit e push
        subprocess.run(['git', 'add', file_path], cwd=BASE_DIR)
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=BASE_DIR)
        subprocess.run(['git', 'push', 'origin', 'master'], cwd=BASE_DIR)
        return True
    except Exception as e:
        st.error(f"Erro ao fazer push para o GitHub: {str(e)}")
        return False
