import streamlit as st
from utils.file_utils import load_channels

def main():
    st.set_page_config(
        page_title="Categoria - Studyflix",
        page_icon="📚",
        layout="wide"
    )

    # Pegar a categoria da URL
    query_params = st.experimental_get_query_params()
    category_id = query_params.get("categoria", [None])[0]

    if not category_id:
        st.error("Categoria não especificada!")
        return

    # Carregar dados
    data = load_channels()
    category_info = data["categories"].get(category_id)
    
    if not category_info:
        st.error("Categoria não encontrada!")
        return

    # Filtrar canais desta categoria
    category_channels = [
        ch for ch in data.get("featured_channels", [])
        if ch.get("category") == category_id
    ]

    # Título da página
    st.title(f"📚 {category_info['name']}")
    st.markdown(f"*{category_info['description']}*")

    # Mostrar canais em grid
    if not category_channels:
        st.info("Ainda não há canais nesta categoria. Em breve adicionaremos mais conteúdo!")
        return

    # Agrupar canais por matéria
    subjects = {}
    for channel in category_channels:
        if channel["subject"] not in subjects:
            subjects[channel["subject"]] = []
        subjects[channel["subject"]].append(channel)

    # Mostrar canais por matéria
    for subject, channels in sorted(subjects.items()):
        st.header(subject)
        cols = st.columns(4)
        for idx, channel in enumerate(channels):
            with cols[idx % 4]:
                st.image(channel["thumbnail"], use_column_width=True)
                st.markdown(f"**{channel['name']}**")
                if st.button("Ver Canal", key=f"btn_{channel['id']}"):
                    st.switch_page(f"https://youtube.com/channel/{channel['id']}")

if __name__ == "__main__":
    main()
