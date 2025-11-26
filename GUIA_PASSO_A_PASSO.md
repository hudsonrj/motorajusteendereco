# Guia Passo a Passo - Motor de Correspondência de Endereços

Este guia detalha todo o processo desde o carregamento dos dados até a execução completa do motor de correspondência.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração Inicial](#configuração-inicial)
3. [Carregamento dos Dados (Camada Bronze)](#carregamento-dos-dados-camada-bronze)
4. [Tratamento Inicial com NER](#tratamento-inicial-com-ner)
5. [Normalização (Camada Prata)](#normalização-camada-prata)
6. [Criação da Camada Ouro](#criação-da-camada-ouro)
7. [Clusterização](#clusterização)
8. [Motor de Correspondência](#motor-de-correspondência)
9. [Validação Geográfica](#validação-geográfica)
10. [Verificação e Análise](#verificação-e-análise)

---

## 1. Pré-requisitos

### 1.1 Infraestrutura Necessária

- ✅ MinIO configurado e rodando
- ✅ Apache Spark configurado
- ✅ DeltaLake instalado
- ✅ Jupyter Notebook com PySpark
- ✅ Credenciais de acesso ao MinIO configuradas

### 1.2 Variáveis de Ambiente

Configure as seguintes variáveis de ambiente antes de iniciar:

```bash
export MINIO_ENDPOINT="http://minio:9000"
export MINIO_ACCESS_KEY="seu_access_key"
export MINIO_SECRET_KEY="seu_secret_key"
export MINIO_BUCKET="enderecos"
```

### 1.3 Estrutura de Diretórios no MinIO

O MinIO deve ter a seguinte estrutura de buckets/diretórios:

```
enderecos/
├── bronze/
│   ├── enderecos_livres/
│   ├── enderecos_com_erros/
│   ├── dne/
│   ├── cnefe/
│   ├── osm/
│   ├── dados_geograficos/
│   └── variacoes_enderecos/
├── silver/
│   ├── enderecos_estruturados/
│   └── enderecos_normalizados/
└── gold/
    ├── camada_ouro/
    ├── clusters/
    └── matches/
```

---

## 2. Configuração Inicial

### Passo 2.1: Abrir o Notebook de Configuração

1. Abra o Jupyter Notebook
2. Navegue até o diretório do projeto
3. Abra o notebook: `00_configuracao_inicial.ipynb`

### Passo 2.2: Verificar Configurações

Execute a primeira célula para verificar as configurações:

```python
import os

# Verificar variáveis de ambiente
print("MINIO_ENDPOINT:", os.getenv("MINIO_ENDPOINT", "Não configurado"))
print("MINIO_ACCESS_KEY:", os.getenv("MINIO_ACCESS_KEY", "Não configurado"))
print("MINIO_SECRET_KEY:", "***" if os.getenv("MINIO_SECRET_KEY") else "Não configurado")
```

**Saída esperada:**
```
MINIO_ENDPOINT: http://minio:9000
MINIO_ACCESS_KEY: seu_access_key
MINIO_SECRET_KEY: ***
```

### Passo 2.3: Executar Configuração Completa

Execute todas as células do notebook `00_configuracao_inicial.ipynb`:

1. **Célula 1**: Importações e verificações
2. **Célula 2**: Criação do SparkSession
3. **Célula 3**: Configuração do DeltaLake e MinIO
4. **Célula 4**: Definição de caminhos
5. **Célula 5**: Funções utilitárias (`save_delta_table`, `read_delta_table`)

**Verificação:**
```python
# Verificar se SparkSession foi criado
print(f"Spark Version: {spark.version}")
print(f"DeltaLake Version: {spark.sql('SELECT spark.databricks.delta.optimize.maxFileSize').show()}")

# Verificar conexão com MinIO
try:
    # Tentar listar buckets
    print("✓ Conexão com MinIO OK")
except Exception as e:
    print(f"✗ Erro na conexão: {e}")
```

---

## 3. Carregamento dos Dados (Camada Bronze)

### Passo 3.1: Abrir Notebook de Carregamento

1. Abra o notebook: `00_carregar_dados_exemplo.ipynb`
2. Este notebook carrega todos os arquivos CSV para o MinIO

### Passo 3.2: Verificar Arquivos CSV Locais

Antes de carregar, verifique se os arquivos existem:

```python
import os

PATH_DADOS_LOCAL = "./dados-exemplo/bronze"
arquivos_esperados = [
    "enderecos_livres.csv",
    "enderecos_com_erros.csv",
    "dne.csv",
    "cnefe.csv",
    "osm.csv",
    "dados_geograficos.csv",
    "variacoes_enderecos.csv"
]

print("Verificando arquivos CSV...")
for arquivo in arquivos_esperados:
    caminho = f"{PATH_DADOS_LOCAL}/{arquivo}"
    existe = os.path.exists(caminho)
    status = "✓" if existe else "✗"
    print(f"{status} {arquivo}")

if all(os.path.exists(f"{PATH_DADOS_LOCAL}/{a}") for a in arquivos_esperados):
    print("\n✓ Todos os arquivos encontrados!")
else:
    print("\n✗ Alguns arquivos estão faltando. Execute gerar_dados_massa.py primeiro.")
```

### Passo 3.3: Executar Carregamento

Execute todas as células do notebook `00_carregar_dados_exemplo.ipynb`:

**Célula 1**: Importar configurações
```python
%run ./00_configuracao_inicial.ipynb
```

**Célula 2**: Definir arquivos e função de carregamento
```python
# Já está no notebook, apenas execute
```

**Célula 3**: Carregar endereços livres
```python
df_enderecos_livres = carregar_csv_para_minio(
    "enderecos_livres",
    "enderecos_livres.csv",
    PATH_ENDERECOS_LIVRES
)
```

**Continue executando as células para cada tipo de dado:**
- Endereços com erros
- DNE
- CNEFE
- OSM
- Dados geográficos
- Variações

### Passo 3.4: Verificar Dados Carregados

Execute a célula de resumo:

```python
# Resumo de dados carregados
tabelas = [
    ("Endereços Livres", PATH_ENDERECOS_LIVRES),
    ("Endereços com Erros", f"{PATH_BRONZE}/enderecos_com_erros"),
    ("DNE", PATH_DNE),
    ("CNEFE", PATH_CNEFE),
    ("OSM", PATH_OSM),
    ("Dados Geográficos", f"{PATH_BRONZE}/dados_geograficos"),
    ("Variações", f"{PATH_BRONZE}/variacoes_enderecos")
]

for nome, caminho in tabelas:
    try:
        df = read_delta_table(caminho)
        count = df.count()
        print(f"{nome:30} {count:>10} registros")
    except Exception as e:
        print(f"{nome:30} {'ERRO':>10} - {str(e)[:50]}")
```

**Saída esperada:**
```
Endereços Livres                 1500 registros
Endereços com Erros              1500 registros
DNE                              1200 registros
CNEFE                            1200 registros
OSM                              1200 registros
Dados Geográficos                1500 registros
Variações                        1500 registros
```

### Passo 3.5: Visualizar Amostra dos Dados

```python
# Visualizar endereços livres
df_enderecos_livres = read_delta_table(PATH_ENDERECOS_LIVRES)
print("Amostra de Endereços Livres:")
df_enderecos_livres.show(10, truncate=False)

# Visualizar DNE
df_dne = read_delta_table(PATH_DNE)
print("\nAmostra de DNE:")
df_dne.show(5, truncate=False)
```

---

## 4. Tratamento Inicial com NER

### Passo 4.1: Abrir Notebook de NER

1. Abra o notebook: `01_tratamento_inicial_ner.ipynb`
2. Este notebook estrutura endereços livres usando regex

### Passo 4.2: Executar Configuração

Execute a primeira célula para importar configurações:

```python
%run ./00_configuracao_inicial.ipynb
```

### Passo 4.3: Carregar Dados de Entrada

```python
# Carregar endereços livres
df_enderecos_livres = read_delta_table(PATH_ENDERECOS_LIVRES)

print(f"Total de endereços livres: {df_enderecos_livres.count()}")
df_enderecos_livres.show(5, truncate=False)
```

### Passo 4.4: Executar Estruturação

Execute a função de estruturação:

```python
# Aplicar estruturação NER
df_estruturado = estruturar_endereco_livre(df_enderecos_livres)

# Visualizar resultado
print("Endereços Estruturados:")
df_estruturado.show(10, truncate=False)
```

**Verificar estrutura:**
```python
# Verificar schema
df_estruturado.printSchema()

# Verificar campos esperados
campos_esperados = ["id", "endereco_livre", "tipo_logradouro", "nome_logradouro", 
                    "numero", "bairro", "complemento", "uf", "cidade"]
campos_presentes = df_estruturado.columns

for campo in campos_esperados:
    status = "✓" if campo in campos_presentes else "✗"
    print(f"{status} {campo}")
```

### Passo 4.5: Salvar na Camada Silver

```python
# Salvar endereços estruturados
save_delta_table(
    df_estruturado,
    PATH_ENDERECOS_ESTRUTURADOS,
    mode="overwrite"
)

print("✓ Endereços estruturados salvos na camada Silver")
```

### Passo 4.6: Análise de Qualidade

```python
# Verificar qualidade da estruturação
from pyspark.sql.functions import col, when, count

df_qualidade = df_estruturado.select(
    count("*").alias("total"),
    count(when(col("tipo_logradouro").isNotNull(), 1)).alias("com_tipo"),
    count(when(col("nome_logradouro").isNotNull(), 1)).alias("com_nome"),
    count(when(col("numero").isNotNull(), 1)).alias("com_numero"),
    count(when(col("bairro").isNotNull(), 1)).alias("com_bairro")
)

df_qualidade.show()
```

**Saída esperada:**
```
+-----+--------+--------+----------+----------+
|total|com_tipo|com_nome|com_numero|com_bairro|
+-----+--------+--------+----------+----------+
| 1500|    1450|    1480|      1420|      1350|
+-----+--------+--------+----------+----------+
```

---

## 5. Normalização (Camada Prata)

### Passo 5.1: Abrir Notebook de Normalização

1. Abra o notebook: `02_normalizacao_camada_prata.ipynb`
2. Este notebook normaliza os endereços estruturados

### Passo 5.2: Carregar Dados Estruturados

```python
%run ./00_configuracao_inicial.ipynb

# Carregar endereços estruturados
df_estruturado = read_delta_table(PATH_ENDERECOS_ESTRUTURADOS)

print(f"Total de endereços estruturados: {df_estruturado.count()}")
```

### Passo 5.3: Executar Normalização

```python
# Aplicar normalização
df_normalizado = normalizar_endereco(df_estruturado)

# Visualizar resultado
print("Endereços Normalizados (antes vs depois):")
df_normalizado.select(
    "endereco_livre",
    "tipo_logradouro",
    "nome_logradouro_normalizado",
    "bairro_normalizado"
).show(10, truncate=False)
```

### Passo 5.4: Verificar Normalizações Aplicadas

```python
# Exemplos de normalizações
exemplos = df_normalizado.filter(
    (col("nome_logradouro") != col("nome_logradouro_normalizado")) |
    (col("tipo_logradouro") != col("tipo_logradouro_normalizado"))
).select(
    "tipo_logradouro",
    "tipo_logradouro_normalizado",
    "nome_logradouro",
    "nome_logradouro_normalizado"
).limit(20)

exemplos.show(truncate=False)
```

**Exemplos esperados:**
- "r." → "RUA"
- "Av." → "AVENIDA"
- "XV" → "QUINZE"
- "souza" → "SOUSA"

### Passo 5.5: Salvar Dados Normalizados

```python
# Salvar na camada Silver
save_delta_table(
    df_normalizado,
    PATH_ENDERECOS_NORMALIZADOS,
    mode="overwrite"
)

print("✓ Endereços normalizados salvos na camada Silver")
```

---

## 6. Criação da Camada Ouro

### Passo 6.1: Abrir Notebook da Camada Ouro

1. Abra o notebook: `03_camada_ouro_deduplicacao.ipynb`
2. Este notebook cria o "Golden Record" unificando fontes

### Passo 6.2: Carregar Todas as Fontes

```python
%run ./00_configuracao_inicial.ipynb

# Carregar todas as fontes de referência
df_dne = read_delta_table(PATH_DNE)
df_cnefe = read_delta_table(PATH_CNEFE)
df_osm = read_delta_table(PATH_OSM)

print(f"DNE: {df_dne.count()} registros")
print(f"CNEFE: {df_cnefe.count()} registros")
print(f"OSM: {df_osm.count()} registros")
```

### Passo 6.3: Normalizar Fontes de Referência

Antes de unificar, normalizar as fontes:

```python
# Normalizar DNE
df_dne_normalizado = normalizar_endereco(df_dne)

# Normalizar CNEFE
df_cnefe_normalizado = normalizar_endereco(df_cnefe)

# Normalizar OSM
df_osm_normalizado = normalizar_endereco(df_osm)
```

### Passo 6.4: Unificar Fontes

```python
# Carregar fontes com metadados
df_dne_carregado = carregar_fonte(df_dne_normalizado, "DNE")
df_cnefe_carregado = carregar_fonte(df_cnefe_normalizado, "CNEFE")
df_osm_carregado = carregar_fonte(df_osm_normalizado, "OSM")

# Unificar
df_unificado = unificar_fontes([
    df_dne_carregado,
    df_cnefe_carregado,
    df_osm_carregado
])

print(f"Total de registros unificados: {df_unificado.count()}")
```

### Passo 6.5: Deduplicar

```python
# Deduplicar por hash
df_deduplicado = deduplicar_por_hash(df_unificado)

print(f"Registros após deduplicação: {df_deduplicado.count()}")
print(f"Duplicatas removidas: {df_unificado.count() - df_deduplicado.count()}")
```

### Passo 6.6: Criar Registros Canônicos

```python
# Criar registros canônicos
df_camada_ouro = criar_registro_canonico(df_deduplicado)

# Visualizar
print("Camada Ouro - Registros Canônicos:")
df_camada_ouro.select(
    "uid",
    "tipo_logradouro",
    "nome_logradouro",
    "numero",
    "bairro",
    "cidade",
    "uf",
    "confianca_score",
    "fontes"
).show(20, truncate=False)
```

### Passo 6.7: Salvar Camada Ouro

```python
# Salvar na camada Gold
save_delta_table(
    df_camada_ouro,
    PATH_CAMADA_OURO,
    mode="overwrite"
)

print("✓ Camada Ouro criada e salva!")
```

### Passo 6.8: Estatísticas da Camada Ouro

```python
from pyspark.sql.functions import avg, min, max, count

estatisticas = df_camada_ouro.agg(
    count("*").alias("total_registros"),
    avg("confianca_score").alias("confianca_media"),
    min("confianca_score").alias("confianca_min"),
    max("confianca_score").alias("confianca_max"),
    count("fontes").alias("com_fontes")
)

estatisticas.show()
```

---

## 7. Clusterização

### Passo 7.1: Abrir Notebook de Clusterização

1. Abra o notebook: `04_clusterizacao.ipynb`
2. Este notebook agrupa variações do mesmo endereço

### Passo 7.2: Carregar Camada Ouro

```python
%run ./00_configuracao_inicial.ipynb

# Carregar Camada Ouro
df_camada_ouro = read_delta_table(PATH_CAMADA_OURO)

print(f"Registros na Camada Ouro: {df_camada_ouro.count()}")
```

### Passo 7.3: Executar Clusterização

```python
# Criar clusters
df_clusters = criar_clusters_simples(df_camada_ouro)

# Visualizar clusters
print("Clusters Criados:")
df_clusters.select(
    "cluster_id",
    "tipo_logradouro",
    "nome_logradouro",
    "numero",
    "bairro",
    "cidade",
    "uf"
).orderBy("cluster_id").show(30, truncate=False)
```

### Passo 7.4: Analisar Clusters

```python
# Estatísticas de clusters
from pyspark.sql.functions import count

estatisticas_clusters = df_clusters.groupBy("cluster_id").agg(
    count("*").alias("tamanho_cluster")
).agg(
    count("*").alias("total_clusters"),
    avg("tamanho_cluster").alias("tamanho_medio"),
    min("tamanho_cluster").alias("tamanho_min"),
    max("tamanho_cluster").alias("tamanho_max")
)

estatisticas_clusters.show()
```

### Passo 7.5: Salvar Clusters

```python
# Salvar clusters
save_delta_table(
    df_clusters,
    PATH_CLUSTERS,
    mode="overwrite"
)

print("✓ Clusters salvos!")
```

---

## 8. Motor de Correspondência

### Passo 8.1: Abrir Notebook do Motor

1. Abra o notebook: `05_motor_correspondencia.ipynb`
2. Este notebook encontra matches entre endereços de entrada e Camada Ouro

### Passo 8.2: Carregar Dados

```python
%run ./00_configuracao_inicial.ipynb

# Carregar endereços normalizados (entrada)
df_entrada = read_delta_table(PATH_ENDERECOS_NORMALIZADOS)

# Carregar Camada Ouro
df_camada_ouro = read_delta_table(PATH_CAMADA_OURO)

print(f"Endereços de entrada: {df_entrada.count()}")
print(f"Registros na Camada Ouro: {df_camada_ouro.count()}")
```

### Passo 8.3: Aplicar Blocking Rígido

```python
# Blocking por UF + Cidade
df_candidatos_rigido = aplicar_blocking_rigido(df_entrada, df_camada_ouro)

print(f"Candidatos após blocking rígido: {df_candidatos_rigido.count()}")
df_candidatos_rigido.show(10, truncate=False)
```

### Passo 8.4: Aplicar Blocking Flexível

```python
# Blocking por SoundexBR
df_candidatos_flexivel = aplicar_blocking_flexivel(df_entrada, df_camada_ouro)

print(f"Candidatos após blocking flexível: {df_candidatos_flexivel.count()}")
```

### Passo 8.5: Calcular Similaridades

```python
# Calcular scores de similaridade
df_matches = calcular_scores_similaridade(df_candidatos_rigido)

# Visualizar matches
print("Top 20 Matches:")
df_matches.select(
    "id_entrada",
    "endereco_livre",
    "uid_ouro",
    "nome_logradouro_ouro",
    "score_jaro_winkler",
    "score_levenshtein",
    "score_final"
).orderBy(col("score_final").desc()).show(20, truncate=False)
```

### Passo 8.6: Filtrar Matches por Threshold

```python
# Filtrar matches com score mínimo
THRESHOLD = 0.7

df_matches_filtrados = df_matches.filter(col("score_final") >= THRESHOLD)

print(f"Matches acima do threshold ({THRESHOLD}): {df_matches_filtrados.count()}")
```

### Passo 8.7: Executar Motor Completo

```python
# Executar motor completo
df_resultado = executar_motor_correspondencia(
    df_entrada,
    df_camada_ouro,
    threshold=0.7
)

print(f"Total de matches encontrados: {df_resultado.count()}")
```

### Passo 8.8: Salvar Resultados

```python
# Salvar matches
save_delta_table(
    df_resultado,
    PATH_MATCHES,
    mode="overwrite"
)

print("✓ Matches salvos!")
```

---

## 9. Validação Geográfica

### Passo 9.1: Abrir Notebook de Validação

1. Abra o notebook: `06_validacao_geografica.ipynb`
2. Este notebook valida matches usando coordenadas geográficas

### Passo 9.2: Carregar Dados

```python
%run ./00_configuracao_inicial.ipynb

# Carregar matches
df_matches = read_delta_table(PATH_MATCHES)

# Carregar dados geográficos
df_geograficos = read_delta_table(f"{PATH_BRONZE}/dados_geograficos")

# Carregar Camada Ouro (com coordenadas)
df_camada_ouro = read_delta_table(PATH_CAMADA_OURO)

print(f"Matches para validar: {df_matches.count()}")
```

### Passo 9.3: Validar Correspondência Geográfica

```python
# Validar correspondência geográfica
df_validado = validar_correspondencia_geografica(
    df_matches,
    df_camada_ouro,
    df_geograficos
)

print("Matches Validados:")
df_validado.select(
    "id_entrada",
    "uid_ouro",
    "score_final",
    "distancia_metros",
    "validacao_geografica",
    "score_final_validado"
).orderBy(col("score_final_validado").desc()).show(20, truncate=False)
```

### Passo 9.4: Executar Validação Completa

```python
# Executar validação completa
df_resultado_final = executar_validacao_geografica_completa(
    df_matches,
    df_camada_ouro,
    df_geograficos
)

print(f"Matches validados: {df_resultado_final.count()}")
```

### Passo 9.5: Análise de Validação

```python
# Estatísticas de validação
from pyspark.sql.functions import count, when, avg

estatisticas_validacao = df_resultado_final.agg(
    count("*").alias("total_matches"),
    count(when(col("validacao_geografica") == "ALTA", 1)).alias("validacao_alta"),
    count(when(col("validacao_geografica") == "MEDIA", 1)).alias("validacao_media"),
    count(when(col("validacao_geografica") == "BAIXA", 1)).alias("validacao_baixa"),
    avg("distancia_metros").alias("distancia_media_metros"),
    avg("score_final_validado").alias("score_medio_final")
)

estatisticas_validacao.show()
```

### Passo 9.6: Salvar Resultados Finais

```python
# Salvar resultados finais
save_delta_table(
    df_resultado_final,
    f"{PATH_GOLD}/matches_validados",
    mode="overwrite"
)

print("✓ Validação geográfica concluída e resultados salvos!")
```

---

## 10. Verificação e Análise

### Passo 10.1: Criar Notebook de Análise

Crie um novo notebook `07_analise_resultados.ipynb` para análise final:

```python
%run ./00_configuracao_inicial.ipynb

# Carregar resultados finais
df_resultado_final = read_delta_table(f"{PATH_GOLD}/matches_validados")

print("="*60)
print("ANÁLISE FINAL - MOTOR DE CORRESPONDÊNCIA")
print("="*60)
```

### Passo 10.2: Estatísticas Gerais

```python
from pyspark.sql.functions import *

# Estatísticas gerais
estatisticas_gerais = df_resultado_final.agg(
    count("*").alias("total_matches"),
    count(when(col("score_final_validado") >= 0.9, 1)).alias("matches_alta_confianca"),
    count(when(col("score_final_validado") >= 0.7, 1)).alias("matches_media_confianca"),
    count(when(col("score_final_validado") < 0.7, 1)).alias("matches_baixa_confianca"),
    avg("score_final_validado").alias("score_medio"),
    min("score_final_validado").alias("score_minimo"),
    max("score_final_validado").alias("score_maximo")
)

estatisticas_gerais.show()
```

### Passo 10.3: Análise por Cidade

```python
# Análise por cidade
analise_cidade = df_resultado_final.groupBy("cidade_entrada", "uf_entrada").agg(
    count("*").alias("total_matches"),
    avg("score_final_validado").alias("score_medio"),
    count(when(col("score_final_validado") >= 0.9, 1)).alias("alta_confianca")
).orderBy(col("total_matches").desc())

analise_cidade.show()
```

### Passo 10.4: Top Matches

```python
# Top 50 matches com maior score
top_matches = df_resultado_final.select(
    "id_entrada",
    "endereco_livre",
    "nome_logradouro_ouro",
    "numero_ouro",
    "bairro_ouro",
    "cidade_ouro",
    "score_final_validado",
    "distancia_metros",
    "validacao_geografica"
).orderBy(col("score_final_validado").desc()).limit(50)

top_matches.show(50, truncate=False)
```

### Passo 10.5: Casos sem Match

```python
# Carregar endereços de entrada
df_entrada = read_delta_table(PATH_ENDERECOS_NORMALIZADOS)

# Encontrar endereços sem match
ids_com_match = df_resultado_final.select("id_entrada").distinct()
df_sem_match = df_entrada.join(
    ids_com_match,
    df_entrada.id == ids_com_match.id_entrada,
    "left_anti"
)

print(f"Endereços sem match: {df_sem_match.count()}")
print("\nExemplos de endereços sem match:")
df_sem_match.select("id", "endereco_livre", "cidade", "uf").show(20, truncate=False)
```

### Passo 10.6: Exportar Resultados

```python
# Exportar resultados para CSV (opcional)
df_resultado_final.coalesce(1).write.mode("overwrite").option("header", "true").csv(
    "s3a://enderecos/resultados/matches_finais"
)

print("✓ Resultados exportados!")
```

---

## 🔍 Troubleshooting

### Problema: Erro ao conectar com MinIO

**Solução:**
```python
# Verificar variáveis de ambiente
import os
print(os.getenv("MINIO_ENDPOINT"))
print(os.getenv("MINIO_ACCESS_KEY"))

# Verificar configuração do Spark
spark.conf.get("spark.hadoop.fs.s3a.endpoint")
spark.conf.get("spark.hadoop.fs.s3a.access.key")
```

### Problema: Erro ao ler Delta Table

**Solução:**
```python
# Verificar se a tabela existe
try:
    df = spark.read.format("delta").load(PATH_ENDERECOS_LIVRES)
    print(f"✓ Tabela existe: {df.count()} registros")
except Exception as e:
    print(f"✗ Erro: {e}")
    print("Verifique se os dados foram carregados corretamente.")
```

### Problema: Performance lenta

**Soluções:**
1. Aumentar número de partições:
```python
df = df.repartition(200)
```

2. Cachear DataFrames frequentemente usados:
```python
df_camada_ouro.cache()
```

3. Usar broadcast join para tabelas pequenas:
```python
from pyspark.sql.functions import broadcast
df_resultado = df_entrada.join(broadcast(df_camada_ouro), ...)
```

---

## 📊 Checklist de Execução

Use este checklist para garantir que todos os passos foram executados:

- [ ] Configuração inicial concluída
- [ ] Dados CSV carregados para MinIO (Bronze)
- [ ] Endereços estruturados (Silver)
- [ ] Endereços normalizados (Silver)
- [ ] Camada Ouro criada (Gold)
- [ ] Clusters criados
- [ ] Motor de correspondência executado
- [ ] Validação geográfica concluída
- [ ] Análise de resultados realizada
- [ ] Resultados exportados

---

## 📝 Notas Finais

1. **Ordem de Execução**: Execute os notebooks na ordem numérica (00 → 01 → 02 → ...)
2. **Dependências**: Cada notebook depende dos anteriores
3. **Modo Overwrite**: Os notebooks usam `mode="overwrite"` - cuidado em produção
4. **Performance**: Para grandes volumes, considere particionar por cidade/UF
5. **Monitoramento**: Acompanhe logs do Spark para identificar gargalos

---

## 🚀 Próximos Passos

1. **Otimização**: Ajustar thresholds e parâmetros de similaridade
2. **Validação**: Comparar resultados com dados conhecidos
3. **Produção**: Adaptar para processamento incremental
4. **API**: Criar API REST para consultas em tempo real
5. **Monitoramento**: Implementar métricas e alertas

---

**Fim do Guia Passo a Passo**

Para dúvidas ou problemas, consulte os notebooks individuais ou a documentação do projeto.
