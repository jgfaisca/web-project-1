# Relatório - Sistema de Monitorização de Equipamentos

## Informações Gerais

**Data:** 18 de Maio de 2026  
**Projeto:** Sistema de Monitorização de Equipamentos (IoT)  
**Baseado em:** trabalho-pratico.pdf

---

## 1. Resumo Executivo

Este projeto implementa um **Sistema de Monitorização de Equipamentos** com arquitetura cliente-servidor, utilizando:
- **Backend:** Python/Flask com API REST
- **Banco de Dados:** SQLite3
- **Frontend:** HTML5/CSS3/JavaScript
- **Autenticação:** JWT (JSON Web Tokens)
- **Documentação:** Swagger/OpenAPI

O sistema permite a gestão dinâmica de equipamentos, clientes e monitorização ativa de alertas térmicos.

---

## 2. Requisitos Implementados

### ✅ A. Gestão do Ciclo de Vida (API REST)

| Funcionalidade | Método | Endpoint | Status |
|---|---|---|---|
| Remover Equipamento | DELETE | `/api/equipamento/<id>` | ✅ Implementado |
| Mudar Cliente | PATCH | `/api/equipamento/<id>` | ✅ Implementado |
| Interface Cliente | - | Web UI | ✅ Implementado |
| Segurança JWT | - | Todos POST/PATCH/DELETE | ✅ Implementado |
| Validação HTTP | - | 404, 401, 400 | ✅ Implementado |

**Rotas Adicionais (CRUD Completo):**
- `GET /api/equipamentos` - Listar todos
- `GET /api/equipamento/<id>` - Obter um
- `POST /api/equipamento` - Criar
- `GET /api/clientes` - Listar clientes
- `GET /api/cliente/<nif>` - Obter cliente
- `POST /api/cliente` - Criar cliente

### ✅ B. Persistência e Integridade (SQLite)

| Requisito | Status |
|---|---|
| Relacionamentos com FK | ✅ Implementado |
| Validação de integridade referencial | ✅ Implementado |
| connection.commit() em alterações | ✅ Implementado |
| Uso de script v3 como base | ✅ Utilizado |

**Tabelas Criadas:**
- `Cliente` - Dados dos clientes
- `Equipamento` - Equipamentos registados
- `PropriedadeEquipamento` - Relacionamento com histórico
- `Temperatura` - Registos de temperatura
- `limites_sensores` - Limites de alerta por sensor
- `alertas_sensores` - Histórico de anomalias

### ✅ C. Sistema de Alertas

| Funcionalidade | Status |
|---|---|
| Monitorização ativa de temperaturas | ✅ Implementado |
| Registo de alertas em anomalias | ✅ Implementado |
| Processamento assíncrono (threading) | ✅ Implementado |
| Tabelas de persistência | ✅ Implementado |
| Rota GET /api/alertas protegida | ✅ Implementado |
| Interface de polling no frontend | ✅ Implementado |
| Fetch API com async/await | ✅ Implementado |
| Try/catch para tratamento de erros | ✅ Implementado |
| Manipulação dinâmica do DOM | ✅ Implementado |

### ✅ D. Intercâmbio de Informação (JSON e GeoJSON)

| Requisito | Status |
|---|---|
| JSON em todas as mensagens | ✅ Implementado |
| Content-Type: application/json | ✅ Implementado |
| GeoJSON (opcional) | ⏳ Não implementado |

### ✅ E. Registo da Leitura de Sensores

| Funcionalidade | Status |
|---|---|
| Script temp_rand_main.py | ✅ Melhorado |
| Suporte a JWT no script | ✅ Implementado |
| Rota /temperatura | ✅ Implementado |

### ✅ F. Ferramentas de Teste e CLI

| Ferramenta | Status |
|---|---|
| Swagger/OpenAPI em /api/docs | ✅ Implementado (Flasgger) |
| Script de teste Python (script_automacao.py) | ✅ Implementado |
| Teste de operações CRUD | ✅ Implementado |

### ✅ G. Ambientes e Tecnologias do Cliente

| Ambiente | Status |
|---|---|
| Mobile (Browser otimizado) | ✅ Implementado |
| PC/Desktop (Web Browser) | ✅ Implementado |

### ✅ H. Persistência e Segurança

| Requisito | Status |
|---|---|
| Integridade referencial | ✅ Implementado |
| Validação de input no cliente | ✅ Implementado |

---

## 3. Estrutura de Ficheiros

```
web-project-1/
├── server_main/
│   ├── server_main.py           # Servidor Flask com API REST completa
│   ├── static/
│   │   ├── index.html           # Frontend (UI responsiva)
│   │   └── css/
│   │       └── styles.css       # Estilos CSS
│   └── templates/               # Templates HTML adicionais
├── client_temp/
│   └── temp_rand_main.py        # Script de leitura de sensores (com JWT)
├── sql/
│   └── 5_IMPLEMENTACAO_v3.sql   # Schema da base de dados
├── script_automacao.py          # Suite de testes automatizados
├── requirements.txt             # Dependências Python
├── db/
│   └── test_database.db         # Base de dados SQLite
└── doc/                         # Documentação do projeto
```

---

## 4. Funcionalidades Principais

### 4.1 Backend (server_main.py)

**Decorador JWT:**
```python
@verificar_jwt
def funcao_protegida():
    # Apenas com token válido
```

**Processamento Assíncrono de Alertas:**
```python
processar_alertas_assincrono(equipamento_id, temp0, temp1, temp2)
# Thread separada para validação de limites
```

**Rotas Principais:**
- `/api/equipamentos` - GET
- `/api/equipamento` - POST, GET, PATCH, DELETE
- `/api/clientes` - GET
- `/api/cliente` - POST, GET
- `/api/alertas` - GET (protegido)
- `/temperatura` - POST (protegido)
- `/api/docs` - Documentação Swagger

### 4.2 Frontend (index.html)

**Abas Principais:**
1. **Equipamentos** - CRUD de equipamentos
2. **Clientes** - CRUD de clientes
3. **Alertas** - Visualização de histórico

**Características:**
- Interface responsiva (mobile-friendly)
- Validação de input
- Tratamento de erros
- Atualização dinâmica sem reload
- Confirmação de ações destrutivas

### 4.3 Script de Testes (script_automacao.py)

**Testes Executados:**
1. Listar equipamentos
2. Criar clientes
3. Criar equipamentos
4. Registar temperaturas (normal e anomalia)
5. Listar alertas
6. Obter equipamento específico
7. Mudar cliente de equipamento
8. Apagar equipamento

---

## 5. Instruções de Uso

### 5.1 Instalação

```bash
# Ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 5.2 Iniciar o Servidor

```bash
cd server_main
python server_main.py
```

Servidor estará disponível em: `http://localhost:5000`

### 5.3 Acessar Interface Web

Abra no browser: `http://localhost:5000`

### 5.4 Gerar Token JWT

```bash
curl http://localhost:5000/api/gerar-token
```

### 5.5 Executar Testes Automatizados

```bash
python script_automacao.py
```

### 5.6 Registar Temperaturas Simuladas

```bash
# Equipamento ID 1
python client_temp/temp_rand_main.py 1

# Equipamento ID 2
python client_temp/temp_rand_main.py 2
```

### 5.7 Acessar Documentação Swagger

`http://localhost:5000/api/docs`

---

## 6. Endpoints da API

### 6.1 Equipamentos

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/api/equipamentos` | Listar todos | ❌ |
| GET | `/api/equipamento/<id>` | Obter um | ❌ |
| POST | `/api/equipamento` | Criar novo | ✅ JWT |
| PATCH | `/api/equipamento/<id>` | Mudar cliente | ✅ JWT |
| DELETE | `/api/equipamento/<id>` | Remover | ✅ JWT |

### 6.2 Clientes

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| GET | `/api/clientes` | Listar todos | ❌ |
| GET | `/api/cliente/<nif>` | Obter um | ❌ |
| POST | `/api/cliente` | Criar novo | ✅ JWT |

### 6.3 Temperaturas e Alertas

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| POST | `/temperatura` | Registar temperatura | ✅ JWT |
| GET | `/api/alertas` | Listar alertas | ✅ JWT |
| GET | `/api/temperaturas/<id>` | Listar por equipamento | ❌ |

### 6.4 Utilitários

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/gerar-token` | Gerar novo JWT |
| GET | `/api/docs` | Documentação Swagger |

---

## 7. Exemplos de Requisições

### 7.1 Criar Cliente

```bash
curl -X POST http://localhost:5000/api/cliente \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nif": "123456789012",
    "nome": "Empresa XYZ",
    "localidade": "Lisboa"
  }'
```

### 7.2 Criar Equipamento

```bash
curl -X POST http://localhost:5000/api/equipamento \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_serie": "SER_001",
    "cliente_nif": "123456789012"
  }'
```

### 7.3 Registar Temperatura

```bash
curl -X POST http://localhost:5000/temperatura \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "equipamento_id": 1,
    "temp0": 25.5,
    "temp1": 26.0,
    "temp2": 24.5
  }'
```

### 7.4 Mudar Cliente (PATCH)

```bash
curl -X PATCH http://localhost:5000/api/equipamento/1 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cliente_nif": "999999999999"}'
```

### 7.5 Apagar Equipamento

```bash
curl -X DELETE http://localhost:5000/api/equipamento/1 \
  -H "Authorization: Bearer TOKEN"
```

---

## 8. Segurança

### 8.1 JWT

- Token gerado com HS256
- Válido para operações de modificação (POST, PATCH, DELETE, PUT)
- Verificação obrigatória no decorador `@verificar_jwt`

### 8.2 Validação

- Validação de campos obrigatórios
- Verificação de integridade referencial (FK)
- Códigos de estado HTTP apropriados
- Tratamento de exceções

### 8.3 Base de Dados

- `PRAGMA foreign_keys = ON` habilitado
- `connection.commit()` em cada operação
- Constraints de check nas tabelas

---

## 9. Testes Realizados

### 9.1 Testes Funcionais

✅ Criar cliente com validação de NIF (12 dígitos)  
✅ Criar equipamento com validação de série única  
✅ Registar temperatura e gerar alerta  
✅ Atualizar cliente de equipamento  
✅ Remover equipamento (DELETE)  
✅ Listar todos os recursos  
✅ Proteger rotas com JWT  

### 9.2 Testes de Validação

✅ Erro 400 - Dados faltando  
✅ Erro 401 - Token inválido  
✅ Erro 404 - Recurso não encontrado  
✅ Integridade referencial respeitada  

### 9.3 Testes de Interface

✅ Criar novo cliente via formulário  
✅ Criar novo equipamento  
✅ Ver lista de alertas em tempo real  
✅ Responsividade em dispositivos móveis  
✅ Manipulação do DOM sem reload  

---

## 10. Melhorias Realizadas

**Em relação ao requisito inicial:**

1. ✅ **Swagger/OpenAPI** - Adicionado com Flasgger
2. ✅ **CRUD Completo** - Todas as operações implementadas
3. ✅ **Frontend Aprimorado** - Interface profissional com abas
4. ✅ **Script de Testes** - Automação completa
5. ✅ **Validação Robusta** - Input validation no cliente e servidor
6. ✅ **Documentação API** - Docstrings em todas as rotas
7. ✅ **Tratamento de Erros** - Try/catch em todos os endpoints
8. ✅ **Mobile-Friendly** - Design responsivo

---

## 11. Limitações e Futuras Melhorias

**Não Implementado:**
- GeoJSON (opcional no requisito)
- Autenticação OAuth
- Dashboard com gráficos
- Notificações em tempo real (WebSocket)
- Exportação de dados (CSV/PDF)

**Possíveis Melhorias:**
- Adicionar testes unitários com pytest
- Implementar rate limiting
- Adicionar logging estruturado
- Cache de consultas frequentes
- Paginação em listas grandes

---

## 12. Conclusão

O sistema implementa **todos os requisitos obrigatórios** especificados no trabalho prático:

- ✅ Gestão do ciclo de vida (CRUD com DELETE/PATCH)
- ✅ Persistência e integridade referencial
- ✅ Sistema de alertas com monitorização ativa
- ✅ Autenticação JWT
- ✅ API REST com JSON
- ✅ Interface cliente web responsiva
- ✅ Documentação Swagger
- ✅ Script de teste automatizado

O projeto está **pronto para produção** e segue boas práticas de desenvolvimento.

---

**Ficheiros Entregues:**
- `server_main/server_main.py` - Backend
- `server_main/static/index.html` - Frontend
- `client_temp/temp_rand_main.py` - Script de sensores
- `script_automacao.py` - Testes automatizados
- `sql/5_IMPLEMENTACAO_v3.sql` - Schema da BD
- `requirements.txt` - Dependências
- `RELATORIO.md` - Este documento

---

**Data:** 18 de Maio de 2026
