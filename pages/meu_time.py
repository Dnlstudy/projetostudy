import streamlit as st
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import requests
from io import BytesIO
import os

st.set_page_config(
    page_title="Meu Time",  # Título com M maiúsculo
    page_icon="🎬",
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
        # Tentar fonte DejaVu que funcionou bem
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 300)  # Ajustado para 300px
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)   # Aumentado para 40px
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)  # Aumentado para 32px
    except:
        try:
            # Tentar fonte Arial que é comum em Windows
            font_title = ImageFont.truetype("arial.ttf", 300)
            font_text = ImageFont.truetype("arial.ttf", 40)
            font_small = ImageFont.truetype("arial.ttf", 32)
        except:
            # Se tudo falhar, usar fonte padrão
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Adicionar título
    title = "MEU TIME"
    title_height = 300  # Ajustado para o novo tamanho
    
    # Calcular largura do título manualmente
    title_width = len(title) * 150  # Ajustado para o novo tamanho
    title_x = (width - title_width) // 2
    title_y = 50  # Um pouco mais pra cima
    
    # Sombra do título com várias camadas para efeito mais dramático
    shadow_offset = 12  # Ajustado para o novo tamanho
    for offset in range(1, shadow_offset + 1):
        draw.text((title_x + offset, title_y + offset), title, 
                 fill=(100 - offset * 7, 0, 0), font=font_title)
    
    # Texto principal do título
    draw.text((title_x, title_y), title, 
              fill=netflix_red, font=font_title)
    
    # Linha de destaque abaixo do título
    accent_line_height = 6  # Um pouco menor
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
        if len(name) > 22:  
            name = name[:19] + "..."  
            
        subject = prof_data["subject"]
        if len(subject) > 18:  
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
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}">{text}</a>'
    return href

def main():
    st.title("Monte seu Time de Professores! 👥")
    
    st.markdown("""
    ### Selecione seus professores favoritos para criar seu time!
    Escolha os professores que mais te ajudam nos estudos e gere uma imagem para compartilhar.
    """)
    
    # Carregar dados dos canais
    channels = load_channels()
    
    # Criar dicionário de professores com suas informações completas
    professors_dict = {
        channel["name"]: channel 
        for channel in channels["featured_channels"]
    }
    
    # Multiselect para escolher os professores
    selected_professors = st.multiselect(
        "Escolha seus professores favoritos:",
        options=sorted(professors_dict.keys()),
        max_selections=9  # Aumentado para 9 seleções
    )
    
    if selected_professors:
        st.write("### Seu Time:")
        
        # Criar colunas para mostrar os cards dos professores selecionados
        cols = st.columns(3)
        for idx, prof_name in enumerate(selected_professors):
            prof_data = professors_dict[prof_name]
            with cols[idx % 3]:
                st.image(prof_data["thumbnail"], width=100)
                st.write(f"**{prof_data['name']}**")
                st.write(f"Matéria: {prof_data['subject']}")
        
        if st.button("Gerar Imagem do Time"):
            selected_data = [professors_dict[name] for name in selected_professors]
            image = create_team_image(selected_data)
            st.image(image, caption="Seu Time de Professores", use_column_width=True)  # Voltando ao redimensionamento automático
            
            # Botão para download
            st.markdown(
                get_image_download_link(image),
                unsafe_allow_html=True
            )
    
    st.markdown("""
    ---
    #### Dicas:
    - Você pode selecionar até 9 professores
    - A imagem gerada pode ser compartilhada nas redes sociais
    - Mostre para seus amigos quem está te ajudando na sua jornada de estudos!
    """)

if __name__ == "__main__":
    main()