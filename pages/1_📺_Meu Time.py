import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import json
import requests
from io import BytesIO
import os
import base64

st.set_page_config(
    page_title="Meu Time",
    page_icon="📺",
)

def load_channels():
    with open("channels.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_image_from_url(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def create_team_image(selected_professors_data):
    # Configurações da imagem
    width = 1200
    height = 1200
    background_color = (18, 18, 18)  # Quase preto
    card_color = (30, 30, 30)  # Cinza escuro
    text_color = (255, 255, 255)  # Branco
    netflix_red = (229, 9, 20)  # Vermelho Netflix
    
    # Criar imagem base
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    
    # Carregar fonte do sistema para garantir que funcione
    try:
        # Tentar fontes em ordem de preferência
        font_files = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "C:/Windows/Fonts/Arial.ttf",  # Windows
            "arial.ttf",  # Windows alternativo
            os.path.join(os.path.dirname(__file__), "assets", "BebasNeue-Regular.ttf")  # Nossa fonte
        ]
        
        font_loaded = False
        for font_file in font_files:
            try:
                font_title = ImageFont.truetype(font_file, 250)  # Aumentado MUITO o tamanho
                font_text = ImageFont.truetype(font_file, 32)
                font_small = ImageFont.truetype(font_file, 24)
                font_loaded = True
                break
            except:
                continue
                
        if not font_loaded:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_small = ImageFont.load_default()
            
    except Exception as e:
        print(f"Erro ao carregar fonte: {e}")
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Adicionar título
    title = "MEU TIME"
    title_height = 300  # Mais espaço para o título maior
    
    # Calcular posição do título
    title_width = font_title.getlength(title) if hasattr(font_title, 'getlength') else len(title) * 100
    title_x = (width - title_width) // 2  # Centralização mais precisa
    title_y = 60
    
    # Sombra do título com várias camadas para efeito mais dramático
    shadow_offset = 10
    for offset in range(1, shadow_offset + 1):
        draw.text((title_x + offset, title_y + offset), title, 
                 fill=(100 - offset * 10, 0, 0), font=font_title)
    
    # Texto principal do título
    draw.text((title_x, title_y), title, 
              fill=netflix_red, font=font_title)
    
    # Linha de destaque abaixo do título
    accent_line_height = 8
    draw.rectangle([(0, title_height), (width, title_height + accent_line_height)], 
                  fill=netflix_red)
    
    # Organizar professores em grid
    card_width = 300
    card_height = 250
    margin = 45
    start_y = title_height + accent_line_height + margin
    
    # Calcular posições para centralizar os cards
    total_width = (card_width * 3) + (margin * 2)
    start_x = (width - total_width) // 2
    
    for idx, prof_data in enumerate(selected_professors_data):
        row = idx // 3
        col = idx % 3
        
        x = start_x + col * (card_width + margin)
        y = start_y + row * (card_height + margin)
        
        # Desenhar card com borda vermelha
        draw.rectangle([(x, y), (x + card_width, y + card_height)], 
                      fill=card_color, outline=netflix_red, width=3)
        
        try:
            # Carregar e redimensionar thumbnail
            thumb = get_image_from_url(prof_data["thumbnail"])
            thumb = thumb.resize((160, 160))
            
            # Criar máscara circular
            mask = Image.new('L', (160, 160), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 160, 160), fill=255)
            
            # Aplicar máscara
            output = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
            output.paste(thumb, (0, 0))
            
            # Calcular posição centralizada para a imagem
            thumb_x = x + (card_width - 160) // 2
            thumb_y = y + 20
            
            # Colar na imagem principal
            image.paste(output, (thumb_x, thumb_y), mask)
        except:
            # Se falhar ao carregar a imagem, desenhar um círculo placeholder
            center_x = x + card_width // 2
            draw.ellipse((center_x - 80, y + 20, center_x + 80, y + 180), 
                        fill=netflix_red, outline=text_color)
        
        # Truncar nomes muito longos
        name = prof_data["name"]
        if len(name) > 22:  # Se o nome for muito longo
            name = name[:19] + "..."  # Trunca e adiciona reticências
            
        subject = prof_data["subject"]
        if len(subject) > 18:  # Se a matéria for muito longa
            subject = subject[:15] + "..."
        
        # Calcular posições para centralizar os textos
        name_width = font_text.getlength(name) if hasattr(font_text, 'getlength') else len(name) * 11
        subject_width = font_small.getlength(subject) if hasattr(font_small, 'getlength') else len(subject) * 9
        
        name_x = x + (card_width - name_width) // 2
        subject_x = x + (card_width - subject_width) // 2
        
        draw.text((name_x, y + 190), name, 
                 fill=text_color, font=font_text)
        draw.text((subject_x, y + 220), subject, 
                 fill=text_color, font=font_small)
    
    # Adicionar créditos na parte inferior com cor mais visível
    credits = "Criado por @danielstudytwt"
    credits_width = len(credits) * 7
    draw.text((width - credits_width - 100, height - 35), credits,  # Movido 100px da borda direita
              fill=(180, 180, 180), font=font_small)
    
    return image

def get_image_download_link(img, filename="meu_time.png", text="Baixar Imagem"):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}">{text}</a>'
    return href

# Carregar dados dos canais
channels = load_channels()

# Título e descrição
st.title("Meu Time de Professores 👥")
st.write("Selecione seus professores favoritos para gerar uma imagem estilo Netflix!")

# Criar multiselect para escolher os professores
selected_professors = st.multiselect(
    "Escolha até 9 professores:",
    options=[channel["name"] for channel in channels],
    max_selections=9
)

# Botão para gerar imagem
if st.button("Gerar Imagem do Time"):
    if not selected_professors:
        st.warning("Por favor, selecione pelo menos um professor!")
    else:
        # Filtrar dados dos professores selecionados
        selected_professors_data = [
            channel for channel in channels 
            if channel["name"] in selected_professors
        ]
        
        # Criar e mostrar a imagem
        image = create_team_image(selected_professors_data)
        st.image(image, caption="Seu Time de Professores", use_column_width=True)
        
        # Adicionar botão de download
        st.markdown(get_image_download_link(image), unsafe_allow_html=True)
