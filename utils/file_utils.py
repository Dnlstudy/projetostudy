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
    # Use session state as a cache
    if 'channels_data' in st.session_state:
        return st.session_state.channels_data

    try:
        channels_file = BASE_DIR / 'channels.json'
        if not channels_file.exists():
            raise FileNotFoundError
        
        with open(channels_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Cache the data
            st.session_state.channels_data = data
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.warning("Criando novo arquivo de dados...")
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
        st.session_state.channels_data = default_data
        return default_data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

def save_channels(channels_data):
    """
    Salva os dados dos canais no arquivo JSON.
    """
    try:
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
        
        # Update session state cache
        st.session_state.channels_data = channels_data
        
        # Verificar se os dados foram salvos corretamente
        with open(channels_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            if saved_data != channels_data:
                raise ValueError("Verificação de dados falhou após salvar")
                
    except Exception as e:
        st.error(f"Erro ao salvar dados: {str(e)}")
        # Tentar restaurar do backup se houver erro
        if backup_file.exists():
            try:
                with open(backup_file, 'r', encoding='utf-8') as backup:
                    backup_data = json.load(backup)
                with open(channels_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=4, ensure_ascii=False)
                st.session_state.channels_data = backup_data
                st.warning("Dados restaurados do backup após erro ao salvar")
            except Exception as backup_error:
                st.error(f"Erro ao restaurar backup: {str(backup_error)}")

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
