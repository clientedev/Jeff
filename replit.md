# Sistema SRI SENAI 1.03

## Visão Geral
Sistema web completo de Serviço de Relacionamento com a Indústria (SRI) do SENAI, desenvolvido em Python Flask com PostgreSQL. O sistema permite gestão de empresas, visitas técnicas, demandas/oportunidades, com controle de permissões, relatórios e auditoria.

## Tecnologias Utilizadas
- **Backend**: Python 3.11 + Flask
- **Banco de Dados**: PostgreSQL (Replit Database)
- **ORM**: SQLAlchemy + Flask-Migrate
- **Autenticação**: Flask-Login + Werkzeug Security
- **Frontend**: Bootstrap 5 + Jinja2 + JavaScript
- **Gráficos**: Chart.js
- **Exportação**: Pandas + openpyxl (Excel) + ReportLab (PDF)
- **Segurança**: Flask-WTF (CSRF Protection)

## Estrutura do Projeto
```
├── app.py                  # Aplicação principal Flask
├── config.py              # Configurações do sistema
├── models/                # Modelos do banco de dados
│   ├── user.py           # Modelo de usuários com perfis
│   ├── empresa.py        # Modelo de empresas
│   ├── visita.py         # Modelo de visitas técnicas
│   ├── demanda.py        # Modelo de demandas/oportunidades
│   └── log.py            # Modelo de logs de auditoria
├── routes/               # Rotas/Blueprints da aplicação
│   ├── auth.py          # Autenticação (login/logout)
│   ├── dashboard.py     # Dashboard com métricas
│   ├── empresas.py      # CRUD de empresas
│   ├── visitas.py       # CRUD de visitas
│   ├── demandas.py      # CRUD de demandas
│   ├── relatorios.py    # Exportação de relatórios
│   └── admin.py         # Gerenciamento de usuários
├── templates/           # Templates HTML
└── static/             # Arquivos estáticos (CSS, JS, uploads)
```

## Funcionalidades Principais

### 1. Sistema de Autenticação e Permissões
- Login seguro com hash de senha (Werkzeug)
- Proteção CSRF em todos os formulários
- 4 perfis de acesso:
  - **Administrador**: Acesso total + gerenciamento de usuários
  - **Coordenador**: Acesso completo aos dados + pode excluir
  - **Atendente**: Cria e edita empresas, visitas e demandas
  - **Leitor**: Apenas visualização

### 2. Gestão de Empresas
- CRUD completo com campos: nome, CNPJ, segmento, porte, contato, etc.
- Busca inteligente por nome, CNPJ, cidade ou segmento
- Status: Ativo, Inativo, Prospect, Estratégico
- Vinculação com visitas e demandas

### 3. Visitas Técnicas
- Cadastro com data, empresa, responsável, objetivo, status
- Status: Planejada, Realizada, Cancelada
- Filtros e paginação
- Histórico completo por empresa

### 4. Demandas/Oportunidades
- Tipos: Curso, Consultoria, Inovação, Tecnologia, etc.
- Status: Nova, Em andamento, Concluída, Cancelada
- Valor estimado e controle de conversão para projeto
- Setor responsável e histórico

### 5. Dashboard com Métricas
- Total de empresas ativas
- Visitas realizadas no mês
- Demandas abertas vs concluídas
- Taxa de conversão de demandas
- Gráficos Chart.js com dados em tempo real
- Últimas visitas e demandas

### 6. Relatórios e Exportação
- Exportação para Excel (XLSX) usando Pandas/openpyxl
- Relatórios de empresas, visitas e demandas
- Filtros aplicados nas exportações

### 7. Logs e Auditoria
- Registro de todas as ações: login, criação, edição, exclusão
- IP address e timestamp
- Descrição detalhada da ação
- Acesso restrito a administradores

### 8. Upload de Documentos
- Suporte a PDF, DOCX, XLSX, PNG, JPG
- Organização por pasta (empresas/visitas/demandas)
- Limite de 16MB por arquivo

## Credenciais Padrão
- **Email**: admin@senai.com
- **Senha**: admin123

> ⚠️ **Importante**: Altere a senha do administrador após o primeiro acesso!

## Como Executar
O sistema já está configurado e rodando automaticamente via workflow:
1. O servidor Flask inicia automaticamente na porta 5000
2. O banco de dados PostgreSQL está configurado via variável DATABASE_URL
3. O usuário admin é criado automaticamente na primeira execução
4. Acesse pelo navegador através do preview do Replit

## Variáveis de Ambiente Necessárias
- `DATABASE_URL`: URL do PostgreSQL (configurado automaticamente)
- `SESSION_SECRET`: Chave secreta para sessões (configurado automaticamente)

## Segurança Implementada
- ✅ Hash de senhas com Werkzeug
- ✅ Proteção CSRF em todos os formulários
- ✅ Cookies seguros e HttpOnly
- ✅ Proteção de rotas com @login_required
- ✅ Controle de permissões por perfil
- ✅ Logs de auditoria completos
- ✅ Validação de sessão

## Arquitetura
- **Padrão MVC** com Blueprints modulares
- **SQLAlchemy ORM** para abstração do banco
- **Flask-Migrate** para migrações (quando necessário)
- **Templates responsivos** com Bootstrap 5
- **Cores institucionais** do SENAI (azul #003DA5)

## Próximas Fases (Sugeridas)
1. Importação em massa de empresas via Excel/CSV
2. Calendário interativo (FullCalendar.js)
3. Notificações por email (Flask-Mail)
4. Recuperação de senha
5. 2FA (autenticação de dois fatores)
6. Integração com API ReceitaWS (consulta CNPJ)
7. Mapa de calor de visitas (Google Maps)
8. Backup automático do banco

## Data de Criação
13 de Outubro de 2025

## Desenvolvido para
SENAI 1.03 - Serviço de Relacionamento com a Indústria
