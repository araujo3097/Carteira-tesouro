# Carteira NTN-B Principal — site com atualização automática

Este site consulta um arquivo `dados.json` com o PU de venda mais recente de
cada vencimento da **NTN-B Principal (Tesouro IPCA+)** e da **NTN-F (Tesouro
Prefixado com Juros Semestrais)**. Um robô roda **automaticamente todo dia
útil** (via GitHub Actions) e atualiza esse arquivo sozinho — sem você
precisar fazer nada depois de configurar uma vez.

## Estrutura do projeto

```
site_tesouro/
├── index.html                        → o site
├── dados.json                        → dados atuais (atualizado pelo robô)
├── scripts/
│   └── gerar_dados_json.py           → script que baixa e processa os dados
└── .github/workflows/atualizar.yml   → agenda o robô para rodar todo dia
```

## Passo a passo para publicar (uma vez só)

### 1. Criar o repositório no GitHub
1. Acesse [github.com/new](https://github.com/new)
2. Dê um nome (ex: `carteira-tesouro`) → Create repository
3. Suba os arquivos desta pasta (pelo site do GitHub, arraste os arquivos em
   "Add file" → "Upload files", ou via linha de comando com `git push`)

### 2. Ativar o GitHub Pages (hospedagem gratuita)
1. No repositório → **Settings** → **Pages**
2. Em "Source", escolha **Deploy from a branch** → branch `main`, pasta `/ (root)`
3. Salve. Em 1–2 minutos seu site estará em:
   `https://SEU-USUARIO.github.io/carteira-tesouro/`

### 3. Ativar o robô de atualização (GitHub Actions)
Não precisa fazer nada além do que já está no repositório — o arquivo
`.github/workflows/atualizar.yml` já configura tudo:
- Roda automaticamente **de segunda a sexta, às 20h (horário de Brasília)**
- Baixa o arquivo mais novo do Tesouro, extrai o PU de venda de cada
  vencimento e atualiza o `dados.json`
- Publica (commit + push) a alteração direto no repositório

O GitHub Pages detecta a mudança e o site já mostra o dado novo na próxima
vez que alguém abrir a página.

### 4. Testar sem esperar o agendamento
No repositório → aba **Actions** → workflow "Atualizar dados do Tesouro" →
botão **Run workflow**. Roda na hora, pra você conferir que está tudo certo.

## Como o site sabe se o dado está atualizado?

Logo abaixo do título, aparece um selo:
- **Verde** "Atualizado automaticamente em [data/hora]" → tudo funcionando
- **Bege** "Usando dados locais... dados.json não encontrado" → aparece só
  se você abrir o `index.html` direto no navegador (sem publicar no GitHub
  Pages) ou se o `dados.json` ainda não existir

## Ajustando o horário do robô

No arquivo `.github/workflows/atualizar.yml`, a linha:
```yaml
- cron: '0 23 * * 1-5'
```
Define 23:00 UTC (20h de Brasília) em dias úteis. Horários no GitHub Actions
são sempre em UTC — ajuste conforme necessário.

## Adicionando mais títulos no futuro

No `scripts/gerar_dados_json.py`, existe uma lista `TITULOS` no topo do
arquivo. Para incluir outro título (ex: LFT, LTN), basta adicionar mais uma
entrada nessa lista com o "slug" usado no nome do arquivo do Tesouro (visível
copiando o link de download em
[histórico de preços e taxas](https://www.tesourodireto.com.br/produtos/dados-sobre-titulos/historico-de-precos-e-taxas))
e o nome de exibição. O site já lê automaticamente qualquer título presente
no `dados.json`, agrupando por tipo no menu de seleção.
