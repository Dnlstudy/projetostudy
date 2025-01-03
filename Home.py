import streamlit as st
from utils.file_utils import load_channels
import webbrowser

# Configuração da página - DEVE ser a primeira chamada Streamlit
st.set_page_config(
    page_title="Studyflix",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.netflix-title {
    color: #E50914;
    font-size: 48px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 30px;
}
.subject-title {
    color: white;
    font-size: 24px;
    margin-top: 20px;
    margin-bottom: 10px;
}
.channel-card {
    background-color: #181818;
    padding: 10px;
    border-radius: 5px;
    margin: 5px;
    transition: transform 0.2s;
}
.channel-card:hover {
    transform: scale(1.05);
    background-color: #282828;
}
.banner-container {
    position: relative;
    text-align: center;
    margin-bottom: 30px;
}
.banner-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 36px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
}
.category-card {
    background-color: #181818;
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 10px;
}
.category-card:hover {
    background-color: #282828;
}
</style>
""", unsafe_allow_html=True)

def show_category(category_id, category_data):
    st.markdown(f"<h2 style='color: #E50914;'>{category_data['name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"*{category_data['description']}*")

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
        st.markdown(f"""
        <div class="banner-container">
            <img src="{data['banners']['cover']}" style="width:100%; max-height:300px; object-fit:cover;">
            <div class="banner-text">Bem-vindo ao Studyflix</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='netflix-title'>Studyflix</h1>", unsafe_allow_html=True)
    
    # Verificar categoria selecionada
    selected_category = st.session_state.get("selected_category", "vestibular")
    
    if selected_category in categories:
        category = categories[selected_category]
        st.markdown(f"<h2 style='color: #E50914;'>{category['name']}</h2>", unsafe_allow_html=True)
        st.markdown(f"*{category['description']}*")
    
    # Filtrar canais da categoria selecionada
    category_channels = [
        ch for ch in data.get("featured_channels", [])
        if ch.get("category") == selected_category
    ]
    
    if not category_channels:
        st.info("Ainda não há canais nesta categoria.")
        return
    
    # Agrupar canais por matéria
    subjects = {}
    for channel in category_channels:
        if channel["subject"] not in subjects:
            subjects[channel["subject"]] = []
        subjects[channel["subject"]].append(channel)
    
    # Mostrar canais por matéria
    for subject, channels in sorted(subjects.items()):
        st.markdown(f"<h2 class='subject-title'>{subject}</h2>", unsafe_allow_html=True)
        cols = st.columns(4)
        for idx, channel in enumerate(channels):
            with cols[idx % 4]:
                st.markdown(f"""
                <div class='channel-card'>
                    <img src="{channel['thumbnail']}" style="width:100%; border-radius:5px;">
                    <h4 style="color:white; margin-top:10px;">{channel['name']}</h4>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Ver Canal", key=f"btn_{channel['id']}"):
                    webbrowser.open(f"https://youtube.com/channel/{channel['id']}")

if __name__ == "__main__":
    main()
