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
            part="snippet",
            id=channel_id,
            fields="items(snippet(title,thumbnails/high))"
        )
        response = request.execute()
        return response.get('items', [])[0] if response.get('items') else None
    except Exception as e:
        st.error(f"Erro ao buscar informações do canal: {str(e)}")
        return None

def extract_channel_id(url):
    """Extrai o ID do canal de diferentes formatos de URL do YouTube"""
    try:
        url = url.split('?si=')[0]
        if '@' in url:
            # Para URLs no formato @nomedocanal
            channel_handle = url.split('@')[-1].split('/')[0]
            youtube = get_youtube_client()
            
            # Buscar canal pelo handle
            request = youtube.search().list(
                part="snippet",
                q=f"@{channel_handle}",
                type="channel",
                maxResults=1,
                fields="items(snippet/channelId)"
            )
            response = request.execute()
            
            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
            return None
            
        elif 'youtube.com/channel/' in url:
            # Para URLs no formato youtube.com/channel/ID
            return url.split('youtube.com/channel/')[-1].split('/')[0]
        elif 'youtube.com/c/' in url:
            # Para URLs personalizadas, precisamos buscar o ID
            custom_name = url.split('youtube.com/c/')[-1].split('/')[0]
            youtube = get_youtube_client()
            
            request = youtube.search().list(
                part="snippet",
                q=custom_name,
                type="channel",
                maxResults=1,
                fields="items(snippet/channelId)"
            )
            response = request.execute()
            
            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
        return None
    except Exception as e:
        st.error(f"Erro ao extrair ID do canal: {str(e)}")
        return None
