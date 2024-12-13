# AI Assistant

Um assistente AI com interface de chat, construído com React e FastAPI.

## Estrutura do Projeto

```
/ai-assistant
  /frontend          # Aplicação React
    /src
      /components    # Componentes React
      /utils         # Utilitários
  /backend           # API FastAPI
    /core            # Lógica principal
    /api             # Endpoints da API
    /config          # Configurações
  /docker            # Arquivos Docker
```

## Requisitos

- Docker e Docker Compose
- Node.js 18+ (para desenvolvimento)
- Python 3.11+ (para desenvolvimento)

## Configuração

1. Clone o repositório
2. Crie um arquivo .env na raiz do projeto com as seguintes variáveis:

```env
OPENAI_API_KEY=sua_chave_api
DEBUG=True  # Apenas em desenvolvimento
```

## Executando com Docker

```bash
# Construir e iniciar os containers
docker-compose up --build

# Parar os containers
docker-compose down
```

## Desenvolvimento Local

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate no Windows
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `GET /health` - Verificação de saúde da API
- `POST /api/chat` - Endpoint para chat via HTTP
- `WS /ws/chat` - Endpoint WebSocket para chat em tempo real
- `GET /tools` - Lista ferramentas disponíveis
- `POST /tool/{tool_name}` - Executa uma ferramenta específica

## Contribuindo

1. Crie uma branch para sua feature
2. Faça commit das suas mudanças
3. Crie um Pull Request

## Licença

MIT
