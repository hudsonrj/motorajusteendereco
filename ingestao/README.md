# Notebooks de Ingestão de Dados

Este diretório contém notebooks modelo para ingestão de dados de diferentes bancos de dados para o MinIO usando DeltaLake.

## Estrutura

```
ingestao/
├── 00_exemplos_todos_bancos.ipynb    # Referência rápida com exemplos de todos os bancos
├── 01_ingestao_oracle.ipynb          # Ingestão Oracle Database
├── 02_ingestao_postgresql.ipynb      # Ingestão PostgreSQL
├── 03_ingestao_sqlserver.ipynb       # Ingestão SQL Server
├── 04_ingestao_mysql.ipynb           # Ingestão MySQL
├── 05_ingestao_mongodb.ipynb         # Ingestão MongoDB
└── README.md                          # Este arquivo
```

## Bancos de Dados Suportados

### 1. Oracle Database
- **Driver**: `oracle.jdbc.OracleDriver`
- **JDBC URL**: `jdbc:oracle:thin:@host:port/service_name`
- **Notebook**: `01_ingestao_oracle.ipynb`

### 2. PostgreSQL
- **Driver**: `org.postgresql.Driver`
- **JDBC URL**: `jdbc:postgresql://host:port/database`
- **Notebook**: `02_ingestao_postgresql.ipynb`

### 3. SQL Server
- **Driver**: `com.microsoft.sqlserver.jdbc.SQLServerDriver`
- **JDBC URL**: `jdbc:sqlserver://host:port;databaseName=database`
- **Notebook**: `03_ingestao_sqlserver.ipynb`

### 4. MySQL
- **Driver**: `com.mysql.cj.jdbc.Driver` (MySQL 8+) ou `com.mysql.jdbc.Driver` (MySQL 5.x)
- **JDBC URL**: `jdbc:mysql://host:port/database`
- **Notebook**: `04_ingestao_mysql.ipynb`

### 5. MongoDB
- **Connector**: MongoDB Spark Connector
- **URI**: `mongodb://user:password@host:port/database`
- **Notebook**: `05_ingestao_mongodb.ipynb`

## Uso

### Configuração Inicial

1. Configure as variáveis de ambiente ou edite as variáveis no notebook:
   ```python
   # Exemplo PostgreSQL
   POSTGRES_HOST = 'localhost'
   POSTGRES_PORT = '5432'
   POSTGRES_DATABASE = 'postgres'
   POSTGRES_USER = 'postgres'
   POSTGRES_PASSWORD = 'senha'
   POSTGRES_SCHEMA = 'public'
   POSTGRES_TABLE = 'tabela'
   ```

2. Execute o notebook na ordem:
   - Primeiro execute a célula de importação: `%run ../00_configuracao_inicial.ipynb`
   - Configure as variáveis de conexão
   - Execute as células de leitura
   - Execute as células de salvamento

### Exemplo Rápido

```python
# PostgreSQL
df = spark.read.format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/postgres") \
    .option("dbtable", "public.tabela") \
    .option("user", "postgres") \
    .option("password", "senha") \
    .option("driver", "org.postgresql.Driver") \
    .load()

# Adicionar metadados
df = df.withColumn("fonte", lit("POSTGRESQL")) \
       .withColumn("ingestao_em", current_timestamp())

# Salvar
save_delta_table(df, f"{PATH_BRONZE}/postgresql/tabela", mode="overwrite")
```

## Funcionalidades

Cada notebook inclui:

1. **Leitura Simples**: Leitura direta de tabela/coleção
2. **Leitura com Query**: Leitura usando query SQL/MongoDB customizada
3. **Particionamento Paralelo**: Para tabelas grandes (apenas JDBC)
4. **Ingestão Incremental**: Baseada em timestamp ou ID
5. **Metadados**: Adição automática de informações de origem e timestamp
6. **Particionamento por Data**: Organização dos dados por data de ingestão

## Drivers Necessários

### Instalação de Drivers JDBC

Os drivers podem ser adicionados de duas formas:

1. **Via Spark JARs**: Colocar o arquivo `.jar` no diretório `jars/` do Spark
2. **Via Maven**: Usar `spark.jars.packages` na configuração do Spark

#### Oracle
```bash
# Baixar ojdbc8.jar e colocar em $SPARK_HOME/jars/
# Ou usar Maven: com.oracle.database.jdbc:ojdbc8:XX.X.X
```

#### SQL Server
```bash
# Baixar mssql-jdbc-XX.X.X.jre8.jar
# Ou usar Maven: com.microsoft.sqlserver:mssql-jdbc:XX.X.X
```

#### MongoDB
```bash
# Baixar mongo-spark-connector_2.12-XX.X.X.jar
# Ou usar Maven: org.mongodb.spark:mongo-spark-connector_2.12:XX.X.X
```

## Variáveis de Ambiente

Configure as variáveis de ambiente para não expor credenciais no código:

```bash
# PostgreSQL
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DATABASE=postgres
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=senha
export POSTGRES_SCHEMA=public
export POSTGRES_TABLE=tabela

# Oracle
export ORACLE_HOST=localhost
export ORACLE_PORT=1521
export ORACLE_SERVICE_NAME=ORCL
export ORACLE_USER=usuario
export ORACLE_PASSWORD=senha
export ORACLE_SCHEMA=SCHEMA_NAME
export ORACLE_TABLE=NOME_TABELA

# SQL Server
export SQLSERVER_HOST=localhost
export SQLSERVER_PORT=1433
export SQLSERVER_DATABASE=master
export SQLSERVER_USER=sa
export SQLSERVER_PASSWORD=senha
export SQLSERVER_SCHEMA=dbo
export SQLSERVER_TABLE=nome_tabela

# MySQL
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DATABASE=mysql
export MYSQL_USER=root
export MYSQL_PASSWORD=senha
export MYSQL_TABLE=nome_tabela

# MongoDB
export MONGODB_HOST=localhost
export MONGODB_PORT=27017
export MONGODB_DATABASE=admin
export MONGODB_USER=admin
export MONGODB_PASSWORD=senha
export MONGODB_AUTH_DB=admin
export MONGODB_COLLECTION=nome_colecao
```

## Estrutura de Destino no MinIO

Os dados são salvos na seguinte estrutura:

```
s3a://enderecos/bronze/
├── oracle/
│   └── schema/
│       └── tabela/
├── postgresql/
│   └── database/
│       └── schema/
│           └── tabela/
├── sqlserver/
│   └── database/
│       └── schema/
│           └── tabela/
├── mysql/
│   └── database/
│       └── tabela/
└── mongodb/
    └── database/
        └── collection/
```

## Ingestão Incremental

Todos os notebooks incluem funções para ingestão incremental:

- **Baseada em Timestamp**: Filtra registros atualizados após uma data específica
- **Baseada em ID**: Para MongoDB, pode usar ObjectId para ordenação temporal eficiente

Exemplo:
```python
# PostgreSQL - Incremental
df_incremental = ingestao_incremental_postgresql(
    table_name="tabela",
    schema="public",
    coluna_timestamp="updated_at",
    ultima_execucao="2024-01-01 00:00:00"
)
```

## Troubleshooting

### Erro de Driver Não Encontrado
- Verifique se o driver JAR está no classpath do Spark
- Confirme o nome exato da classe do driver
- Para Spark clusters, certifique-se de que o driver está disponível em todos os nós

### Erro de Conexão
- Verifique credenciais e conectividade de rede
- Teste a conexão diretamente com o cliente do banco
- Verifique firewall e regras de segurança

### Performance Lenta
- Use particionamento paralelo para tabelas grandes
- Ajuste o número de partições conforme o tamanho dos dados
- Considere usar queries com filtros para reduzir volume

## Próximos Passos

Após a ingestão, os dados estarão disponíveis na camada Bronze e podem ser processados pelos notebooks de transformação:
- `01_tratamento_inicial_ner.ipynb`
- `02_normalizacao_camada_prata.ipynb`
- Etc.
