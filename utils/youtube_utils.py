import streamlit as st
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

def get_youtube_client():
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        st.error("⚠️ Chave da API do YouTube não encontrada!")
        st.stop()
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        return youtube
    except Exception as e:
        st.error(f"⚠️ Erro ao conectar com a API do YouTube: {str(e)}")
        st.stop()

def get_channel_info(youtube, channel_id):
    try:
        request = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id,
            fields="items(snippet(title,thumbnails/high))"
        )
        response = request.execute()
        
        if not response.get('items'):
            return None
            
        channel_data = response['items'][0]
        return {
            "title": channel_data['snippet']['title'],
            "thumbnail": channel_data['snippet']['thumbnails']['high']['url']
        }
    except Exception as e:
        st.error(f"Erro ao buscar informações do canal: {str(e)}")
        return None

def extract_channel_id(url):
    """Extrai o ID do canal de diferentes formatos de URL do YouTube"""
    try:
        # Remover parâmetros da URL
        url = url.split('?')[0].strip('/')
        
        if '/channel/' in url:
            # Para URLs no formato youtube.com/channel/ID
            return url.split('/channel/')[-1]
        elif '/c/' in url or '/user/' in url or '@' in url:
            # Para URLs personalizadas ou com handle (@), precisamos buscar o ID
            youtube = get_youtube_client()
            
            # Se for uma URL com @, extrair o handle
            if '@' in url:
                channel_handle = '@' + url.split('@')[-1].split('/')[0]
            else:
                # Se for /c/ ou /user/, extrair o nome personalizado
                channel_handle = url.split('/')[-1]
            
            # Buscar canal
            request = youtube.search().list(
                part="id",
                q=channel_handle,
                type="channel",
                maxResults=1
            )
            response = request.execute()
            
            if response.get('items'):
                return response['items'][0]['id']['channelId']
            
        return None
    except Exception as e:
        st.error(f"Erro ao extrair ID do canal: {str(e)}")
        return None
