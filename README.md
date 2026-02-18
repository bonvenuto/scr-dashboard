# 📊 SCR Credit Analytics: Pipeline de Engenharia e Visualização

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white)

## 📌 Visão Executiva
Este projeto é uma solução *end-to-end* de **Analytics Engineering** voltada para o acompanhamento do mercado de crédito brasileiro. Utilizando dados públicos do **Sistema de Informações de Crédito (SCR)** do Banco Central do Brasil, a aplicação processa grandes volumes de dados brutos e os converte em um painel executivo focado em tomada de decisão estratégica, gestão de portfólio e análise de risco (inadimplência/Over90).

## 🏗️ Arquitetura e Fluxo de Dados (Modern Data Stack)

A arquitetura foi desenhada priorizando performance, modularidade e isolamento de responsabilidades:

1. **Extract (Python):** Script autônomo (`extract.py`) que faz requisições ao portal de dados abertos do BCB, processa os arquivos ZIP de safras específicas (2024 a 2026) e converte os relatórios CSV em arquivos `.parquet`. Essa abordagem reduz drasticamente o tempo de I/O e o custo de armazenamento.
2. **Transform (dbt + DuckDB):** Modelagem dimensional focada em regras de negócio. O DuckDB atua como *engine* OLAP em memória, garantindo alta velocidade em consultas analíticas.
   * **Staging (`stg_scr_data`):** Higienização de dados, tipagem forte (cast de *strings* para *dates/floats*) e padronização.
   * **Marts (`mart_scr_*`):** Tabelas agregadas que entregam valor direto para a visualização, lidando com cálculos complexos de Variação Mensal (MoM) e representatividade em pontos percentuais (p.p.).
3. **Serve (Streamlit):** Interface *web* de alto nível, com gráficos desenvolvidos em `plotly.graph_objects` para controle preciso de eixos duplos, labels customizados (Mi/Bi/Tri) e padrões de formatação executiva.
4. **Deploy (Docker):** Ambiente 100% conteinerizado (via `docker-compose`), garantindo que o pipeline seja reproduzível em qualquer máquina ou servidor.

## 📂 Estrutura de Diretórios

```text
├── app/
│   └── dashboard.py               # Front-end da aplicação e lógicas de UI/UX
├── dbt_scr/
│   ├── models/
│   │   ├── staging/               # Camada Prata: Tratamento e limpeza
│   │   └── marts/                 # Camada Ouro: Tabelas consolidadas por dimensão
│   ├── dbt_project.yml            # Configurações gerais do projeto dbt
│   └── profiles.yml               # Mapeamento da conexão dbt <> DuckDB
├── scripts/
│   └── extract.py                 # Orquestração do web scraping e geração de Parquets
├── .gitignore                     # Proteção contra vazamento de dados locais/bancos
├── docker-compose.yml             # Orquestração de serviços
├── Dockerfile                     # Construção da imagem do ambiente Python/Streamlit
└── requirements.txt               # Trava de dependências (incluindo Streamlit >=1.36)
```

## 📈 Funcionalidades do Dashboard
O painel foi estruturado para refletir as necessidades de uma diretoria de Políticas de Crédito ou MIS:

**Big Numbers:** Cards de resumo mostrando o Volume Total de Carteira Ativa e o Índice de Inadimplência, comparando o mês atual com o mês anterior (cálculos de variação relativa e variação absoluta em p.p.).

**Tendência Macro:** Gráfico histórico (Line Chart) cruzando a evolução da Inadimplência vs. Ativos Problemáticos.

**Mapa de Risco Geográfico:** Análise cross-section com gráfico de barras horizontais, ordenado e com escala de cor (degradê de risco) mapeando o comportamento de crédito por Unidade Federativa (UF).

**Segmentação PF x PJ:** Monitoramento histórico comparativo entre linhas de negócio (Pessoa Física e Jurídica).

**Performance por Modalidade:** Gráfico de Pareto avançado (Eixos Duplos) cruzando o Saldo Contratado (Barras com formatação inteligente R$ Bi/Tri) e o Risco Associado (Linha de Inadimplência).

**Perfil de Endividamento:** Análise de Curto vs. Longo Prazo estratificada por Faixa de Rendimento/Porte.

## ⚙️ Como Executar o Projeto Localmente
Para rodar este projeto na sua máquina, siga os passos abaixo:

**1. Pré-requisitos**
**Python 3.10+** instalado

**Docker** e **Docker Compose** instalados e rodando

**2. Extração dos Dados (Carga Inicial)**
Por segurança e boas práticas, o repositório não hospeda os bancos de dados reais. Você precisará extrair os dados do BCB rodando o script:

_Bash_
```text
python scripts/extract.py
```
(Este comando fará o download das safras de 2024 a 2026 e gerará a pasta de arquivos Parquet localmente).

**3. Execução das Transformações (dbt)**

Com os dados extraídos, construa as tabelas analíticas (.duckdb):

_Bash_
```text
cd dbt_scr
dbt deps      # Baixa os pacotes necessários
dbt build     # Executa testes e materializa as models
```
**4. Subindo a Aplicação Web**

Retorne à raiz do projeto e inicie o container Docker:

_Bash_
```text
cd ..
docker-compose up -d --build
```
Acesse o painel em seu navegador através de: http://localhost:8501

Desenvolvido com foco em escalabilidade de dados, governança e clareza analítica.
