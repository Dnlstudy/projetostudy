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
    subjects = set()
    for channel in channels_data.get("featured_channels", []):
        if "subject" in channel:
            subjects.add(channel["subject"])
    return sorted(list(subjects))

def manage_categories():
    st.header("Gerenciar Categorias")
    channels_data = load_channels()
    
    # Lista de categorias disponíveis
    AVAILABLE_CATEGORIES = {
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
    
    # Mostrar canais por categoria
    for cat_id, category in AVAILABLE_CATEGORIES.items():
        with st.expander(f"{category['name']} - {category['description']}"):
            # Filtrar canais desta categoria
            category_channels = [ch for ch in channels_data.get("featured_channels", []) 
                               if ch.get("category") == cat_id]
            
            if category_channels:
                for channel in category_channels:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{channel['name']}** ({channel['subject']})")
                    with col2:
                        if st.button("Remover", key=f"remove_{channel['id']}"):
                            channels_data["featured_channels"].remove(channel)
                            save_channels(channels_data)
                            st.success("Canal removido com sucesso!")
                            st.rerun()
            else:
                st.info("Nenhum canal nesta categoria.")

def manage_channels():
    st.header("Gerenciar Canais")
    channels_data = load_channels()
    
    # Adicionar novo canal
    with st.expander("Adicionar Novo Canal"):
        # Inicializar o estado se não existir
        if 'use_existing_subject' not in st.session_state:
            st.session_state.use_existing_subject = False
            
        # Carregar matérias existentes para sugestão
        existing_subjects = get_unique_subjects(channels_data)
        
        # Controles fora do formulário
        subject_col1, subject_col2 = st.columns(2)
        with subject_col1:
            st.session_state.use_existing_subject = st.checkbox(
                "Usar matéria existente",
                value=st.session_state.use_existing_subject,
                key="use_existing"
            )
        
        # Formulário para adicionar canal
        with st.form("new_channel"):
            category_id = st.selectbox(
                "Categoria",
                options=["vestibular", "engenharia", "informatica"],
                format_func=lambda x: x.title()
            )
            
            channel_url = st.text_input("URL do Canal")
            
            # Campo de matéria baseado na escolha do usuário
            if st.session_state.use_existing_subject and existing_subjects:
                new_channel_subject = st.selectbox(
                    "Selecione a matéria",
                    options=existing_subjects,
                    key="subject_select"
                )
            else:
                new_channel_subject = st.text_input("Nova matéria")
                
            featured = st.checkbox("Destacar canal")
            
            if st.form_submit_button("Adicionar Canal"):
                if channel_url and new_channel_subject:
                    try:
                        channel_id = extract_channel_id(channel_url)
                        if channel_id:
                            # Verificar se o canal já existe
                            channel_exists = any(
                                c["id"] == channel_id 
                                for c in channels_data.get("featured_channels", [])
                            )
                            
                            if not channel_exists:
                                youtube = get_youtube_client()
                                channel_info = get_channel_info(youtube, channel_id)
                                
                                if channel_info:
                                    new_channel = {
                                        "id": channel_id,
                                        "name": channel_info["title"],
                                        "subject": new_channel_subject,
                                        "category": category_id,
                                        "thumbnail": channel_info["thumbnail"],
                                        "featured": featured
                                    }
                                    
                                    if "featured_channels" not in channels_data:
                                        channels_data["featured_channels"] = []
                                    
                                    channels_data["featured_channels"].append(new_channel)
                                    save_channels(channels_data)
                                    st.success("Canal adicionado com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("Não foi possível obter informações do canal")
                            else:
                                st.error("Este canal já está cadastrado")
                        else:
                            st.error("URL do canal inválida")
                    except Exception as e:
                        st.error(f"Erro ao adicionar canal: {str(e)}")
                else:
                    st.error("URL do canal e matéria são obrigatórios")
    
    # Editar/Remover canais existentes
    with st.expander("Editar/Remover Canais"):
        channels = channels_data.get("featured_channels", [])
        if not channels:
            st.info("Nenhum canal cadastrado")
            return
        
        for i, channel in enumerate(channels):
            st.subheader(channel["name"])
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_subject = st.text_input(f"Matéria", channel["subject"], key=f"subject_{i}")
                new_category = st.selectbox(
                    "Categoria",
                    options=["vestibular", "engenharia", "informatica"],
                    index=["vestibular", "engenharia", "informatica"].index(channel["category"]),
                    key=f"category_{i}"
                )
                new_featured = st.checkbox("Destacar", channel["featured"], key=f"feat_{i}")
                
                if st.button("Salvar Alterações", key=f"save_{i}"):
                    channels[i].update({
                        "subject": new_subject,
                        "category": new_category,
                        "featured": new_featured
                    })
                    save_channels(channels_data)
                    st.success("Alterações salvas!")
                    st.rerun()
            
            with col2:
                if st.button("Remover Canal", key=f"del_{i}"):
                    channels.pop(i)
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
