import streamlit as st
import anthropic
import base64
from PIL import Image
import io
import time
from datetime import datetime

# ===== CONFIGURAÇÃO DA API =====
API_KEY = st.secrets["API_KEY"]

# ===== TEMPLATES DE MINUTAS =====
TEMPLATES_MINUTAS = {
    "Procuração para Negócio Consigo Mesmo": """PROCURAÇÃO PARA NEGÓCIO CONSIGO MESMO (AUTOCONTRATO)
 
PROCURAÇÃO BASTANTE QUE FAZEM
XXXXXXXXXXX E XXXXXXXXXXX, NA FORMA ABAIXO:
.""",
    
    "Escritura de Compra e Venda": """ESCRITURA PÚBLICA DE COMPRA E VENDA DE IMÓVEL
outorgam e assinam.""",
    
    "Procuração Ad Judicia": """PROCURAÇÃO AD JUDICIA
disse e me pediu este instrumento que lhe lavrei, lido, achado conforme, aceita, outorga e assina.""",
    
    "Escritura de Doação": """ESCRITURA PÚBLICA DE DOAÇÃO
 
SAIBAM quantos esta pública escritura de doação virem que aos XXXXXXXXXXX dias do mês de XXXXXXXXXXX do ano de XXXXXXXXXXX, nesta cidade de XXXXXXXXXXX, Estado de Minas Gerais, em meu Cartório, perante mim, XXXXXXXXXXX, compareceram as partes entre si justas e contratadas:

DOADOR(A): XXXXXXXXXXX (qualificar completamente)
DONATÁRIO(A): XXXXXXXXXXX (qualificar completamente)

Reconheço a identidade dos comparecentes pelos documentos apresentados e dou fé de que são capazes. Pelo(a) DOADOR(A) me foi dito que é senhor(a) e legítimo(a) possuidor(a) do imóvel situado XXXXXXXXXXX, com as características descritas na matrícula nº XXXXXXXXXXX do Cartório de Registro de Imóveis XXXXXXXXXXX, e que por mera liberalidade e sem qualquer encargo, pelo presente instrumento faz DOAÇÃO PURA E SIMPLES do referido imóvel ao DONATÁRIO, que aceita a doação. Fica desde já transmitida ao DONATÁRIO a posse, domínio e todos os direitos sobre o imóvel objeto desta escritura. O DOADOR se obriga pela evicção de direito. O imóvel ora doado encontra-se livre e desembaraçado de quaisquer ônus reais. Assim o disseram e me pediram esta escritura que lhes lavrei, lida, achada conforme, aceitam, outorgam e assinam."""
}

# Configuração da página
st.set_page_config(
    page_title="Claude 4 Chat Cartorial",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🏛️"
)

# CSS moderno com melhorias visuais
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Remove padding padrão do Streamlit */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        max-width: 100%;
        font-family: 'Inter', sans-serif;
    }
    
    /* Container principal */
    .main-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
    }
    
    /* Header com gradiente e sombra */
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .chat-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        letter-spacing: -0.5px;
    }
    
    .chat-subtitle {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Chat container */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 0;
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Mensagens com animações */
    .message-container {
        width: 100%;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
        animation: slideInUp 0.4s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message-content {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem;
        display: flex;
        gap: 1.5rem;
        align-items: flex-start;
    }
    
    .user-message {
        background: linear-gradient(135deg, #3b4371 0%, #4a5d7a 100%);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #2d4a5a 0%, #3a5f6f 100%);
    }
    
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: bold;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease;
    }
    
    .message-avatar:hover {
        transform: scale(1.05);
    }
    
    .user-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .assistant-avatar {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .message-text {
        flex: 1;
        line-height: 1.7;
        color: #ffffff;
        white-space: pre-wrap;
        font-family: 'Inter', sans-serif;
        font-size: 15px;
        padding: 1rem 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    /* Input area melhorada */
    .input-container {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        border-top: 2px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        position: sticky;
        bottom: 0;
        backdrop-filter: blur(20px);
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .input-wrapper {
        max-width: 900px;
        margin: 0 auto;
        position: relative;
    }
    
    /* Select box personalizado */
    .stSelectbox > div > div > select {
        background: linear-gradient(135deg, #3a4d5c 0%, #4a5d6f 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* File upload melhorado */
    .upload-area {
        background: linear-gradient(135deg, #3a4d5c 0%, #4a5d6f 100%);
        border: 2px dashed rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        font-size: 14px;
        color: #ffffff;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, #4a5d6f 0%, #5a6d7f 100%);
    }
    
    .file-info {
        background: linear-gradient(135deg, #10a37f 0%, #0ea270 100%);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 1rem;
        font-size: 14px;
        color: white;
        border-left: 4px solid #00c896;
        box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
        animation: slideInUp 0.3s ease-out;
    }
    
    /* TextArea melhorada */
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, #3a4d5c 0%, #4a5d6f 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 16px !important;
        color: #ffffff !important;
        padding: 16px 60px 16px 20px !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        font-family: 'Inter', sans-serif !important;
        resize: none !important;
        min-height: 60px !important;
        max-height: 200px !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3) !important;
        outline: none !important;
        transform: translateY(-2px) !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Botão de enviar melhorado */
    .send-button {
        position: absolute;
        right: 12px;
        bottom: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px !important;
        cursor: pointer !important;
        color: white !important;
        width: 44px !important;
        height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    .send-button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6) !important;
    }
    
    .send-button:active {
        transform: translateY(0px) !important;
    }
    
    .send-button:disabled {
        background: linear-gradient(135deg, #555 0%, #666 100%) !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Botão de limpar melhorado */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ee5a24 0%, #ff6b6b 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(255, 107, 107, 0.5) !important;
    }
    
    /* Spinner melhorado */
    .stSpinner > div {
        border-color: #667eea transparent transparent transparent !important;
        border-width: 3px !important;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 6px;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Ocultar elementos do Streamlit */
    .stDeployButton, footer, header {
        display: none;
    }
    
    /* Indicador de digitação melhorado */
    .typing-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: rgba(255, 255, 255, 0.7);
        font-style: italic;
    }
    
    .typing-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        animation: typing 1.4s infinite ease-in-out;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    .typing-dot:nth-child(3) { animation-delay: 0s; }
    
    @keyframes typing {
        0%, 80%, 100% { 
            transform: scale(0.8); 
            opacity: 0.5; 
        }
        40% { 
            transform: scale(1.2); 
            opacity: 1; 
        }
    }
    
    /* Stats container */
    .stats-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        justify-content: center;
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        text-align: center;
        min-width: 120px;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.2rem;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.7);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .message-content {
            padding: 1.5rem 1rem;
            gap: 1rem;
        }
        
        .message-avatar {
            width: 32px;
            height: 32px;
            font-size: 14px;
        }
        
        .message-text {
            font-size: 14px;
            padding: 0.8rem 1rem;
        }
        
        .input-container {
            padding: 1.5rem 1rem;
        }
        
        .stats-container {
            flex-direction: column;
            align-items: center;
        }
        
        .stat-card {
            min-width: 200px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Inicializar o cliente Claude 4
@st.cache_resource
def init_claude():
    return anthropic.Anthropic(api_key=API_KEY)

# Função para processar imagem
def process_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        
        # Redimensionar se necessário
        if image.size[0] > 1024 or image.size[1] > 1024:
            image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        img_byte_arr = io.BytesIO()
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(img_byte_arr, format='JPEG', quality=90)
        
        img_data = img_byte_arr.getvalue()
        if len(img_data) > 5 * 1024 * 1024:  # 5 MB
            st.error("⚠️ A imagem excede o tamanho máximo permitido (5 MB).")
            return None
        
        return base64.b64encode(img_data).decode('utf-8')
    except Exception as e:
        st.error(f"❌ Erro ao processar a imagem: {str(e)}")
        return None

# Função para construir histórico de mensagens para o Claude
def build_message_history():
    """Constrói o histórico de mensagens para enviar ao Claude"""
    messages = []
    
    for msg in st.session_state.messages:
        if not msg.get("is_loading", False) and msg.get("assistant") != "...":
            # Adicionar mensagem do usuário
            user_text = msg['user']
            # Remover prefixes de template e arquivo
            if user_text.startswith('[') and '] ' in user_text:
                user_text = user_text.split('] ', 1)[1]
            if ' [Arquivo:' in user_text:
                user_text = user_text.split(' [Arquivo:')[0]
            
            messages.append({
                "role": "user",
                "content": user_text
            })
            
            # Adicionar resposta do assistente
            messages.append({
                "role": "assistant", 
                "content": msg['assistant']
            })
    
    return messages

# Função para enviar ao Claude 4 com histórico
def chat_with_claude(message_content, template_tipo=None):
    try:
        client = init_claude()
        
        # Construir histórico de mensagens anteriores
        history = build_message_history()
        
        # Construir prompt baseado no template selecionado
        if template_tipo and template_tipo in TEMPLATES_MINUTAS:
            template = TEMPLATES_MINUTAS[template_tipo]
            system_prompt = f"""Você é um assistente especializado em documentos cartoriais com Claude 4. Você tem acesso ao histórico completo da conversa e pode fazer referência a informações discutidas anteriormente.

O usuário selecionou o tipo de minuta: "{template_tipo}".

Use o seguinte template como base:

{template}

INSTRUÇÕES:
1. Analise os dados fornecidos pelo usuário (texto ou imagem) e o contexto da conversa anterior
2. Preencha o template substituindo todos os "XXXXXXXXXXX" pelos dados corretos
3. Se algum dado não estiver disponível, mantenha "XXXXXXXXXXX" ou pergunte ao usuário
4. Mantenha a formatação e estrutura do template original
5. Use linguagem jurídica formal e precisa
6. Faça referência a informações anteriores da conversa quando relevante

Seja preciso, contextual e mantenha a consistência com as informações já discutidas."""
            
            # Preparar mensagens para o Claude 4
            messages = history.copy()
            
            # Adicionar mensagem atual
            if isinstance(message_content, list):
                # Se é uma lista (pode conter imagem)
                current_message = {"role": "user", "content": message_content}
            else:
                current_message = {"role": "user", "content": message_content}
            
            messages.append(current_message)
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",  # Claude 4 Sonnet
                max_tokens=4000,
                temperature=0.3,
                system=system_prompt,
                messages=messages
            )
        else:
            # Chat geral com histórico
            system_prompt = """Você é um assistente especializado em documentos cartoriais usando Claude 4. Você tem acesso ao histórico completo da conversa e pode:

1. Fazer referência a informações discutidas anteriormente
2. Manter consistência nas respostas
3. Ajudar com documentos cartoriais, jurídicos e administrativos
4. Explicar procedimentos, requisitos e formatações
5. Analisar imagens de documentos quando fornecidas

Seja preciso, contextual e mantenha a continuidade da conversa."""
            
            messages = build_message_history()
            
            # Adicionar mensagem atual
            if isinstance(message_content, list):
                current_message = {"role": "user", "content": message_content}
            else:
                current_message = {"role": "user", "content": message_content}
            
            messages.append(current_message)
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",  # Claude 4 Sonnet
                max_tokens=3000,
                temperature=0.4,
                system=system_prompt,
                messages=messages
            )
        
        return response.content[0].text
    except Exception as e:
        st.error(f"❌ Erro ao processar a solicitação: {str(e)}")
        return None

# Inicializar estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False
if "message_sent" not in st.session_state:
    st.session_state.message_sent = False
if "send_clicked" not in st.session_state:
    st.session_state.send_clicked = False
if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now()

# Header melhorado
st.markdown("""
<div class="chat-header">
    <h1 class="chat-title">🏛️ Claude 4 - Inteligência Artificial Cartorial</h1>
    <p class="chat-subtitle">Assistente especializado em documentos jurídicos com memória de conversa</p>
</div>
""", unsafe_allow_html=True)

# Stats container
total_messages = len(st.session_state.messages)
session_duration = (datetime.now() - st.session_state.session_start).seconds // 60


# Container principal do chat
chat_container = st.container()

with chat_container:
    # Exibir mensagens existentes
    for i, message in enumerate(st.session_state.messages):
        # Mensagem do usuário
        st.markdown(f"""
        <div class="message-container user-message">
            <div class="message-content">
                <div class="message-avatar user-avatar">👤</div>
                <div class="message-text">{message['user']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mensagem do assistente
        if message.get("is_loading", False):
            # Mostrar indicador de digitação
            st.markdown("""
            <div class="message-container assistant-message">
                <div class="message-content">
                    <div class="message-avatar assistant-avatar">🤖</div>
                    <div class="message-text">
                        <div class="typing-indicator">
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <span style="margin-left: 8px;">Claude 4 está analisando com base no histórico...</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Mostrar resposta normal
            assistant_response = message['assistant'].replace('\n', '<br>')
            st.markdown(f"""
            <div class="message-container assistant-message">
                <div class="message-content">
                    <div class="message-avatar assistant-avatar">🤖</div>
                    <div class="message-text">{assistant_response}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Input area fixa na parte inferior
st.markdown('<div class="input-container">', unsafe_allow_html=True)

with st.container():
    # Primeira linha: seleção e botão de limpar
    col_select, col_clear = st.columns([4, 1])
    
    with col_select:
        tipo_minuta = st.selectbox(
            "🏛️ Selecione o tipo de minuta:",
            ["Nenhum"] + list(TEMPLATES_MINUTAS.keys()),
            key="tipo_minuta_select",
            help="Selecione um template de minuta para preenchimento automático"
        )
    
    with col_clear:
        st.write("")
        if st.button("🗑️ Nova Conversa", key="clear_chat", help="Limpar todo o histórico"):
            st.session_state.messages = []
            st.session_state.send_clicked = False
            st.session_state.session_start = datetime.now()
            st.rerun()
    
    # Upload de arquivo (opcional)
    uploaded_file = st.file_uploader(
        "📎 Anexar arquivo com dados (opcional)",
        type=['png', 'jpg', 'jpeg', 'webp', 'txt', 'pdf'],
        label_visibility="collapsed",
        key="file_upload",
        help="Formatos suportados: Imagens (PNG, JPG, JPEG, WebP) e Texto (TXT, PDF)"
    )
    
    if uploaded_file:
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        st.markdown(f"""
        <div class="file-info">
            📎 <strong>Arquivo:</strong> {uploaded_file.name}<br>
            📏 <strong>Tamanho:</strong> {file_size:.2f} MB | <strong>Tipo:</strong> {uploaded_file.type}
        </div>
        """, unsafe_allow_html=True)
    
    # Área de input com duas colunas
    col1, col2 = st.columns([10, 1])
    
    with col1:
        # Usar valor padrão vazio se mensagem foi enviada
        input_value = "" if st.session_state.get("message_sent", False) else st.session_state.get("current_message", "")
        
        placeholder_text = "💬 Digite sua mensagem... (Ctrl+Enter para enviar)"
        if tipo_minuta != "Nenhum":
            placeholder_text = f"📝 Digite os dados para preencher a minuta de {tipo_minuta}... (Ctrl+Enter para enviar)"
        
        user_input = st.text_area(
            "Digite sua mensagem...",
            value=input_value,
            height=80,
            max_chars=3000,
            placeholder=placeholder_text,
            label_visibility="collapsed",
            key="message_input"
        )
    
    with col2:
        send_disabled = not (user_input.strip() or uploaded_file)
        if st.button("🚀", key="send_btn", help="Enviar mensagem", disabled=send_disabled):
            st.session_state.send_clicked = True

st.markdown('</div>', unsafe_allow_html=True)

# Processar envio da mensagem
if st.session_state.send_clicked and (user_input.strip() or uploaded_file):
    # Reset the button state
    st.session_state.send_clicked = False
    
    # Preparar conteúdo da mensagem
    message_content = []
    file_info = ""
    
    # Processar arquivo se houver
    if uploaded_file:
        if uploaded_file.type.startswith('image/'):
            img_base64 = process_image(uploaded_file)
            if img_base64:
                st.session_state["last_uploaded_image"] = {
                    "data": img_base64,
                    "type": 'image/jpeg',
                    "name": uploaded_file.name
                }
                message_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": 'image/jpeg',
                        "data": img_base64
                    }
                })
                file_info = f" [📎 Imagem: {uploaded_file.name}]"
        elif uploaded_file.type == 'text/plain':
            try:
                file_content = uploaded_file.read().decode('utf-8')
                message_content.append({
                    "type": "text",
                    "text": f"📄 Conteúdo do arquivo {uploaded_file.name}:\n\n{file_content}\n\n"
                })
                file_info = f" [📎 Arquivo: {uploaded_file.name}]"
            except Exception as e:
                st.error(f"❌ Erro ao ler arquivo de texto: {str(e)}")
        else:
            st.warning("⚠️ Formato de arquivo não suportado. Use imagens (PNG, JPG, JPEG, WebP) ou texto (TXT).")
    
    # Adicionar mensagem do usuário
    user_message = user_input.strip() if user_input.strip() else "🔍 Analise os dados fornecidos"
    if tipo_minuta != "Nenhum":
        display_message = f"📋 [{tipo_minuta}] {user_message}{file_info}"
    else:
        display_message = f"{user_message}{file_info}"
    
    # Adicionar texto da mensagem
    message_content.append({
        "type": "text",
        "text": user_message
    })
    
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({
        "user": display_message,
        "assistant": "...",
        "is_loading": True,
        "template_tipo": tipo_minuta if tipo_minuta != "Nenhum" else None,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Marcar que mensagem foi enviada para limpar input
    st.session_state.message_sent = True
    
    # Rerun para mostrar mensagem imediatamente
    st.rerun()

# Reset flag após rerun
if st.session_state.get("message_sent", False):
    st.session_state.message_sent = False

# Processar resposta do Claude se há mensagem em loading
if st.session_state.messages and st.session_state.messages[-1].get("is_loading", False):
    last_message = st.session_state.messages[-1]
    
    # Reconstruir message_content para enviar ao Claude
    message_content = []
    
    # Extrair texto da mensagem do usuário (removendo prefixes)
    user_text = last_message['user']
    if user_text.startswith('📋 [') and '] ' in user_text:
        user_text = user_text.split('] ', 1)[1]
    if ' [📎' in user_text:
        user_text = user_text.split(' [📎')[0]
    
    message_content.append({
        "type": "text",
        "text": user_text
    })
    
    # Adicionar imagem se disponível
    if "last_uploaded_image" in st.session_state:
        img_data = st.session_state["last_uploaded_image"]
        message_content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": img_data["type"],
                "data": img_data["data"]
            }
        })
    
    # Obter resposta do Claude 4
    template_tipo = last_message.get('template_tipo')
    
    start_time = time.time()
    with st.spinner("🧠 Claude 4 está processando com base no histórico da conversa..."):
        response = chat_with_claude(message_content, template_tipo)
    processing_time = time.time() - start_time
    
    # Atualizar a mensagem com a resposta
    if response:
        # Adicionar informações de processamento
        response_with_info = f"{response}\n\n---\n⏱️ *Processado em {processing_time:.1f}s com Claude 4 Sonnet*"
        st.session_state.messages[-1]["assistant"] = response_with_info
    else:
        st.session_state.messages[-1]["assistant"] = "❌ Erro ao obter resposta do Claude 4. Tente novamente."
    
    st.session_state.messages[-1]["is_loading"] = False
    
    # Limpar imagem temporária
    if "last_uploaded_image" in st.session_state:
        del st.session_state["last_uploaded_image"]
    
    # Rerun para mostrar a resposta
    st.rerun()

# JavaScript melhorado para interatividade
st.markdown("""
<script>
    // Auto-resize textarea
    function setupTextarea() {
        const textarea = document.querySelector('textarea[data-testid="stTextArea"]');
        if (textarea) {
            // Auto-resize
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 200) + 'px';
            });
            
            // Submit on Ctrl+Enter
            textarea.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    const sendBtn = document.querySelector('button[data-testid="baseButton-secondary"]');
                    if (sendBtn && !sendBtn.disabled) {
                        sendBtn.click();
                    }
                }
            });
            
            // Focus on textarea when page loads
            textarea.focus();
        }
    }
    
    // Auto-scroll to bottom
    function scrollToBottom() {
        setTimeout(() => {
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }
    
    // Setup when DOM is ready
    document.addEventListener('DOMContentLoaded', setupTextarea);
    
    // Setup on dynamic content changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                setupTextarea();
                scrollToBottom();
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+K para focar no input
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            const textarea = document.querySelector('textarea[data-testid="stTextArea"]');
            if (textarea) textarea.focus();
        }
        
        // Ctrl+L para limpar conversa
        if (e.ctrlKey && e.key === 'l') {
            e.preventDefault();
            const clearBtn = document.querySelector('button[data-testid="baseButton-secondary"]');
            if (clearBtn && clearBtn.textContent.includes('Nova Conversa')) {
                clearBtn.click();
            }
        }
    });
    
    // Add visual feedback for file uploads
    const fileUploader = document.querySelector('input[type="file"]');
    if (fileUploader) {
        fileUploader.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                // Add visual feedback
                const container = e.target.closest('.stFileUploader');
                if (container) {
                    container.style.borderColor = '#667eea';
                    container.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
                }
            }
        });
    }
    
    // Initialize
    setupTextarea();
    scrollToBottom();
</script>
""", unsafe_allow_html=True)

