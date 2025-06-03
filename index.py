import streamlit as st
import anthropic
import base64
from PIL import Image
import io
import time

# ===== CONFIGURAÇÃO DA API =====
API_KEY = st.secret("jhghhj")

# ===== TEMPLATES DE MINUTAS =====
TEMPLATES_MINUTAS = {
    "Procuração para Negócio Consigo Mesmo": """PROCURAÇÃO PARA NEGÓCIO CONSIGO MESMO (AUTOCONTRATO)
 
PROCURAÇÃO BASTANTE QUE FAZEM
XXXXXXXXXXX E XXXXXXXXXXX, NA FORMA ABAIXO:
 
SAIBAM quantos este instrumento público de procuração virem que, em XXXXXXXXXXX nesta Cidade XXXXXXXXXXX, Estado de Minas Gerais, no Cartório de XXXXXXXXXXX, localizado na XXXXXXXXXXX, compareceram como Outorgantes: XXXXXXXXXXX e XXXXXXXXXXX (qualificar), casados entre si sob o regime da xxxx, desde xxx, conforme certidão expedida em xxx pelo Cartório do Registro Civil de xxx, livro xxx, folha xxx, termo xxx (ou matrícula). As partes são capazes e se identificaram, conforme documentação apresentada, do que dou fé. E pelos Outorgantes me foi dito que, por este instrumento, nomeiam e constituem sua bastante PROCURADORA: XXXXXXXXXXX; a quem conferem poderes para vender para PARA SI MESMA, OUTORGADA, pelo preço de R$ XXXXXXXXXXX, já pagos e quitados, via TED, na data xxxx, o IMÓVEL URBANO, constituído do APARTAMENTO, XXXXXXXXXXX, localizado no XXX andar do EDIFÍCIO XXXXXXXXXXX, situado na cidade de XXXXXXXXXXX, a RUA XXXXXXXXXXX, nº XXXXXXXXXXX, apartamento esse com dependências, instalações e pertences, área privativa de XXXXXXXXXXX, área comum de XXXXXXXXXXX, área total de XXXXXXXXXXX m², fração ideal do prédio de XXXXXXXXXXX m² e XXXXXXXXXXX m² de área ideal do terreno onde está o prédio, com a área de XXXXXXXXXXX m², índice cadastral no IPTU nº XXXXXXXXXXX, e sua VAGA DE GARAGEM N º XXXXXXXXXXX, índice cadastral no IPTU, cuja descrição e caracterização encontram-se na Matrícula nº XXXXXXXXXXX do Cartório de Registro de Imóveis do xx° Oficio de XXXXXXXXXXX-MG, podendo para tanto, transmitir posse, domínio, direito e ação; receber o preço e dar quitação; firmar recibo; outorgar e assinar a competente escritura com cláusulas e demais solenidades de estilo, usuais e necessárias, para que a transação seja feita boa, firme e valiosa, assim como ulteriores retificações, se porventura necessárias; descrever e melhor caracterizar o imóvel, dando áreas limites e confrontações; fazer com que os Outorgantes respondam pela evicção de direitos, na forma da Lei; representar amplamente os Outorgantes perante repartições públicas federais, estaduais e municipais, cartórios e onde mais preciso for, requerendo e assinando o que necessário for; prestar declarações sob responsabilidade civil e penal, quanto a situação jurídica do imóvel e dos Outorgantes, enfim, praticar todos os atos necessários para o fiel desempenho deste mandato. Foi consultado o domínio www.indisponibilidade.org.br e constatado que não há indisponibilidade de bens em nome dos Outorgantes, código(s) HASH: XXXXXXXXXXX. Assim o disseram, do que dou fé, e me pediram este instrumento que lhes lavrei nas minhas notas, tendo sido lido pelos Outorgantes, e, estes, tendo-o achado conforme, aceitaram, outorgaram e assinam. Dispensada a presença de testemunhas, com base no artigo 215, parágrafo 5º, do CCB. O nome e dados do procurador foram fornecidos por declaração e conferidos pelos Outorgantes, que por eles se responsabilizam. As partes Outorgantes declaram sob as penas da lei que o seu estado civil encontra-se inalterado até a presente data. A certidão atualizada que comprova o estado civil das partes deverá ser apresentada quando da lavratura da respectiva escritura. Esta procuração só terá validade com apresentação dos documentos que comprovem a propriedade do imóvel objeto desta em nome dos Outorgantes no momento da lavratura da escritura de compra e venda. Ficam arquivados neste Cartório os documentos necessários para lavratura da presente procuração, dentre eles os exigidos no Código de Normas do Extrajudicial de Minas Gerais. Valor Total: Emolumentos: XXXXXXXXXXX - Valor Total: R$ XXXXXXXXXXX.""",
    
    "Escritura de Compra e Venda": """ESCRITURA PÚBLICA DE COMPRA E VENDA DE IMÓVEL
 
SAIBAM quantos esta pública escritura de compra e venda virem que aos XXXXXXXXXXX dias do mês de XXXXXXXXXXX do ano de XXXXXXXXXXX, nesta cidade de XXXXXXXXXXX, Estado do Maranhão, em meu Cartório, perante mim, XXXXXXXXXXX, compareceram as partes entre si justas e contratadas, a saber:

VENDEDOR(A): XXXXXXXXXXX (qualificar completamente)
COMPRADOR(A): XXXXXXXXXXX (qualificar completamente)

Reconheço a identidade dos comparecentes pelos documentos apresentados e dou fé de que são capazes. Pelo(a) VENDEDOR(A) me foi dito que é senhor(a) e legítimo(a) possuidor(a) do IMÓVEL situado XXXXXXXXXXX, com as características descritas na matrícula nº XXXXXXXXXXX do Cartório de Registro de Imóveis XXXXXXXXXXX, e que pelo presente instrumento o VENDE ao COMPRADOR pelo preço certo e ajustado de R$ XXXXXXXXXXX, quantia que confessa ter recebido antes da lavratura desta escritura, pelo que lhe dá plena, geral e irrevogável quitação. Fica desde já transmitida ao COMPRADOR a posse, domínio e todos os direitos sobre o imóvel objeto desta escritura. O VENDEDOR obriga-se pela evicção de direito e o COMPRADOR declara conhecer o estado de conservação do imóvel, recebendo-o no estado em que se encontra. O imóvel ora vendido encontra-se livre e desembaraçado de quaisquer ônus reais. As partes elegem o foro da Comarca de XXXXXXXXXXX para dirimir questões oriundas deste contrato. Assim o disseram e me pediram esta escritura que lhes lavrei, lida, achada conforme, aceitam, outorgam e assinam.""",
    
    "Procuração Ad Judicia": """PROCURAÇÃO AD JUDICIA
 
SAIBAM quantos este público instrumento de procuração ad judicia virem que aos XXXXXXXXXXX dias do mês de XXXXXXXXXXX do ano de XXXXXXXXXXX, nesta cidade de XXXXXXXXXXX, Estado de Minas Gerais, em meu Cartório, perante mim, XXXXXXXXXXX, compareceu como OUTORGANTE: XXXXXXXXXXX (qualificar completamente).

Reconheço a identidade do comparecente pelos documentos apresentados e dou fé que é capaz. Pelo OUTORGANTE me foi dito que por este instrumento nomeia e constitui seu bastante PROCURADOR o(a) Dr(a). XXXXXXXXXXX, advogado(a), inscrito(a) na OAB/MG sob o nº XXXXXXXXXXX, ao qual confere os poderes da cláusula ad judicia, podendo propor contra quem de direito as competentes ações, bem como defender o outorgante nas que contra ele forem propostas, seguindo umas e outras até final decisão; podendo transigir, desistir, fazer acordos, receber e dar quitação; substabelecer esta procuração no todo ou em parte, com ou sem reservas de iguais poderes; enfim, praticar todos os atos necessários ao fiel desempenho deste mandato, inclusive os constantes dos artigos 81 e seguintes do Código de Processo Civil. Assim o disse e me pediu este instrumento que lhe lavrei, lido, achado conforme, aceita, outorga e assina.""",
    
    "Escritura de Doação": """ESCRITURA PÚBLICA DE DOAÇÃO
 
SAIBAM quantos esta pública escritura de doação virem que aos XXXXXXXXXXX dias do mês de XXXXXXXXXXX do ano de XXXXXXXXXXX, nesta cidade de XXXXXXXXXXX, Estado de Minas Gerais, em meu Cartório, perante mim, XXXXXXXXXXX, compareceram as partes entre si justas e contratadas:

DOADOR(A): XXXXXXXXXXX (qualificar completamente)
DONATÁRIO(A): XXXXXXXXXXX (qualificar completamente)

Reconheço a identidade dos comparecentes pelos documentos apresentados e dou fé de que são capazes. Pelo(a) DOADOR(A) me foi dito que é senhor(a) e legítimo(a) possuidor(a) do imóvel situado XXXXXXXXXXX, com as características descritas na matrícula nº XXXXXXXXXXX do Cartório de Registro de Imóveis XXXXXXXXXXX, e que por mera liberalidade e sem qualquer encargo, pelo presente instrumento faz DOAÇÃO PURA E SIMPLES do referido imóvel ao DONATÁRIO, que aceita a doação. Fica desde já transmitida ao DONATÁRIO a posse, domínio e todos os direitos sobre o imóvel objeto desta escritura. O DOADOR se obriga pela evicção de direito. O imóvel ora doado encontra-se livre e desembaraçado de quaisquer ônus reais. Assim o disseram e me pediram esta escritura que lhes lavrei, lida, achada conforme, aceitam, outorgam e assinam."""
}

# Configuração da página
st.set_page_config(
    page_title="Claude Chat Cartorial",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS moderno estilo ChatGPT
st.markdown("""
<style>
    /* Remove padding padrão do Streamlit */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    /* Container principal */
    .main-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        background: #212121;
        color: #ffffff;
    }
    
    /* Header */
    .chat-header {
        background: #ffffff;
        padding: 1rem 2rem;
        border-bottom: 1px solid #444654;
        text-align: center;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .chat-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #000000;
        margin: 0;
    }
    
    /* Chat container */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 0;
        background: #343541;
    }
    
    /* Mensagens */
    .message-container {
        width: 100%;
        border-bottom: 1px solid #444654;
    }
    
    .message-content {
        max-width: 768px;
        margin: 0 auto;
        padding: 1.5rem 2rem;
        display: flex;
        gap: 1rem;
        align-items: flex-start;
    }
    
    .user-message {
        background: #343541;
    }
    
    .assistant-message {
        background: #444654;
    }
    
    .message-avatar {
        width: 32px;
        height: 32px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        font-weight: bold;
        flex-shrink: 0;
    }
    
    .user-avatar {
        background: #5436da;
        color: white;
    }
    
    .assistant-avatar {
        background: #19c37d;
        color: white;
    }
    
    .message-text {
        flex: 1;
        line-height: 1.6;
        color: #ffffff;
        white-space: pre-wrap;
        font-family: 'Courier New', monospace;
    }
    
    /* Input area */
    .input-container {
        background: #343541;
        border-top: 1px solid #444654;
        padding: 1rem 2rem 2rem 2rem;
        position: sticky;
        bottom: 0;
    }
    
    .input-wrapper {
        max-width: 768px;
        margin: 0 auto;
        position: relative;
    }
    
    /* Select box customization */
    .stSelectbox > div > div > select {
        background-color: #40414f !important;
        border: 1px solid #565869 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
    }
    
    .stSelectbox > div > div > div {
        background-color: #40414f !important;
        border: 1px solid #565869 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    /* File upload area */
    .upload-area {
        background: #40414f;
        border: 2px solid #565869;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 12px;
        color: #ffffff;
    }
    
    .file-info {
        background: #444654;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 8px;
        font-size: 12px;
        color: #10a37f;
        border-left: 3px solid #10a37f;
    }
    
    /* Customizar elementos do Streamlit */
    .stTextArea > div > div > textarea {
        background-color: #40414f !important;
        border: 1px solid #565869 !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 12px 50px 12px 16px !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
        resize: none !important;
        min-height: 52px !important;
        max-height: 200px !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #10a37f !important;
        box-shadow: 0 0 0 1px #10a37f !important;
        outline: none !important;
    }
    
    /* Botão de enviar */
    .send-button {
        position: absolute;
        right: 8px;
        bottom: 8px;
        background: #19c37d !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px !important;
        cursor: pointer !important;
        color: white !important;
        width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .send-button:hover {
        background: #0ea270 !important;
    }
    
    .send-button:disabled {
        background: #565869 !important;
        cursor: not-allowed !important;
    }
    
    /* Spinner customizado */
    .stSpinner > div {
        border-color: #10a37f transparent transparent transparent !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #343541;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #565869;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #666;
    }
    
    /* Ocultar elementos do Streamlit */
    .stDeployButton {
        display: none;
    }
    
    footer {
        display: none;
    }
    
    header {
        display: none;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        color: #888;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #888;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    .typing-dot:nth-child(3) { animation-delay: 0s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Inicializar o cliente Claude
@st.cache_resource
def init_claude():
    return anthropic.Anthropic(api_key=API_KEY)

# Função para processar imagem
def process_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        
        if image.size[0] > 1024 or image.size[1] > 1024:
            image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        img_byte_arr = io.BytesIO()
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(img_byte_arr, format='JPEG')  # Sempre converter para JPEG
        
        img_data = img_byte_arr.getvalue()
        if len(img_data) > 5 * 1024 * 1024:  # 5 MB
            st.error("Erro: A imagem excede o tamanho máximo permitido (5 MB).")
            return None
        
        return base64.b64encode(img_data).decode('utf-8')
    except Exception as e:
        st.error(f"Erro ao processar a imagem: {str(e)}")
        return None

# Função para enviar ao Claude
def chat_with_claude(message_content, template_tipo=None):
    try:
        client = init_claude()
        
        # Construir prompt baseado no template selecionado
        if template_tipo and template_tipo in TEMPLATES_MINUTAS:
            template = TEMPLATES_MINUTAS[template_tipo]
            system_prompt = f"""Você é um assistente especializado em documentos cartoriais. O usuário selecionou o tipo de minuta, somente substitua os pontos XXXXXXXX pelas informações fornecidas pelo usuário, não faça absolutamente NENHUM! comentário, somente retorne conteúdo da minuta substituindo as informações que conseguir, as que não conseguir, deixe o valor como está se atenha substituir as informações que conseguir: "{template_tipo}".

Use o seguinte template como base:

{template}

Analise os dados fornecidos pelo usuário (texto ou imagem) e preencha o template substituindo todos os "XXXXXXXXXXX" pelos dados corretos extraídos das informações fornecidas. 

Mantenha a formatação e estrutura do template original. Se algum dado não estiver disponível nas informações fornecidas, mantenha "XXXXXXXXXXX" para que possa ser preenchido posteriormente.

Seja preciso e mantenha a linguagem jurídica formal."""
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Modelo que suporta imagens
                max_tokens=3000,
                system=system_prompt,
                messages=[{"role": "user", "content": message_content}]
            )
        else:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": message_content}]
            )
        
        return response.content[0].text
    except Exception as e:
        st.error(f"Erro ao processar a solicitação: {str(e)}")
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

# Header
st.markdown("""
<div class="chat-header">
    <h1 class="chat-title">🏛️ Inteligência Artificial de Cartório</h1>
</div>
""", unsafe_allow_html=True)

# Container principal do chat
chat_container = st.container()

with chat_container:
    # Exibir mensagens existentes
    for message in st.session_state.messages:
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
                            <span style="margin-left: 8px;">Claude está digitando...</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Mostrar resposta normal
            st.markdown(f"""
            <div class="message-container assistant-message">
                <div class="message-content">
                    <div class="message-avatar assistant-avatar">🤖</div>
                    <div class="message-text">{message['assistant']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Input area fixa na parte inferior
st.markdown('<div class="input-container">', unsafe_allow_html=True)

with st.container():
    # Seleção do tipo de minuta
    col_select, col_clear = st.columns([4, 1])
    
    with col_select:
        tipo_minuta = st.selectbox(
            "Selecione o tipo de minuta:",
            ["Nenhum"] + list(TEMPLATES_MINUTAS.keys()),
            key="tipo_minuta_select"
        )
    
    with col_clear:
        if st.button("🗑️ Nova Conversa", key="clear_chat"):
            st.session_state.messages = []
            st.session_state.send_clicked = False
            st.rerun()
    
    # Upload de arquivo (opcional)
    uploaded_file = st.file_uploader(
        "Anexar arquivo com dados (opcional)",
        type=['png', 'jpg', 'jpeg', 'webp', 'txt', 'pdf'],
        label_visibility="collapsed",
        key="file_upload"
    )
    
    if uploaded_file:
        st.markdown(f"""
        <div class="file-info">
            📎 Arquivo anexado: {uploaded_file.name} ({uploaded_file.type})
        </div>
        """, unsafe_allow_html=True)
    
    # Área de input com duas colunas
    col1, col2 = st.columns([10, 1])
    
    with col1:
        # Usar valor padrão vazio se mensagem foi enviada
        input_value = "" if st.session_state.get("message_sent", False) else st.session_state.get("current_message", "")
        
        placeholder_text = "Digite os dados para preencher a minuta ou descreva o que precisa..."
        if tipo_minuta != "Nenhum":
            placeholder_text = f"Digite os dados para preencher a minuta de {tipo_minuta}..."
        
        user_input = st.text_area(
            "Digite sua mensagem...",
            value=input_value,
            height=70,
            max_chars=2000,
            placeholder=placeholder_text,
            label_visibility="collapsed",
            key="message_input"
        )
    
    with col2:
        if st.button("➤", key="send_btn", help="Enviar mensagem"):
            st.session_state.send_clicked = True

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
                file_info = f" [Arquivo: {uploaded_file.name}]"
        elif uploaded_file.type == 'text/plain':
            file_content = uploaded_file.read().decode('utf-8')
            message_content.append({
                "type": "text",
                "text": f"Conteúdo do arquivo {uploaded_file.name}:\n\n{file_content}\n\n"
            })
            file_info = f" [Arquivo: {uploaded_file.name}]"
        else:
            st.warning("Formato de arquivo não suportado para imagens.")
    
    # Adicionar mensagem do usuário
    user_message = user_input.strip() if user_input.strip() else "Analise os dados fornecidos"
    if tipo_minuta != "Nenhum":
        display_message = f"[{tipo_minuta}] {user_message}{file_info}"
    else:
        display_message = f"{user_message}{file_info}"
    
    message_content.append({
        "type": "text",
        "text": user_message
    })
    
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({
        "user": display_message,
        "assistant": "...",
        "is_loading": True,
        "template_tipo": tipo_minuta if tipo_minuta != "Nenhum" else None
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
    if user_text.startswith('[') and '] ' in user_text:
        user_text = user_text.split('] ', 1)[1]
    if ' [Arquivo:' in user_text:
        user_text = user_text.split(' [Arquivo:')[0]
    
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
    
    # Obter resposta do Claude
    template_tipo = last_message.get('template_tipo')
    with st.spinner("Claude está processando..."):
        response = chat_with_claude(message_content, template_tipo)
    
    # Atualizar a mensagem com a resposta
    if response:
        st.session_state.messages[-1]["assistant"] = response
    else:
        st.session_state.messages[-1]["assistant"] = "Erro ao obter resposta do Claude."
    st.session_state.messages[-1]["is_loading"] = False
    
    # Rerun para mostrar a resposta
    st.rerun()

# JavaScript para melhorar a experiência
st.markdown("""
<script>
    // Auto-resize textarea
    const textarea = document.querySelector('textarea');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
        
        // Submit on Ctrl+Enter
        textarea.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                const sendBtn = document.querySelector('[data-testid="baseButton-secondary"]');
                if (sendBtn) sendBtn.click();
            }
        });
    }
    
    // Auto-scroll to bottom
    function scrollToBottom() {
        window.scrollTo(0, document.body.scrollHeight);
    }
    
    // Scroll to bottom when new messages appear
    const observer = new MutationObserver(scrollToBottom);
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)
