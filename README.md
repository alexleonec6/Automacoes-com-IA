# Hub de Automações com IA (FastAPI + Telegram + n8n)

Microsserviço de automação de eventos e mensagens corporativas. O sistema recebe webhooks de formulários, alertas de monitoramento ou integrações via **n8n**, realiza a triagem semântica com modelos de IA (OpenAI ou LLMs locais), classifica urgência, gera respostas contextuais e despacha alertas prioritários para o **Telegram**, persistindo o histórico em SQLite.

---

## Como Funciona

1. **Ingestão (Webhook / API):** Endpoint `/webhook` recebe payloads contendo mensagens ou eventos de sistemas externos (n8n, Typeform, Stripe, GitHub, etc.).
2. **Triagem com IA:** Analisa a mensagem e categoriza o evento:
   - `INCIDENTE_URGENTE` (urgência crítica)
   - `QUALIFICACAO_LEAD` (oportunidade comercial)
   - `SUPORTE_CLIENTE` (dúvidas e chamados de usuários)
   - `AUTOMACAO_TAREFA` (tarefas operacionais internas)
3. **Despacho Assíncrono:** Eventos urgentes ou que exigem ação humana disparam notificações em tempo real no Telegram através de `BackgroundTasks`.
4. **Persistência:** Todos os eventos e respostas da IA são salvos no banco local SQLite para auditoria e histórico.

---

## Tecnologias

| Tecnologia | Finalidade |
| :--- | :--- |
| **Python 3.10+** | Linguagem principal |
| **FastAPI** | Framework web assíncrono para a API REST e webhooks |
| **Pydantic** | Validação rigorosa dos schemas de entrada e saída |
| **Telegram Bot API** | Canal de alerta e mensageria em tempo real |
| **OpenAI / LLMs** | Classificação semântica e geração de respostas |
| **SQLite** | Armazenamento leve do histórico de eventos |
| **n8n** | Orquestração de fluxos low-code integrada |

---

## Estrutura do Repositório

```text
Automacoes-com-IA/
├── src/
│   ├── config.py             # Variáveis de ambiente e credenciais
│   ├── database.py           # Conexão e queries com o SQLite
│   ├── ai_service.py         # Triagem semântica e integração com LLM
│   ├── telegram_service.py   # Envio formatado de alertas no Telegram
│   └── main.py               # Servidor FastAPI com rotas de webhook
├── workflows/
│   └── n8n_pipeline_atendimento.json  # Workflow exportado pronto para o n8n
├── tests/
│   └── test_ai_service.py    # Testes unitários das regras de classificação
├── .env.example              # Modelo de variáveis de ambiente
├── requirements.txt          # Dependências mínimas do projeto
└── README.md
```

---

## Como Rodar o Projeto

### 1. Clonar o repositório
```bash
git clone https://github.com/alexleonec6/Automacoes-com-IA.git
cd Automacoes-com-IA
```

### 2. Criar e ativar o ambiente virtual
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
*(Opcional: se não configurar chave da OpenAI ou Telegram, o projeto roda normalmente utilizando o modo de fallback inteligente).*

### 5. Iniciar o servidor
```bash
uvicorn src.main:app --reload
```
A API estará disponível em `http://localhost:8000`. Acesse a documentação interativa Swagger em:
`http://localhost:8000/docs`

---

## Testando sem Webhook Externo

Você pode testar a automação diretamente via endpoint de simulação:

```bash
# Simular um incidente crítico
curl -X POST "http://localhost:8000/simular?tipo=incidente"

# Simular um lead comercial
curl -X POST "http://localhost:8000/simular?tipo=lead"

# Consultar o histórico no banco de dados
curl -X GET "http://localhost:8000/eventos"
```

---

## Integração com n8n

O arquivo `workflows/n8n_pipeline_atendimento.json` contém o fluxo visual completo. Para utilizar:
1. Abra seu painel do **n8n**.
2. Clique em **Workflows** > **Import from File**.
3. Selecione o arquivo `.json` do diretório `workflows/`.
