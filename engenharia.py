import streamlit as st
from utils.file_utils import load_channels

def main():
    st.set_page_config(
        page_title="Engenharia - Studyflix",
        page_icon="🔧",
        layout="wide"
    )

    # Carregar dados
    data = load_channels()
    category = data["categories"].get("engenharia", {"channels": []})

    # Título da página
    st.title(f"📚 {category['name']}")
    st.markdown(f"*{category['description']}*")

    # Mostrar canais em grid
    if not category["channels"]:
        st.info("Ainda não há canais nesta categoria. Em breve adicionaremos mais conteúdo!")
        return

    # Agrupar canais por matéria
    subjects = {}
    for channel in category["channels"]:
        if channel["subject"] not in subjects:
            subjects[channel["subject"]] = []
        subjects[channel["subject"]].append(channel)

    # Mostrar canais por matéria
    for subject, channels in subjects.items():
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
