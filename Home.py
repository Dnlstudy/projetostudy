import streamlit as st
from utils.file_utils import load_channels
import webbrowser

# Configuração da página - DEVE ser a primeira chamada Streamlit
st.set_page_config(
    page_title="Studyflix",
    page_icon="📚",
    layout="wide"
)

# Estilos CSS
st.markdown("""
<style>
    /* Estilos gerais */
    .netflix-title {
        color: #E50914;
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
    }
    
    /* Estilos do carrossel */
    .channel-carousel {
        overflow-x: auto;
        white-space: nowrap;
        padding: 10px 0;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none; /* Firefox */
        margin: 0 -1rem;
        padding: 0 1rem;
    }
    
    .channel-carousel::-webkit-scrollbar {
        display: none; /* Chrome, Safari, Edge */
    }
    
    .channel-card {
        display: inline-block;
        width: 200px;
        margin-right: 15px;
        vertical-align: top;
        transition: transform 0.3s;
        text-decoration: none;
    }
    
    .channel-card:hover {
        transform: scale(1.05);
    }
    
    .channel-card img {
        width: 100%;
        border-radius: 8px;
        aspect-ratio: 16/9;
        object-fit: cover;
    }
    
    .channel-card .title {
        color: white;
        margin-top: 8px;
        font-size: 14px;
        white-space: normal;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        line-height: 1.2;
        height: 2.4em;
    }
    
    .subject-title {
        color: #E50914;
        margin: 30px 0 10px 0;
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Estilos responsivos */
    @media (max-width: 768px) {
        .channel-card {
            width: 160px;
            margin-right: 12px;
        }
        
        .subject-title {
            font-size: 20px;
            margin: 20px 0 8px 0;
        }
    }
</style>
""", unsafe_allow_html=True)

def display_channels(channels_data):
    # Remove padding padrão do Streamlit e força tema escuro
    st.markdown("""
        <style>
            /* Reset Streamlit */
            .element-container, .stMarkdown, div[data-testid="stHorizontalBlock"], 
            .stDeployButton, .main, .st-emotion-cache-1y4p8pa,
            .st-emotion-cache-1wrcr25, .st-emotion-cache-6qob1r,
            .st-emotion-cache-ue6h4q, .st-emotion-cache-eczf16 {
                padding: 0 !important;
                margin: 0 !important;
                background-color: transparent !important;
                color: white !important;
            }
            
            /* Força tema escuro */
            body, iframe {
                background-color: rgb(14, 17, 23) !important;
            }
            
            /* Esconde scrollbar padrão */
            ::-webkit-scrollbar {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Agrupar canais por matéria
    channels_by_subject = {}
    for channel in channels_data.get("featured_channels", []):
        subject = channel.get("subject", "Outros")
        if subject not in channels_by_subject:
            channels_by_subject[subject] = []
        channels_by_subject[subject].append(channel)
    
    # Exibir canais agrupados por matéria em ordem alfabética
    for subject in sorted(channels_by_subject.keys()):
        channels = channels_by_subject[subject]
        
        # Título da matéria
        st.markdown(f'<h3 class="subject-title">{subject}</h3>', unsafe_allow_html=True)
        
        # Calcular altura baseada no número de linhas do título (2) + altura da imagem + padding
        img_height = 280 * 9/16  # width * 9/16 para aspect ratio 16:9
        title_height = 2 * 14 * 1.2  # 2 linhas * font-size * line-height
        total_height = img_height + title_height + 40  # +40 para padding e margem
        
        # HTML completo com iframe
        html = f"""
            <div style="width: 100%; height: {int(total_height)}px;">
                <iframe srcdoc='
                    <!DOCTYPE html>
                    <html style="background: rgb(14, 17, 23);">
                    <head>
                        <style>
                            body {{
                                margin: 0;
                                padding: 0;
                                background: rgb(14, 17, 23);
                                overflow-x: auto;
                                overflow-y: hidden;
                            }}
                            .scroll-container {{
                                display: flex;
                                gap: 1rem;
                                padding: 1rem 0;
                                overflow-x: auto;
                                scroll-behavior: smooth;
                                scrollbar-width: none;
                            }}
                            .scroll-container::-webkit-scrollbar {{
                                display: none;
                            }}
                            .channel-card {{
                                flex: 0 0 auto;
                                width: 280px;
                                text-decoration: none;
                            }}
                            .channel-card img {{
                                width: 100%;
                                border-radius: 8px;
                                aspect-ratio: 16/9;
                                object-fit: contain;
                                transition: transform 0.2s;
                            }}
                            .channel-card:hover img {{
                                transform: scale(1.05);
                            }}
                            .channel-title {{
                                color: white;
                                margin-top: 8px;
                                font-size: 14px;
                                text-align: left;
                                overflow: hidden;
                                text-overflow: ellipsis;
                                display: -webkit-box;
                                -webkit-line-clamp: 2;
                                -webkit-box-orient: vertical;
                                line-height: 1.2;
                                height: 2.4em;
                            }}
                            @media (max-width: 768px) {{
                                .channel-card {{
                                    width: 200px;
                                }}
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="scroll-container">
                ' 
                style="width: 100%; height: 100%; border: none; background: rgb(14, 17, 23);"
                >
                    {" ".join([f'''
                        <a href="https://youtube.com/channel/{channel["id"]}" target="_blank" class="channel-card">
                            <img src="{channel["thumbnail"]}" alt="{channel["name"]}">
                            <div class="channel-title">{channel["name"]}</div>
                        </a>
                    ''' for channel in channels])}
                </div>
                </body>
                </html>
                '
            ></iframe>
            </div>
        """
        
        # Renderizar usando components.html
        st.components.v1.html(html, height=int(total_height))

def main():
    # Carregar dados
    data = load_channels()
    categories = data.get("categories", {})
    
    # Menu lateral com categorias
    with st.sidebar:
        st.markdown("<h2 style='color: #E50914;'>Categorias</h2>", unsafe_allow_html=True)
        for cat_id, cat_info in categories.items():
            if st.button(
                f"{cat_info['name']}",
                key=f"cat_btn_{cat_id}",
                use_container_width=True
            ):
                st.session_state.selected_category = cat_id
    
    # Banner principal
    if "banners" in data and "cover" in data["banners"]:
        cover_banner = data["banners"]["cover"]
        banner_html = f"""
        <div class="banner-container">
        """
        
        # Pegar URL e link do banner
        if isinstance(cover_banner, dict):
            banner_url = cover_banner.get("url", "")
            banner_link = cover_banner.get("link", "")
        else:
            banner_url = cover_banner
            banner_link = ""
        
        # Se tiver link, adicionar tag <a>
        if banner_link:
            banner_html += f'<a href="{banner_link}" target="_blank">'
        
        banner_html += f"""
            <img src="{banner_url}" style="width:100%; max-height:300px; object-fit:cover;">
        """
        
        if banner_link:
            banner_html += '</a>'
        
        banner_html += '</div>'
        st.markdown(banner_html, unsafe_allow_html=True)
    
    # Banners promocionais
    if "banners" in data and "promotional" in data["banners"]:
        promotional = data["banners"]["promotional"]
        if promotional:
            st.markdown("### 🎯 Destaques")
            cols = st.columns(3)
            for i, banner in enumerate(promotional):
                with cols[i % 3]:
                    promo_html = ""
                    
                    # Pegar URL e link do banner
                    if isinstance(banner, dict):
                        banner_url = banner.get("url", "")
                        banner_link = banner.get("link", "")
                    else:
                        banner_url = banner
                        banner_link = ""
                    
                    # Se tiver link, adicionar tag <a>
                    if banner_link:
                        promo_html += f'<a href="{banner_link}" target="_blank">'
                    
                    promo_html += f'<img src="{banner_url}" style="width:100%; border-radius:8px;">'
                    
                    if banner_link:
                        promo_html += '</a>'
                    
                    st.markdown(promo_html, unsafe_allow_html=True)
    
    # Conteúdo principal - Removido título Studyflix que estava duplicado
    
    # Verificar categoria selecionada
    selected_category = st.session_state.get("selected_category", "vestibular")

    # Carregar dados dos canais
    data = load_channels()

    # Filtrar canais pela categoria selecionada
    filtered_data = {
        "featured_channels": [
            ch for ch in data.get("featured_channels", [])
            if ch.get("category") == selected_category
        ]
    }

    # Exibir canais
    display_channels(filtered_data)

    # Rodapé
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            Desenvolvido por <a href='https://x.com/danielstudytwt' target='_blank' style='color: #E50914;'>@danielstudytwt</a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
