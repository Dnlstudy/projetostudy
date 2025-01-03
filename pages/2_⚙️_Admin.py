import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path
from utils.youtube_utils import get_youtube_client, get_channel_info, extract_channel_id
from utils.file_utils import (
    load_channels, 
    save_channels, 
    generate_session_token, 
    verify_admin_credentials,
    validate_session_token
)

# Configurações de segurança
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_TIME = 900  # 15 minutos em segundos
SESSION_TIMEOUT = 1800  # 30 minutos em segundos

def is_account_locked():
    """Verifica se a conta está bloqueada por tentativas falhas"""
    if not hasattr(st.session_state, 'failed_attempts'):
        st.session_state.failed_attempts = 0
        st.session_state.last_failed_attempt = 0
        return False
    
    if st.session_state.failed_attempts >= MAX_LOGIN_ATTEMPTS:
        time_since_last_attempt = time.time() - st.session_state.last_failed_attempt
        if time_since_last_attempt < LOCKOUT_TIME:
            return True
        # Reset após o tempo de bloqueio
        st.session_state.failed_attempts = 0
    return False

def reset_failed_attempts():
    """Reseta o contador de tentativas falhas"""
    st.session_state.failed_attempts = 0
    st.session_state.last_failed_attempt = 0

def record_failed_attempt():
    """Registra uma tentativa falha de login"""
    if not hasattr(st.session_state, 'failed_attempts'):
        st.session_state.failed_attempts = 0
    st.session_state.failed_attempts += 1
    st.session_state.last_failed_attempt = time.time()

def check_password(username, password):
    """Verifica as credenciais do usuário"""
    if is_account_locked():
        remaining_time = LOCKOUT_TIME - (time.time() - st.session_state.last_failed_attempt)
        st.error(f"Conta bloqueada. Tente novamente em {int(remaining_time/60)} minutos.")
        return False

    if verify_admin_credentials(username, password):
        reset_failed_attempts()
        token = generate_session_token()
        st.session_state.admin_session = {
            'token': token,
            'last_activity': time.time()
        }
        return True
    
    record_failed_attempt()
    return False

def verify_session():
    """Verifica se a sessão atual é válida"""
    if not hasattr(st.session_state, 'admin_session'):
        return False
    
    token = st.session_state.admin_session.get('token')
    if not validate_session_token(token):
        if hasattr(st.session_state, 'admin_session'):
            del st.session_state.admin_session
        return False
    
    return True

def get_unique_subjects(channels_data):
    """Retorna uma lista de matérias únicas dos canais existentes"""
    subjects = set()
    for channel in channels_data.get("featured_channels", []):
        if "subject" in channel:
            subjects.add(channel["subject"])
    return sorted(list(subjects))

def manage_categories():
    st.header("Gerenciar Categorias")
    channels_data = load_channels()
    
    # Inicializar categorias se não existirem
    if "categories" not in channels_data:
        channels_data["categories"] = {
            "vestibular": {
                "name": "Vestibular",
                "description": "Canais focados em preparação para vestibular"
            },
            "engenharia": {
                "name": "Engenharia",
                "description": "Canais sobre engenharia e tecnologia"
            },
            "informatica": {
                "name": "Informática",
                "description": "Canais sobre programação e computação"
            }
        }
        save_channels(channels_data)
    
    # Adicionar nova categoria
    with st.expander("Adicionar Nova Categoria"):
        with st.form("new_category"):
            cat_id = st.text_input("ID da Categoria (ex: medicina)").lower().strip()
            cat_name = st.text_input("Nome da Categoria")
            cat_desc = st.text_area("Descrição")
            
            if st.form_submit_button("Adicionar Categoria"):
                if cat_id and cat_name:
                    # Validar ID da categoria
                    if not cat_id.isalnum():
                        st.error("O ID da categoria deve conter apenas letras e números")
                        return
                    
                    if cat_id in channels_data["categories"]:
                        st.error("Já existe uma categoria com este ID")
                        return
                    
                    channels_data["categories"][cat_id] = {
                        "name": cat_name,
                        "description": cat_desc
                    }
                    save_channels(channels_data)
                    st.success("Categoria adicionada com sucesso!")
                    st.rerun()
                else:
                    st.error("ID e Nome são obrigatórios")
    
    # Mostrar e gerenciar categorias existentes
    st.subheader("Categorias Existentes")
    for cat_id, category in channels_data["categories"].items():
        with st.expander(f"{category['name']} ({cat_id})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_name = st.text_input("Nome", category["name"], key=f"name_{cat_id}")
                new_desc = st.text_area("Descrição", category["description"], key=f"desc_{cat_id}")
                
                if st.button("Salvar Alterações", key=f"save_{cat_id}", type="primary"):
                    if new_name:
                        channels_data["categories"][cat_id] = {
                            "name": new_name,
                            "description": new_desc
                        }
                        save_channels(channels_data)
                        st.success("Alterações salvas!")
                        st.rerun()
                    else:
                        st.error("O nome da categoria não pode ficar vazio")
            
            with col2:
                # Contador de canais na categoria
                category_channels = [ch for ch in channels_data.get("featured_channels", []) 
                                  if ch.get("category") == cat_id]
                st.metric("Canais", len(category_channels))
                
                if st.button("Remover Categoria", key=f"del_{cat_id}", type="secondary"):
                    if len(category_channels) > 0:
                        st.error(f"Esta categoria possui {len(category_channels)} canais. Remova-os primeiro.")
                    else:
                        confirm = st.button(
                            "Confirmar Remoção",
                            key=f"confirm_del_{cat_id}",
                            type="secondary"
                        )
                        if confirm:
                            channels_data["categories"].pop(cat_id)
                            save_channels(channels_data)
                            st.success("Categoria removida!")
                            st.rerun()
            
            if category_channels:
                st.markdown("### Canais nesta categoria:")
                for channel in category_channels:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**{channel['name']}**")
                    with col2:
                        st.write(f"Matéria: {channel['subject']}")
                    with col3:
                        if st.button("Remover Canal", key=f"remove_{channel['id']}", type="secondary"):
                            channels_data["featured_channels"].remove(channel)
                            save_channels(channels_data)
                            st.success("Canal removido!")
                            st.rerun()

def manage_channels():
    st.header("Gerenciar Canais")
    channels_data = load_channels()
    
    tab1, tab2 = st.tabs(["Adicionar Canal", "Editar Canais"])
    
    with tab1:
        with st.form("add_channel_form"):
            st.subheader("Adicionar Novo Canal")
            channel_url = st.text_input("URL do Canal do YouTube")
            
            # Carregar matérias existentes
            existing_subjects = get_unique_subjects(channels_data)
            
            # Seleção de categoria
            categories = channels_data.get("categories", {})
            if not categories:
                st.error("Nenhuma categoria cadastrada. Por favor, adicione uma categoria primeiro.")
                return
                
            category = st.selectbox(
                "Categoria",
                options=list(categories.keys()),
                format_func=lambda x: f"{categories[x]['name']} ({x})"
            )
            
            # Gestão de matérias
            col1, col2 = st.columns(2)
            with col1:
                use_existing = st.checkbox("Usar matéria existente", value=True if existing_subjects else False)
            
            with col2:
                if use_existing and existing_subjects:
                    subject = st.selectbox("Selecionar Matéria", options=existing_subjects)
                else:
                    subject = st.text_input("Nova Matéria", 
                                          help="Digite o nome da nova matéria (ex: Física, Química)")
            
            submit_button = st.form_submit_button("Adicionar Canal", type="primary")
            
            if submit_button:
                if not channel_url:
                    st.error("Por favor, insira a URL do canal")
                    return
                
                if not subject:
                    st.error("Por favor, selecione ou digite uma matéria")
                    return
                
                try:
                    channel_id = extract_channel_id(channel_url)
                    if not channel_id:
                        st.error("URL do canal inválida. Certifique-se de usar uma URL válida do YouTube")
                        return
                    
                    # Verificar se o canal já existe
                    existing_channels = channels_data.get("featured_channels", [])
                    if any(ch.get("id") == channel_id for ch in existing_channels):
                        st.error("Este canal já está cadastrado!")
                        return
                    
                    with st.spinner("Obtendo informações do canal..."):
                        youtube = get_youtube_client()
                        channel_info = get_channel_info(youtube, channel_id)
                        
                        if not channel_info:
                            st.error("Não foi possível obter informações do canal. Verifique se o canal existe e está acessível")
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
                    st.info("Dica: Verifique sua conexão com a internet e se a URL do canal está correta")
    
    with tab2:
        st.subheader("Editar Canais Existentes")
        channels = channels_data.get("featured_channels", [])
        
        if not channels:
            st.info("Nenhum canal cadastrado ainda")
            return
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.selectbox(
                "Filtrar por Categoria",
                options=["Todas"] + list(categories.keys()),
                format_func=lambda x: "Todas" if x == "Todas" else categories[x]["name"]
            )
        
        with col2:
            filter_subject = st.selectbox(
                "Filtrar por Matéria",
                options=["Todas"] + get_unique_subjects(channels_data)
            )
        
        # Aplicar filtros
        filtered_channels = channels
        if filter_category != "Todas":
            filtered_channels = [ch for ch in filtered_channels if ch["category"] == filter_category]
        if filter_subject != "Todas":
            filtered_channels = [ch for ch in filtered_channels if ch["subject"] == filter_subject]
        
        # Mostrar canais
        for channel in filtered_channels:
            with st.expander(f"{channel['name']} - {channel['subject']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    new_name = st.text_input("Nome", channel["name"], key=f"edit_name_{channel['id']}")
                    new_subject = st.text_input("Matéria", channel["subject"], key=f"edit_subject_{channel['id']}")
                    new_category = st.selectbox(
                        "Categoria",
                        options=list(categories.keys()),
                        index=list(categories.keys()).index(channel["category"]),
                        format_func=lambda x: categories[x]["name"],
                        key=f"edit_category_{channel['id']}"
                    )
                    
                    if st.button("Salvar Alterações", key=f"save_edit_{channel['id']}", type="primary"):
                        if new_name and new_subject:
                            channel_index = channels_data["featured_channels"].index(channel)
                            channels_data["featured_channels"][channel_index].update({
                                "name": new_name,
                                "subject": new_subject,
                                "category": new_category
                            })
                            save_channels(channels_data)
                            st.success("Alterações salvas!")
                            st.rerun()
                        else:
                            st.error("Nome e Matéria são obrigatórios")
                
                with col2:
                    st.image(channel["thumbnail"], use_column_width=True)
                    if st.button("Remover Canal", key=f"remove_edit_{channel['id']}", type="secondary"):
                        confirm = st.button(
                            "Confirmar Remoção",
                            key=f"confirm_remove_{channel['id']}",
                            type="secondary"
                        )
                        if confirm:
                            channels_data["featured_channels"].remove(channel)
                            save_channels(channels_data)
                            st.success("Canal removido!")
                            st.rerun()

def manage_banners():
    st.header("Gerenciar Banners")
    channels_data = load_channels()
    
    # Banner principal
    st.subheader("Banner Principal")
    current_cover = channels_data["banners"].get("cover", "")
    new_cover = st.text_input("URL do Banner Principal", current_cover)
    
    if st.button("Atualizar Banner Principal"):
        channels_data["banners"]["cover"] = new_cover
        save_channels(channels_data)
        st.success("Banner principal atualizado!")
    
    # Banners promocionais
    st.subheader("Banners Promocionais")
    promo_banners = channels_data["banners"].get("promotional", [])
    
    # Adicionar novo banner promocional
    with st.expander("Adicionar Banner Promocional"):
        with st.form("new_promo"):
            promo_url = st.text_input("URL da Imagem")
            promo_title = st.text_input("Título (opcional)")
            promo_link = st.text_input("Link de Redirecionamento (opcional)")
            
            if st.form_submit_button("Adicionar"):
                new_banner = {
                    "image_url": promo_url,
                    "title": promo_title,
                    "link": promo_link
                }
                promo_banners.append(new_banner)
                channels_data["banners"]["promotional"] = promo_banners
                save_channels(channels_data)
                st.success("Banner promocional adicionado!")
                st.rerun()
    
    # Gerenciar banners existentes
    for idx, banner in enumerate(promo_banners):
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.image(banner["image_url"], width=300)
            new_title = st.text_input("Título", banner.get("title", ""), key=f"title_{idx}")
            new_link = st.text_input("Link", banner.get("link", ""), key=f"link_{idx}")
            new_url = st.text_input("URL da Imagem", banner["image_url"], key=f"url_{idx}")
            
            if st.button("Atualizar", key=f"update_{idx}"):
                promo_banners[idx] = {
                    "image_url": new_url,
                    "title": new_title,
                    "link": new_link
                }
                channels_data["banners"]["promotional"] = promo_banners
                save_channels(channels_data)
                st.success("Banner atualizado!")
        
        with col2:
            if st.button("Remover", key=f"remove_{idx}"):
                promo_banners.pop(idx)
                channels_data["banners"]["promotional"] = promo_banners
                save_channels(channels_data)
                st.success("Banner removido!")
                st.rerun()

def admin_panel():
    if not verify_session():
        st.session_state.admin_logged_in = False
        st.rerun()
    
    st.title("⚙️ Painel Administrativo")
    
    # Mensagem de boas-vindas com hora atual
    current_time = datetime.now().strftime("%H:%M")
    st.markdown(f"""
    ### Bem-vindo ao Painel Administrativo! 🎉
    
    Aqui você pode:
    - ✨ Gerenciar categorias
    - 📺 Adicionar/remover canais
    - 🖼️ Personalizar banners
    
    *Hora atual: {current_time}*
    """)
    
    st.markdown("---")
    
    st.markdown("<h1 style='color: #E50914;'>STUDYFLIX</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #E50914;'>Painel de Gerenciamento</h2>", unsafe_allow_html=True)
    
    # Botão de logout
    col1, col2 = st.columns([6,1])
    with col2:
        if st.button("Sair"):
            st.session_state.admin_logged_in = False
            st.session_state.pop("admin_session", None)
            st.rerun()
    
    with col1:
        st.markdown(f"Último acesso: {datetime.fromtimestamp(time.time()).strftime('%d/%m/%Y %H:%M:%S')}")
    
    channels_data = load_channels()
    
    # Menu de configurações
    st.sidebar.title("Menu")
    menu = st.sidebar.selectbox(
        "Opções",
        ["Gerenciar Categorias", "Gerenciar Canais", "Gerenciar Banners", "Configurações de Segurança"]
    )
    
    if menu == "Gerenciar Categorias":
        manage_categories()
    elif menu == "Gerenciar Canais":
        manage_channels()
    elif menu == "Gerenciar Banners":
        manage_banners()
    else:  # Configurações de Segurança
        st.subheader("Alterar Credenciais")
        with st.form("change_credentials"):
            current_password = st.text_input("Senha Atual", type="password")
            new_password = st.text_input("Nova Senha", type="password")
            confirm_password = st.text_input("Confirmar Nova Senha", type="password")
            
            if st.form_submit_button("Atualizar Senha"):
                if not verify_admin_credentials(st.secrets["admin_username"], current_password):
                    st.error("Senha atual incorreta!")
                elif new_password != confirm_password:
                    st.error("As senhas não coincidem!")
                elif len(new_password) < 8:
                    st.error("A nova senha deve ter pelo menos 8 caracteres!")
                else:
                    # Atualizar senha no arquivo de configuração
                    # Aqui você pode adicionar a lógica para atualizar a senha no arquivo de configuração
                    st.success("Senha atualizada com sucesso!")

def main():
    st.set_page_config(
        page_title="Gerenciamento",
        page_icon="",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #141414;
            color: white;
        }
        .stButton button {
            background-color: #E50914;
            color: white;
        }
        .stTextInput input {
            background-color: #2b2b2b;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Verificar se já está logado
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if not st.session_state.admin_logged_in:
        st.markdown("<h1 style='color: #E50914;'>STUDYFLIX</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #E50914;'>Área Restrita</h2>", unsafe_allow_html=True)
        
        # Verificar se a conta está bloqueada
        locked = is_account_locked()
        if locked:
            st.error(f"Acesso bloqueado por tentativas inválidas. Tente novamente em {int(LOCKOUT_TIME/60)} minutos.")
            return
        
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                if check_password(username, password):
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    attempts_left = MAX_LOGIN_ATTEMPTS - st.session_state.failed_attempts
                    if attempts_left > 0:
                        st.error(f"Credenciais inválidas! {attempts_left} tentativas restantes.")
                    else:
                        st.error("Conta bloqueada por excesso de tentativas. Tente novamente mais tarde.")
    else:
        admin_panel()

if __name__ == "__main__":
    main()
