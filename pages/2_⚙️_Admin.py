import streamlit as st
import json
from datetime import datetime
from utils.youtube_utils import get_youtube_client, get_channel_info, extract_channel_id
from utils.file_utils import load_channels, save_channels

# Configuração da página
st.set_page_config(page_title="Admin - Studyflix", page_icon="⚙️", layout="wide")

# Estilo personalizado
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
    
    .stApp {
        background-color: #141414 !important;
        color: white !important;
    }
    
    .admin-title {
        font-family: 'Bebas Neue', sans-serif;
        color: #E50914;
        font-size: 3em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 20px;
        text-align: center;
    }
    
    .category-card {
        background-color: #1f1f1f;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .channel-card {
        background-color: #1f1f1f;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #333;
    }
    
    .channel-card:hover {
        border-color: #E50914;
    }
    
    .success-msg {
        color: #4CAF50;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .error-msg {
        color: #f44336;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Estilo para forms */
    .stTextInput input {
        background-color: #333 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    
    .stTextInput input:focus {
        border-color: #E50914 !important;
        box-shadow: 0 0 0 1px #E50914 !important;
    }
    
    .stSelectbox select {
        background-color: #333 !important;
        color: white !important;
    }
    
    .stButton button {
        background-color: #E50914 !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        background-color: #ff0f1f !important;
        transform: translateY(-2px);
    }
    
    .secondary-button button {
        background-color: #333 !important;
    }
    
    .secondary-button button:hover {
        background-color: #444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def manage_categories():
    st.markdown("<h1 class='admin-title'>Gerenciar Categorias</h1>", unsafe_allow_html=True)
    
    # Carregar dados
    channels_data = load_channels()
    if "categories" not in channels_data:
        channels_data["categories"] = {}
    
    # Adicionar nova categoria
    st.markdown("### Adicionar Nova Categoria")
    with st.form(key="add_category"):
        col1, col2 = st.columns(2)
        with col1:
            cat_id = st.text_input("ID da Categoria (ex: vestibular)", 
                                 help="Use apenas letras e números, sem espaços",
                                 key="category_id_input")
        with col2:
            cat_name = st.text_input("Nome da Categoria (ex: Vestibular)",
                                   help="Nome que será exibido para os usuários",
                                   key="category_name_input")
        
        cat_desc = st.text_area("Descrição da Categoria",
                               help="Uma breve descrição do tipo de conteúdo desta categoria",
                               key="category_description_input")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Adicionar Categoria", use_container_width=True)
        
        if submit:
            cat_id = cat_id.lower().strip()
            if not cat_id or not cat_name:
                st.error("ID e Nome são obrigatórios!")
            elif not cat_id.isalnum():
                st.error("O ID deve conter apenas letras e números!")
            elif cat_id in channels_data["categories"]:
                st.error("Esta categoria já existe!")
            else:
                channels_data["categories"][cat_id] = {
                    "name": cat_name,
                    "description": cat_desc
                }
                save_channels(channels_data)
                st.success(f"Categoria '{cat_name}' adicionada com sucesso!")
                st.rerun()
    
    # Lista de categorias existentes
    st.markdown("### Categorias Existentes")
    
    if not channels_data["categories"]:
        st.info("Nenhuma categoria cadastrada ainda.")
        return
    
    for cat_id, category in channels_data["categories"].items():
        st.markdown(f"""
        <div class='category-card'>
            <h3>{category['name']} ({cat_id})</h3>
            <p>{category['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            with st.form(key=f"edit_{cat_id}"):
                new_name = st.text_input("Novo Nome", category["name"],
                                        key=f"edit_category_name_input_{cat_id}")
                new_desc = st.text_area("Nova Descrição", category["description"],
                                       key=f"edit_category_description_input_{cat_id}")
                if st.form_submit_button("Salvar Alterações", use_container_width=True):
                    if new_name:
                        channels_data["categories"][cat_id].update({
                            "name": new_name,
                            "description": new_desc
                        })
                        save_channels(channels_data)
                        st.success("Alterações salvas!")
                        st.rerun()
                    else:
                        st.error("O nome não pode ficar vazio!")
        
        with col2:
            with st.form(key=f"delete_{cat_id}"):
                st.markdown("### ")  # Espaço para alinhar com o outro form
                if st.form_submit_button("Remover Categoria", 
                                       use_container_width=True,
                                       type="secondary"):
                    # Verificar se há canais nesta categoria
                    has_channels = any(ch.get("category") == cat_id 
                                     for ch in channels_data.get("featured_channels", []))
                    if has_channels:
                        st.error("Não é possível remover uma categoria que possui canais!")
                    else:
                        channels_data["categories"].pop(cat_id)
                        save_channels(channels_data)
                        st.success("Categoria removida com sucesso!")
                        st.rerun()
        
        # Mostrar canais da categoria
        channels = [ch for ch in channels_data.get("featured_channels", []) 
                   if ch.get("category") == cat_id]
        if channels:
            st.markdown(f"##### Canais nesta categoria ({len(channels)}):")
            for channel in channels:
                col1, col2, col3 = st.columns([2,2,1])
                with col1:
                    st.write(f"**{channel['name']}**")
                with col2:
                    st.write(f"_{channel['subject']}_")
                with col3:
                    if st.button("🗑️", key=f"del_ch_{channel['id']}"):
                        channels_data["featured_channels"].remove(channel)
                        save_channels(channels_data)
                        st.success("Canal removido!")
                        st.rerun()
        else:
            st.info("Nenhum canal nesta categoria ainda.")
        
        st.markdown("---")

def manage_channels():
    st.markdown("<h1 class='admin-title'>Gerenciar Canais</h1>", unsafe_allow_html=True)
    
    channels_data = load_channels()
    if "categories" not in channels_data:
        st.error("Você precisa criar categorias primeiro!")
        return
    
    categories = channels_data["categories"]
    if not categories:
        st.error("Nenhuma categoria cadastrada. Adicione categorias primeiro!")
        return
    
    # Adicionar novo canal
    st.markdown("### Adicionar Novo Canal")
    with st.form("add_channel"):
        col1, col2 = st.columns(2)
        
        with col1:
            channel_url = st.text_input(
                "URL do Canal do YouTube",
                help="Cole a URL do canal que deseja adicionar",
                key="channel_url_input"
            )
            
            category = st.selectbox(
                "Categoria",
                options=list(categories.keys()),
                format_func=lambda x: f"{categories[x]['name']} ({x})",
                key="channel_category_select"
            )
        
        with col2:
            # Carregar matérias existentes
            existing_subjects = sorted(set(
                ch["subject"] for ch in channels_data.get("featured_channels", [])
                if "subject" in ch
            ))
            
            # Opção para usar matéria existente ou criar nova
            if existing_subjects:
                subject_type = st.radio(
                    "Tipo de Matéria",
                    options=["Usar Existente", "Criar Nova"],
                    horizontal=True,
                    key="subject_type_radio"
                )
                
                # Container para matéria existente
                existing_container = st.container()
                # Container para nova matéria
                new_container = st.container()
                
                if subject_type == "Usar Existente":
                    with existing_container:
                        subject = st.selectbox(
                            "Selecione a Matéria",
                            options=existing_subjects,
                            key="existing_subject_select"
                        )
                    new_container.empty()
                else:
                    with new_container:
                        subject = st.text_input(
                            "Nova Matéria",
                            help="Digite o nome da matéria (ex: Matemática, Física)",
                            key="new_subject_input"
                        )
                    existing_container.empty()
            else:
                subject = st.text_input(
                    "Nova Matéria",
                    help="Digite o nome da matéria (ex: Matemática, Física)",
                    key="new_subject_input_single"
                )
        
        submit = st.form_submit_button("Adicionar Canal", use_container_width=True)
        
        if submit:
            if not channel_url:
                st.error("Por favor, insira a URL do canal!")
                return
            
            if not subject:
                st.error("Por favor, selecione ou digite uma matéria!")
                return
            
            try:
                channel_id = extract_channel_id(channel_url)
                if not channel_id:
                    st.error("URL do canal inválida!")
                    return
                
                # Verificar se o canal já existe
                if any(ch.get("id") == channel_id 
                      for ch in channels_data.get("featured_channels", [])):
                    st.error("Este canal já está cadastrado!")
                    return
                
                with st.spinner("Obtendo informações do canal..."):
                    youtube = get_youtube_client()
                    channel_info = get_channel_info(youtube, channel_id)
                    
                    if not channel_info:
                        st.error("Não foi possível obter informações do canal!")
                        return
                    
                    new_channel = {
                        "id": channel_id,
                        "name": channel_info["title"],
                        "subject": subject,
                        "category": category,
                        "thumbnail": channel_info["thumbnail"],
                        "featured": False
                    }
                    
                    if "featured_channels" not in channels_data:
                        channels_data["featured_channels"] = []
                    
                    channels_data["featured_channels"].append(new_channel)
                    save_channels(channels_data)
                    st.success(f"Canal '{channel_info['title']}' adicionado com sucesso!")
                    st.rerun()
            
            except Exception as e:
                st.error(f"Erro ao adicionar canal: {str(e)}")
    
    # Lista de canais
    st.markdown("### Canais Cadastrados")
    
    channels = channels_data.get("featured_channels", [])
    if not channels:
        st.info("Nenhum canal cadastrado ainda.")
        return
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox(
            "Filtrar por Categoria",
            options=["Todas"] + list(categories.keys()),
            format_func=lambda x: "Todas" if x == "Todas" else categories[x]["name"],
            key="filter_category_select"
        )
    
    with col2:
        all_subjects = sorted(set(ch["subject"] for ch in channels))
        filter_subject = st.selectbox(
            "Filtrar por Matéria",
            options=["Todas"] + all_subjects,
            key="filter_subject_select"
        )
    
    # Aplicar filtros
    filtered_channels = channels
    if filter_category != "Todas":
        filtered_channels = [ch for ch in filtered_channels 
                           if ch["category"] == filter_category]
    if filter_subject != "Todas":
        filtered_channels = [ch for ch in filtered_channels 
                           if ch["subject"] == filter_subject]
    
    # Mostrar canais filtrados
    for channel in filtered_channels:
        st.markdown(f"""
        <div class='channel-card'>
            <div style='display: flex; align-items: center;'>
                <img src='{channel["thumbnail"]}' style='width: 48px; height: 48px; border-radius: 50%; margin-right: 15px;'>
                <div>
                    <h3 style='margin: 0;'>{channel["name"]}</h3>
                    <p style='margin: 5px 0; color: #999;'>{channel["subject"]} • {categories[channel["category"]]["name"]}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            with st.form(key=f"edit_channel_{channel['id']}"):
                new_name = st.text_input("Nome", channel["name"],
                                        key=f"edit_channel_name_input_{channel['id']}")
                new_subject = st.text_input("Matéria", channel["subject"],
                                           key=f"edit_channel_subject_input_{channel['id']}")
                new_category = st.selectbox(
                    "Categoria",
                    options=list(categories.keys()),
                    index=list(categories.keys()).index(channel["category"]),
                    format_func=lambda x: categories[x]["name"],
                    key=f"edit_channel_category_select_{channel['id']}"
                )
                
                if st.form_submit_button("Salvar Alterações", use_container_width=True):
                    if new_name and new_subject:
                        idx = channels_data["featured_channels"].index(channel)
                        channels_data["featured_channels"][idx].update({
                            "name": new_name,
                            "subject": new_subject,
                            "category": new_category
                        })
                        save_channels(channels_data)
                        st.success("Canal atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Nome e Matéria são obrigatórios!")
        
        with col2:
            with st.form(key=f"delete_channel_{channel['id']}"):
                st.markdown("### ")  # Espaço para alinhar com o outro form
                if st.form_submit_button("Remover Canal", 
                                       use_container_width=True,
                                       type="secondary"):
                    channels_data["featured_channels"].remove(channel)
                    save_channels(channels_data)
                    st.success("Canal removido com sucesso!")
                    st.rerun()
        
        st.markdown("---")

def main():
    st.markdown("<h1 class='admin-title'>Painel Administrativo</h1>", unsafe_allow_html=True)
    
    # Tabs para navegação
    tab1, tab2 = st.tabs(["📁 Categorias", "📺 Canais"])
    
    with tab1:
        manage_categories()
    
    with tab2:
        manage_channels()

if __name__ == "__main__":
    main()
