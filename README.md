# Motor de Correspondência de Endereços - Notebooks PySpark

Este repositório contém notebooks PySpark para implementar um motor de correspondência de alta acurácia para validação e geolocalização de endereços livres brasileiros.

## Arquitetura

O sistema segue uma arquitetura em camadas (Medallion Architecture):

- **Bronze**: Dados brutos de entrada (endereços livres, DNE, CNEFE, OSM)
- **Silver**: Dados normalizados e estruturados (Camada Prata)
- **Gold**: Dados canônicos e validados (Camada Ouro)

## Estrutura dos Notebooks

### 00_configuracao_inicial.ipynb
Configuração do ambiente Spark com DeltaLake e MinIO:
- Configuração do SparkSession
- Conexão com MinIO (S3-compatible)
- Definição de caminhos e funções auxiliares
- Configuração de particionamento

### 01_tratamento_inicial_ner.ipynb
Tratamento inicial do endereço livre usando NER (Named Entity Recognition):
- Extração de componentes: LOGRADOURO, NÚMERO, BAIRRO, COMPLEMENTO
- Identificação de tipo de logradouro
- Estruturação do endereço livre em componentes

### 02_normalizacao_camada_prata.ipynb
Normalização léxica dos endereços (Camada Prata):
- Expansão de abreviações (R. → RUA, DR → DOUTOR)
- Conversão de numerais (15 → QUINZE, II → SEGUNDO)
- Correção de problemas fonéticos e ortográficos
- Normalização de texto (maiúsculas, remoção de acentos)

### 03_camada_ouro_deduplicacao.ipynb
Criação da Camada Ouro (Golden Record):
- Unificação de múltiplas fontes (DNE, CNEFE, OSM)
- Deduplicação por hash de endereço
- Criação de registros canônicos
- Agregação de informações de múltiplas fontes
- Cálculo de score de confiança baseado no número de fontes

### 04_clusterizacao.ipynb
Clusterização de endereços similares:
- Agrupamento de variações do mesmo endereço
- Uso de algoritmos de similaridade (Jaro-Winkler)
- Criação de clusters conectados
- Atribuição de UID único por cluster

### 05_motor_correspondencia.ipynb
Motor de correspondência principal:
- **Blocking Rígido**: Filtro por UF + Cidade
- **Blocking Flexível**: Filtro fonético usando SoundexBR do bairro
- **Algoritmos de Similaridade**:
  - Jaro-Winkler: Eficaz para erros no final de palavras
  - Levenshtein: Conta número exato de typos
  - Match de número e tipo de logradouro
- Cálculo de score combinado
- Seleção do melhor match por endereço

### 06_validacao_geografica.ipynb
Validação geográfica cruzada:
- Validação usando coordenadas de múltiplas fontes
- Cálculo de distância Haversine
- Boost de confiança para matches validados geograficamente
- Classificação de nível de confiança (ALTÍSSIMA, ALTA, MÉDIA, BAIXA)

## Tecnologias Utilizadas

- **PySpark**: Processamento distribuído de dados
- **DeltaLake**: Tabelas transacionais com versionamento
- **MinIO**: Armazenamento S3-compatible
- **Algoritmos de Similaridade**: Jaro-Winkler, Levenshtein, SoundexBR

## Fluxo de Processamento

```
1. Endereço Livre (Bronze)
   ↓
2. Estruturação via NER (Silver)
   ↓
3. Normalização (Silver)
   ↓
4. Motor de Correspondência
   ├─ Blocking Rígido (UF + Cidade)
   ├─ Blocking Flexível (SoundexBR)
   └─ Algoritmos de Similaridade
   ↓
5. Validação Geográfica
   ├─ Verificação de múltiplas fontes
   └─ Cálculo de distância
   ↓
6. Match Final (Gold)
```

## Configuração

### Variáveis de Ambiente

```bash
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin
export MINIO_BUCKET=enderecos
```

### Dependências

```bash
pip install pyspark delta-spark minio boto3
```

## Estrutura de Dados no MinIO

```
s3a://enderecos/
├── bronze/
│   ├── enderecos_livres/
│   ├── dne/
│   ├── cnefe/
│   └── osm/
├── silver/
│   ├── enderecos_estruturados/
│   └── enderecos_normalizados/
└── gold/
    ├── camada_ouro/
    ├── clusters/
    └── matches/
```

## Execução

Execute os notebooks na seguinte ordem:

1. `00_configuracao_inicial.ipynb` - Configurar ambiente
2. `01_tratamento_inicial_ner.ipynb` - Estruturar endereços livres
3. `02_normalizacao_camada_prata.ipynb` - Normalizar endereços
4. `03_camada_ouro_deduplicacao.ipynb` - Criar Camada Ouro
5. `04_clusterizacao.ipynb` - Clusterizar endereços similares
6. `05_motor_correspondencia.ipynb` - Executar motor de correspondência
7. `06_validacao_geografica.ipynb` - Validar geograficamente

## Características Principais

### Alta Acurácia
- Validação cruzada de múltiplas fontes
- Validação geográfica como prova de confiança
- Algoritmos sofisticados de similaridade

### Escalabilidade
- Processamento distribuído com Spark
- Armazenamento eficiente com DeltaLake
- Particionamento por UF e Cidade

### Flexibilidade
- Tolerância a erros de digitação
- Suporte a variações de grafia
- Normalização robusta de endereços brasileiros

## Exemplo de Uso

```python
# Carregar endereços normalizados
df_enderecos = read_delta_table(PATH_ENDERECOS_NORMALIZADOS)

# Executar motor de correspondência
df_matches = executar_motor_correspondencia(df_enderecos)

# Validar geograficamente
df_validado = executar_validacao_geografica_completa(df_matches)

# Filtrar matches de alta confiança
df_alta_confianca = df_validado.filter(
    col("nivel_confianca_final").isin(["ALTISSIMA", "ALTA"])
)
```

## Notas Importantes

- Os algoritmos de similaridade implementados são versões simplificadas. Para produção, considere usar bibliotecas especializadas como `jellyfish` ou `rapidfuzz`.
- A implementação do SoundexBR é básica. Para melhor acurácia, considere usar MetaphonePT ou outras técnicas fonéticas específicas para português.
- O NER implementado é baseado em regex. Para melhor acurácia, considere usar modelos treinados (SpaCy, BERTimbau).
- A clusterização usa algoritmo simples. Para clusters mais complexos, considere usar GraphFrames.

## Documentação Adicional

- **[GUIA_PASSO_A_PASSO.md](GUIA_PASSO_A_PASSO.md)**: Guia completo passo a passo para executar todo o pipeline
- **[QUICK_START.md](QUICK_START.md)**: Guia rápido de início
- **[dados-exemplo/README.md](dados-exemplo/README.md)**: Documentação dos dados de exemplo
- **[ingestao/README.md](ingestao/README.md)**: Documentação dos notebooks de ingestão
- **[helm-charts/README.md](helm-charts/README.md)**: Documentação do deploy no Kubernetes

## Estrutura do Projeto

```
enderecos/
├── notebooks/                    # Notebooks principais
│   ├── 00_configuracao_inicial.ipynb
│   ├── 01_tratamento_inicial_ner.ipynb
│   ├── 02_normalizacao_camada_prata.ipynb
│   ├── 03_camada_ouro_deduplicacao.ipynb
│   ├── 04_clusterizacao.ipynb
│   ├── 05_motor_correspondencia.ipynb
│   ├── 06_validacao_geografica.ipynb
│   └── 07_analise_resultados.ipynb
├── ingestao/                     # Notebooks de ingestão
│   ├── 00_exemplos_todos_bancos.ipynb
│   ├── 01_ingestao_oracle.ipynb
│   ├── 02_ingestao_postgresql.ipynb
│   ├── 03_ingestao_sqlserver.ipynb
│   ├── 04_ingestao_mysql.ipynb
│   └── 05_ingestao_mongodb.ipynb
├── dados-exemplo/                # Dados de exemplo
│   ├── bronze/                  # 9.600+ registros CSV
│   └── gerar_dados_massa.py    # Gerador de dados
├── helm-charts/                 # Helm charts para Kubernetes
│   ├── keycloak/
│   ├── minio/
│   ├── jupyter/
│   └── spark/
├── GUIA_PASSO_A_PASSO.md        # Guia completo
├── QUICK_START.md               # Início rápido
└── README.md                     # Este arquivo
```

## Contribuições

Este é um projeto de referência. Sinta-se livre para adaptar e melhorar conforme suas necessidades específicas.
