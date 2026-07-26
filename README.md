<div align="center">

  <h1>🤖 SENAI Jaú — ChatBot Técnico em Desenvolvimento de Sistemas</h1>

  <p>
    <strong>Assistente inteligente especializado no curso técnico do SENAI Jaú</strong>
  </p>

  <p>
    <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white" alt="React 19">
    <img src="https://img.shields.io/badge/TypeScript-6-3178C6?logo=typescript&logoColor=white" alt="TypeScript 6">
    <img src="https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white" alt="Vite 8">
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12">
    <img src="https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Groq-LLaMA%203.1-10a37f" alt="Groq LLaMA 3.1">
  </p>

</div>

---

## 📋 Visão Geral

Chatbot com **RAG (Retrieval-Augmented Generation)** que responde perguntas sobre o **Curso Técnico em Desenvolvimento de Sistemas** do **SENAI Jaú**. O sistema utiliza o modelo **LLaMA 3.1 (8B)** via **Groq API** combinado com busca vetorial no plano de curso oficial em PDF para gerar respostas precisas e contextuais.

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **💬 Chat inteligente** | Respostas baseadas no plano de curso oficial com RAG |
| **🎤 Comando de voz** | Reconhecimento de fala nativo (Web Speech API) |
| **🏫 Imagens contextuais** | Exibição alternada de imagens das salas do SENAI |
| **⚡ Streaming de resposta** | Indicador de digitação e carregamento assíncrono |
| **📱 Responsivo** | Layout adaptável para mobile e desktop |
| **🔍 Sugestões inteligentes** | Perguntas pré-definidas para acesso rápido |
| **🧠 Memória de conversa** | Contexto mantido durante a sessão |
| **📊 Métricas de desempenho** | Endpoint `/metrics` para monitoramento |

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vite + React)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ ChatPage.tsx │──│ ChatPage.css │  │ index.html (SPA)  │  │
│  └──────┬──────┘  └──────────────┘  └───────────────────┘  │
│         │                                                      │
│         │  HTTP POST /api/chat                                 │
└─────────┼─────────────────────────────────────────────────────┘
          │
┌─────────┼─────────────────────────────────────────────────────┐
│         ▼                                                      │
│                    Backend (FastAPI + Python)                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   response_service.py                     │  │
│  │  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐   │  │
│  │  │analyzer │─▶│ planner  │─▶│ fusion │─▶│ ranking  │   │  │
│  │  └─────────┘  └──────────┘  └────────┘  └──────────┘   │  │
│  └─────────────────────────┬───────────────────────────────┘  │
│                            ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    groq_service.py                       │  │
│  │            (LLaMA 3.1 8B via Groq API)                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                            │                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    search_engine.py                      │  │
│  │         (PDF → Chunks → Busca semântica + rerank)        │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### Fluxo de uma pergunta

1. **📝 Análise** — O `analyzer` classifica a intenção da pergunta
2. **🔎 Busca** — O `search_engine` consulta o índice do PDF com relevância semântica
3. **🧩 Fusão** — O `fusion` deduplica e combina trechos relevantes
4. **📊 Ranking** — O `ranking` ordena os chunks por similaridade
5. **🤖 Geração** — O `groq_service` constrói o prompt e gera a resposta via LLaMA 3.1
6. **✅ Pós-processamento** — O `post_processor` limpa e formata a resposta final

---

## 🛠️ Stack Tecnológica

### Frontend
| Tecnologia | Versão | Uso |
|---|---|---|
| React | 19.2 | Interface de usuário |
| TypeScript | 6.0 | Tipagem estática |
| Vite | 8.1 | Bundler e dev server |
| Tailwind CSS | 4.3 | Estilização utilitária |
| React Router | 7.18 | Navegação SPA |

### Backend
| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.12 | Runtime |
| FastAPI | — | Framework HTTP assíncrono |
| PyMuPDF | — | Extração de texto do PDF |
| Groq SDK | — | API do modelo LLaMA 3.1 |
| Uvicorn | — | Servidor ASGI |

---

## 🚀 Como Executar

### Pré-requisitos

- [Node.js](https://nodejs.org/) ≥ 18
- [Python](https://python.org/) ≥ 3.12
- [Groq API Key](https://console.groq.com/)

### 1. Backend

```bash
cd backend

# Crie o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Instale as dependências
pip install -r requirements.txt

# Configure a chave da API
# Edite o arquivo .env com sua GROQ_API_KEY

# Inicie o servidor
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend

# Instale as dependências
npm install

# Inicie o dev server
npm run dev
```

O frontend estará disponível em `http://localhost:5173` e o backend em `http://localhost:8000`.

---

## 🌐 Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/chat` | Enviar mensagem e obter resposta |
| `GET` | `/health` | Verificar status do servidor |
| `POST` | `/reset` | Resetar memória da conversa |
| `GET` | `/metrics` | Métricas de desempenho |

---

## 📁 Estrutura do Projeto

```
📦 senai-jau-chatbot
├── 📂 backend
│   ├── 📂 app                 # Versão modular (Fase 4)
│   │   ├── 📂 api             # Rotas FastAPI
│   │   ├── 📂 core            # Métricas e core
│   │   ├── 📂 llm             # Integração Groq, prompts
│   │   ├── 📂 memory          # Memória de conversa
│   │   ├── 📂 rag             # Chunker, fusion, planner, ranking
│   │   └── 📂 services        # Orquestração do pipeline
│   ├── 📂 assets/documents    # PDF do plano de curso
│   ├── 📂 static              # HTML estático + imagens
│   ├── main.py                # Servidor FastAPI (Fase 3)
│   ├── search_engine.py       # Motor de busca RAG
│   ├── prompt_builder.py      # Construção de prompts
│   └── requirements.txt       # Dependências Python
│
├── 📂 frontend
│   ├── 📂 img                 # Imagens (salas, background)
│   ├── 📂 src/pages           # Componentes React
│   ├── index.html             # Página principal SPA
│   ├── ChatPage.css           # Estilos do chat
│   ├── package.json           # Dependências Node
│   └── vite.config.ts         # Configuração Vite + proxy
│
├── 📂 .github/workflows       # CI/CD
├── .gitignore
└── README.md
```

---

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Obrigatória |
|---|---|---|
| `GROQ_API_KEY` | Chave da API Groq para acesso ao LLaMA 3.1 | ✅ |
| `VITE_API_URL` | URL base da API (opcional, usa proxy em dev) | ❌ |

---

## 📄 Licença

Este projeto é desenvolvido para fins educacionais pelo **SENAI Jaú**.

---

<div align="center">
  <p>
    <strong>SENAI Jaú</strong> — Curso Técnico em Desenvolvimento de Sistemas
  </p>
  <p>
    <sub>Feito com 💻 e ☕ pelos alunos e instrutores do SENAI</sub>
  </p>
</div>
