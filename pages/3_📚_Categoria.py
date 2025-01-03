import streamlit as st
from utils.file_utils import load_channels

# Configuração da página
st.set_page_config(
    page_title="Studyflix - Categoria",
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
</style>
""", unsafe_allow_html=True)

def main():
    # Carregar dados
    data = load_channels()
    categories = data.get("categories", {})
    
    # Verificar se há uma categoria selecionada
    if "selected_category" not in st.session_state:
        st.error("Nenhuma categoria selecionada!")
        if st.button("Voltar para página inicial"):
            st.switch_page("Home.py")
        return
    
    category_id = st.session_state.selected_category
    category = categories.get(category_id)
    
    if not category:
        st.error("Categoria não encontrada!")
        if st.button("Voltar para página inicial"):
            st.switch_page("Home.py")
        return
    
    # Título da categoria
    st.markdown(f"<h1 class='netflix-title'>{category['name']}</h1>", unsafe_allow_html=True)
    st.markdown(f"*{category['description']}*")
    
    # Filtrar canais da categoria
    category_channels = [
        ch for ch in data.get("featured_channels", [])
        if ch.get("category") == category_id
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
                    st.switch_page(f"https://youtube.com/channel/{channel['id']}")

if __name__ == "__main__":
    main()
