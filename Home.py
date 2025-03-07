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
    cursor: pointer;
    text-decoration: none;
    display: block;
}
.channel-card:hover {
    transform: scale(1.05);
    background-color: #282828;
    text-decoration: none;
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
.channel-title {
    color: white;
    margin-top: 10px;
    text-decoration: none;
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
                <a href="https://youtube.com/channel/{channel['id']}" target="_blank" class="channel-card">
                    <img src="{channel['thumbnail']}" style="width:100%; border-radius:5px;">
                    <h4 class="channel-title">{channel['name']}</h4>
                </a>
                """, unsafe_allow_html=True)

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
