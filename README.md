# Transformação de Horas (Texto → Número)

Notebook do trabalho de Pensamento Computacional / Ciência de Dados.

Alunos: 

Cristina Bisol Orso      RA: 1139000
Jorge Utermoehl          RA: 1123739

Este projeto converte respostas textuais sobre horas de trabalho/estudo e horas de lazer em valores numéricos, permitindo análise estatística e visualização.

## O que o notebook faz

- Importa e lê o arquivo Respostas.csv  
- Identifica automaticamente as colunas de horas  
- Renomeia colunas para nomes claros em português  
- Converte textos como:
  - “Menos de 20 horas” → 10
  - “20–30 horas” → 25
  - “Mais de 50 horas” → 55
- Cria duas colunas numéricas:
  - horas_trabalho_num
  - horas_lazer_num
- Gera estatísticas básicas e correlação  
- Plota um gráfico mostrando a relação entre trabalho e lazer  
- Salva a tabela final em Respostas_transformadas_ptbr.csv

## Arquivos gerados

- Respostas_transformadas_ptbr.csv – com as colunas numéricas adicionadas.

## Ferramentas usadas

- Python, Pandas, NumPy, Regex, Matplotlib
