import json
from pathlib import Path

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
    with open(BASE_DIR / 'channels.json', 'w', encoding='utf-8') as f:
        json.dump(channels_data, f, indent=4, ensure_ascii=False)
