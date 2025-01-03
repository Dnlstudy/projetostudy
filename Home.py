import streamlit as st
from utils.file_utils import load_channels
import webbrowser

st.set_page_config(
    page_title="Studyflix",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Forçar tema escuro
st.markdown("""
    <script>
        var observer = new MutationObserver(function(mutations) {
            if (document.querySelector('.stApp')) {
                document.querySelector('.stApp').classList.add('dark');
                observer.disconnect();
            }
        });
        
        observer.observe(document, {childList: true, subtree: true});
    </script>
""", unsafe_allow_html=True)

# Custom CSS for Netflix-like styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
    
    .stApp {
        background-color: #141414 !important;
        color: white !important;
    }
    .netflix-title {
        font-family: 'Bebas Neue', sans-serif;
        color: #E50914;
        font-size: 4em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 30px;
    }
    .subject-title {
        color: white;
        font-size: 1.5em;
        font-weight: bold;
        margin: 20px 0 10px 0;
    }
    .featured-channel {
        position: relative;
        transition: transform .3s;
        margin: 10px;
    }
    .featured-channel:hover {
        transform: scale(1.05);
        z-index: 1;
    }
    .channel-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(transparent, rgba(0,0,0,0.8));
        padding: 20px 10px;
        color: white;
    }
    .banner-container {
        width: 100%;
        margin: 0 0 30px 0;
        position: relative;
    }
    .banner-container img {
        width: 100%;
        height: auto;
        object-fit: cover;
    }
    .cover-banner {
        width: 100%;
        height: 600px;
        object-fit: cover;
        margin-bottom: 30px;
    }
    
    /* Forçar tema escuro em elementos específicos */
    .stButton button {
        background-color: #333 !important;
        color: white !important;
    }
    .stButton button:hover {
        background-color: #444 !important;
    }
    .stMarkdown {
        color: white !important;
    }
    .st-emotion-cache-1gulkj5 {
        background-color: #141414 !important;
    }
    </style>
""", unsafe_allow_html=True)

def show_category(category_id, category_data):
    """Mostra os canais de uma categoria específica"""
    st.title(f"📚 {category_data['name']}")
    
    # Se não houver canais, mostrar mensagem
    channels = category_data.get("channels", [])
    if not channels:
        st.info("Ainda não há canais nesta categoria. Em breve!")
        return
    
    # Agrupar canais por matéria
    subjects = {}
    for channel in channels:
        subject = channel.get("subject", "Geral")
        if subject not in subjects:
            subjects[subject] = []
        subjects[subject].append(channel)
    
    # Mostrar canais por matéria
    for subject, subject_channels in subjects.items():
        st.markdown(f"<h2 style='color: #E50914;'>{subject}</h2>", unsafe_allow_html=True)
        cols = st.columns(4)
        for idx, channel in enumerate(subject_channels):
            with cols[idx % 4]:
                st.markdown(f'''
                    <div class="featured-channel">
                        <a href="https://www.youtube.com/channel/{channel['id']}" target="_blank">
                            <img src="{channel.get('thumbnail', '')}" width="100%">
                            <div class="channel-overlay">
                                <h3>{channel.get('name', 'Canal')}</h3>
                            </div>
                        </a>
                    </div>
                ''', unsafe_allow_html=True)
        
        # Separador entre matérias
        st.markdown("<hr style='margin: 30px 0; border-color: #333;'>", unsafe_allow_html=True)

def main():
    # Carregar dados
    data = load_channels()
    
    # Definir categorias
    categories = {
        "vestibular": {
            "name": "Vestibular",
            "description": "Canais focados em preparação para vestibular",
            "channels": [ch for ch in data.get("featured_channels", []) if ch.get("category") == "vestibular"]
        },
        "engenharia": {
            "name": "Engenharia",
            "description": "Canais sobre engenharia e tecnologia",
            "channels": []  # Por enquanto não temos canais nesta categoria
        },
        "informatica": {
            "name": "Informática",
            "description": "Canais sobre programação e computação",
            "channels": [ch for ch in data.get("featured_channels", []) if ch.get("category") == "informatica"]
        }
    }
    
    # Menu lateral com categorias
    with st.sidebar:
        st.title("📚 Categorias")
        
        # Ícones para cada categoria
        category_icons = {
            "vestibular": "📝",
            "engenharia": "⚙️",
            "informatica": "💻",
        }
        
        # Ordenar categorias alfabeticamente pelo nome
        sorted_categories = sorted(
            categories.items(),
            key=lambda x: x[1]["name"]
        )
        
        for cat_id, category in sorted_categories:
            icon = category_icons.get(cat_id, "📚")
            if st.button(f"{icon} {category['name']}", key=f"menu_{cat_id}"):
                st.session_state.category = cat_id
                st.rerun()
    
    # Verificar categoria selecionada
    selected_category = st.session_state.get("category", "vestibular")
    
    # Se não estiver na página inicial, mostrar a categoria selecionada
    if selected_category != "vestibular":
        show_category(selected_category, categories[selected_category])
        return
    
    # Página inicial (vestibular)
    # Banner principal
    if "banners" in data and "cover" in data["banners"]:
        st.markdown(f"""
            <div class="banner-container">
                <img src="{data['banners']['cover']}" class="cover-banner">
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='netflix-title'>Studyflix</h1>", unsafe_allow_html=True)
    
    # Mostrar categorias em cards
    for cat_id, category in categories.items():
        with st.container():
            st.markdown(f"""
            <div class='category-card'>
                <h3>{category['name']}</h3>
                <p>{category['description']}</p>
                <a href="?page=3_📚_Categoria&categoria={cat_id}" target="_self">
                    <button>Ver Canais</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    # Mostrar canais em destaque
    featured_channels = [c for c in data.get("featured_channels", []) if c.get("featured", False)]
    if featured_channels:
        st.markdown("<h2 style='color: #E50914;'>Destaques</h2>", unsafe_allow_html=True)
        cols = st.columns(4)
        for idx, channel in enumerate(featured_channels):
            with cols[idx % 4]:
                st.markdown(f'''
                    <div class="featured-channel">
                        <a href="https://www.youtube.com/channel/{channel['id']}" target="_blank">
                            <img src="{channel['thumbnail']}" width="100%">
                            <div class="channel-overlay">
                                <h3>{channel['name']}</h3>
                                <p>{channel.get('description', '')}</p>
                            </div>
                        </a>
                    </div>
                ''', unsafe_allow_html=True)
    
    # Mostrar todos os canais da categoria vestibular
    show_category("vestibular", categories["vestibular"])

if __name__ == "__main__":
    main()
