# KnowYourFan

Uma aplicação web desenvolvida com **Flask**, que combina autenticação de usuários com funcionalidades de inteligência artificial para entrega de notícias personalizadas e validação de documentos.

Acesse em: [knowyourfan.pythonanywhere.com](https://knowyourfan.pythonanywhere.com)

## ✨ Funcionalidades

- **Cadastro e Login de Usuários**  
  Permite a criação de contas e autenticação com credenciais seguras.

- **Página Inicial com Notícias Personalizadas**  
  Após o login, o usuário é direcionado para uma página inicial onde recebe **notícias relevantes** com base em inteligência artificial.

- **Barra de Navegação com Acesso Rápido**:
  - 🗨️ **Chatbot**: Um botão que abre um chat lateral para conversas com um assistente inteligente.
  - ✅ **Verificar Documento**: Página de upload onde o sistema analisa uma imagem enviada (ex: documento) e verifica se as informações são compatíveis com os dados do usuário.
  - 🔗 **Vincular Contas**: Integração com plataformas externas, como a **Twitch**, permitindo o vínculo da conta do usuário.

## 🚀 Acessar Online

Acesse a aplicação diretamente pelo link:  
🔗 [https://knowyourfan.pythonanywhere.com](https://knowyourfan.pythonanywhere.com)

## 🛠️ Instalação Local

Caso prefira rodar localmente:

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Na base no diretório, crie um arquivo chamado config.py e nele insira as seguintes informações:
   ```
   SECRET_KEY = "RANDOM_SECRET_KEY"
   DATABASE = "PATH_TO_YOUR_DATABASE_FILE"
   GOOGLE_GEMINI_API_KEY = "YOUR_GOOGLE_GEMINI_API_KEY"
   TWITCH_OAUTH_CLIENT_ID = "YOUR_TWITCH_OAUTH_CLIENT_ID"
   TWITCH_OAUTH_CLIENT_SECRET = "YOUR_TWITCH_OAUTH_CLIENT_SECRET"
   ```
4. Inicialize o banco de dados:
   ```
   flask --app app init-db
   ```
5. Execute o servidor Flask:
   ```
   flask run
   ```
