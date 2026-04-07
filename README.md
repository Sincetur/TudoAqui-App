# 🚀 TUDOaqui SuperApp - Fase 1 MVP

## 📋 Visão Geral

TUDOaqui é um **SuperApp** modular para Angola que integra múltiplos serviços numa única plataforma.

### Fase 1 - MVP: Tuendi Taxi 🚕

O MVP foca no módulo de mobilidade **Tuendi Taxi**, incluindo:
- ✅ Autenticação via OTP + JWT
- ✅ Gestão de motoristas
- ✅ Solicitação e gestão de corridas
- ✅ Sistema de pagamentos com Ledger
- ✅ Avaliações

---

## 🛠️ Stack Tecnológica

| Componente | Tecnologia |
|------------|------------|
| **Backend** | FastAPI (Python 3.12) |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Auth** | JWT + OTP |
| **Package Manager** | uv |

---

## 🚀 Quick Start

### Pré-requisitos
- Docker & Docker Compose
- Python 3.12+ (para desenvolvimento local)

### 1. Clonar e Configurar

```bash
cd tudoaqui-mvp

# Copiar variáveis de ambiente
cp backend/.env.example backend/.env
```

### 2. Iniciar com Docker

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f api
```

### 3. Acessar

- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **pgAdmin** (opcional): http://localhost:5050

---

## 📁 Estrutura do Projeto

```
tudoaqui-mvp/
├── backend/
│   ├── src/
│   │   ├── auth/           # Autenticação (OTP, JWT)
│   │   ├── users/          # Utilizadores
│   │   ├── tuendi/         # Módulo Tuendi
│   │   │   ├── drivers/    # Motoristas
│   │   │   ├── rides/      # Corridas
│   │   │   └── matching/   # Matching algorithm
│   │   ├── payments/       # Pagamentos e Ledger
│   │   ├── notifications/  # Notificações (futuro)
│   │   ├── config.py       # Configurações
│   │   ├── database.py     # Conexão DB
│   │   └── main.py         # Aplicação principal
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
├── database/
│   └── V1__create_schema.sql
├── frontend/               # Flutter (futuro)
├── docs/
└── docker-compose.yml
```

---

## 🔐 Autenticação

### Fluxo de Login (OTP)

1. **Solicitar OTP**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"telefone": "+244923456789"}'
```

2. **Verificar OTP**
```bash
curl -X POST http://localhost:8000/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"telefone": "+244923456789", "codigo": "123456"}'
```

3. **Usar Access Token**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
```

---

## 🚕 API Tuendi

### Fluxo de Corrida

| Passo | Endpoint | Actor |
|-------|----------|-------|
| 1 | `POST /api/v1/rides/estimate` | Cliente |
| 2 | `POST /api/v1/rides/request` | Cliente |
| 3 | `GET /api/v1/rides/pending/nearby` | Motorista |
| 4 | `POST /api/v1/rides/{id}/accept` | Motorista |
| 5 | `POST /api/v1/rides/{id}/start` | Motorista |
| 6 | `POST /api/v1/rides/{id}/finish` | Motorista |
| 7 | `POST /api/v1/rides/{id}/rate` | Ambos |

### Endpoints Principais

#### Cliente
- `POST /api/v1/rides/estimate` - Estimar preço
- `POST /api/v1/rides/request` - Solicitar corrida
- `GET /api/v1/rides/current` - Corrida atual
- `POST /api/v1/rides/{id}/cancel` - Cancelar
- `GET /api/v1/rides/history/client` - Histórico

#### Motorista
- `POST /api/v1/drivers/register` - Registar como motorista
- `POST /api/v1/drivers/me/online` - Ficar online/offline
- `POST /api/v1/drivers/me/location` - Atualizar localização
- `GET /api/v1/rides/pending/nearby` - Ver corridas pendentes
- `POST /api/v1/rides/{id}/accept` - Aceitar corrida
- `POST /api/v1/rides/{id}/start` - Iniciar corrida
- `POST /api/v1/rides/{id}/finish` - Finalizar corrida

---

## 💰 Preços (Fase 1)

| Parâmetro | Valor |
|-----------|-------|
| Taxa da plataforma | 20% |
| Preço por km | 150 Kz |
| Preço por minuto | 50 Kz |
| Taxa mínima | 500 Kz |

---

## 🧪 Desenvolvimento Local

### Sem Docker

```bash
cd backend

# Instalar uv
pip install uv

# Instalar dependências
uv sync

# Configurar .env
cp .env.example .env

# Iniciar PostgreSQL e Redis localmente

# Rodar API
uv run uvicorn src.main:app --reload
```

### Testes

```bash
cd backend
uv run pytest
```

---

## 📊 Modelo de Dados

### Tabelas Principais

- **users** - Utilizadores (todos os roles)
- **drivers** - Perfis de motoristas
- **rides** - Corridas
- **ratings** - Avaliações
- **payments** - Pagamentos
- **ledger_entries** - Livro razão (split de pagamentos)
- **wallets** - Carteiras (Fase 2)

### Roles de Utilizadores

```
cliente | motorista | entregador | organizador | 
vendedor | anfitriao | agente | staff | admin
```

---

## 🗺️ Roadmap

### ✅ Fase 1 - MVP (Atual)
- [x] Auth (OTP + JWT)
- [x] Tuendi Taxi (corridas)
- [x] Motoristas (registo, online/offline)
- [x] Pagamentos (estrutura)
- [x] Ledger (split)

### ✅ Fase 1.1 - Frontend Flutter
- [x] Estrutura Flutter com Bloc
- [x] Telas de Auth (Login, OTP)
- [x] Home Screen
- [x] Request Ride Screen (com mapa)
- [x] Ride Tracking Screen
- [x] Profile Screen
- [x] WebSocket Service
- [x] API Client completo

### 🔜 Fase 2
- [ ] App Motorista completo
- [ ] Push Notifications (Firebase)
- [ ] Integração Multicaixa Express
- [ ] Integração Mobile Money
- [ ] Testes E2E

### 🔮 Fases Futuras
- [ ] Tuendi Entrega
- [ ] Módulo Eventos
- [ ] Módulo Marketplace
- [ ] Módulo Alojamento
- [ ] Módulo Turismo
- [ ] Módulo Real Estate
- [ ] Wallet B2B

---

## 📄 Licença

Propriedade de TUDOaqui © 2025

---

## 👥 Contacto

- **Email**: dev@tudoaqui.ao
- **Website**: https://tudoaqui.ao
