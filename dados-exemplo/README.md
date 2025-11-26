# Dados de Exemplo - Motor de Correspondência de Endereços

Este diretório contém arquivos CSV de exemplo para testar todas as etapas do motor de correspondência de endereços.

## Estrutura

```
dados-exemplo/
├── bronze/
│   ├── enderecos_livres.csv          # Endereços livres de entrada (1.500 registros)
│   ├── enderecos_com_erros.csv       # Endereços com diferentes tipos de erros (1.500 registros)
│   ├── dne.csv                       # Dados do DNE (1.200 registros)
│   ├── cnefe.csv                     # Dados do CNEFE (1.200 registros)
│   ├── osm.csv                       # Dados do OpenStreetMap (1.200 registros)
│   ├── dados_geograficos.csv         # Dados geográficos para validação (1.500 registros)
│   └── variacoes_enderecos.csv       # Variações de endereços para clusterização (1.500 registros)
├── gerar_dados_massa.py              # Script gerador de dados
└── README.md                         # Este arquivo
```

## Arquivos de Dados

### 1. enderecos_livres.csv

Contém endereços livres (não estruturados) que serão processados pelo NER.

**Colunas:**
- `id`: Identificador único
- `endereco_livre`: Endereço em texto livre
- `uf`: Unidade Federativa
- `cidade`: Cidade
- `timestamp`: Data/hora de entrada

**Exemplos de variações:**
- Abreviações: "r. do ouvidor", "Av. Paulista"
- Numerais: "XV de Nov", "Quinze de Novembro"
- Formato livre: "entregar na rua do ouvidor 120 perto da praça"
- Minúsculas/maiúsculas misturadas

### 2. enderecos_com_erros.csv

Endereços com diferentes tipos de erros para testar a robustez do sistema.

**Tipos de erros incluídos:**
- `abreviacao`: Abreviações de logradouros
- `abreviacao_numeral`: Numerais romanos abreviados
- `sem_tipo_logradouro`: Falta tipo de logradouro
- `erro_fonetico`: Erros fonéticos (Souza vs Sousa)
- `minusculas`: Tudo em minúsculas
- `maiusculas`: Tudo em maiúsculas
- `numeral_por_extenso`: Numerais por extenso
- `numeral_arabico`: Numerais arábicos
- `cidade_incompleta`: Cidade abreviada
- `tipo_logradouro_ausente`: Sem tipo de logradouro
- `complemento`: Com informações de complemento
- `texto_livre`: Texto livre com instruções
- `formato_completo`: Formato completo correto
- `referencia_local`: Com referências locais ("perto da praça")

### 3. dne.csv

Dados do Diretório Nacional de Endereços (DNE) - fonte oficial brasileira.

**Colunas:**
- `id_fonte`: Identificador da fonte
- `tipo_logradouro`: Tipo (RUA, AVENIDA, etc)
- `nome_logradouro`: Nome do logradouro
- `numero`: Número do endereço
- `bairro`: Bairro
- `cidade`: Cidade
- `uf`: Unidade Federativa
- `cep`: CEP
- `latitude`: Latitude
- `longitude`: Longitude
- `confiabilidade`: Score de confiabilidade (0-1)

**Características:**
- Alta confiabilidade (0.90-0.95)
- Dados normalizados e canônicos
- Coordenadas geográficas precisas

### 4. cnefe.csv

Dados do Cadastro Nacional de Endereços para Fins Estatísticos (CNEFE) do IBGE.

**Características:**
- Muito alta confiabilidade (0.95-0.98)
- Dados estatísticos oficiais
- Coordenadas geográficas de alta precisão
- Mesma estrutura do DNE

### 5. osm.csv

Dados do OpenStreetMap - fonte colaborativa.

**Características:**
- Confiabilidade média-alta (0.75-0.85)
- Dados variados em formato
- Coordenadas geográficas
- Pode ter variações de grafia

### 6. dados_geograficos.csv

Dados geográficos para validação cruzada.

**Colunas adicionais:**
- `precisao`: ALTA, MEDIA, BAIXA
- `altitude`: Altitude em metros
- `fonte_geografica`: IBGE, GOOGLE, OSM

**Uso:**
- Validação geográfica cruzada
- Cálculo de distâncias
- Verificação de consistência entre fontes

## Cenários de Teste

### Cenário 1: Endereços Simples
- Endereços bem formatados
- Testa estruturação básica
- Arquivo: `enderecos_livres.csv` (primeiros 10 registros)

### Cenário 2: Abreviações
- Testa expansão de abreviações
- Arquivo: `enderecos_com_erros.csv` (tipo_erro = "abreviacao")

### Cenário 3: Numerais
- Testa conversão de numerais
- Arquivo: `enderecos_com_erros.csv` (tipo_erro contém "numeral")

### Cenário 4: Erros Fonéticos
- Testa correção fonética
- Arquivo: `enderecos_com_erros.csv` (tipo_erro = "erro_fonetico")

### Cenário 5: Validação Geográfica
- Testa correspondência geográfica
- Arquivos: `dne.csv`, `cnefe.csv`, `osm.csv`, `dados_geograficos.csv`

### Cenário 6: Texto Livre
- Testa NER em texto livre
- Arquivo: `enderecos_com_erros.csv` (tipo_erro = "texto_livre")

## Como Usar

### 1. Carregar no MinIO (Bronze)

```python
# Exemplo usando PySpark
df_enderecos_livres = spark.read.csv(
    "s3a://enderecos/bronze/enderecos_livres.csv",
    header=True,
    inferSchema=True
)

save_delta_table(df_enderecos_livres, PATH_ENDERECOS_LIVRES)
```

### 2. Processar com NER

```python
# Usar notebook 01_tratamento_inicial_ner.ipynb
df_estruturado = estruturar_endereco_livre(df_enderecos_livres)
```

### 3. Normalizar

```python
# Usar notebook 02_normalizacao_camada_prata.ipynb
df_normalizado = normalizar_endereco(df_estruturado)
```

### 4. Criar Camada Ouro

```python
# Carregar todas as fontes
df_dne = spark.read.csv("s3a://enderecos/bronze/dne.csv", header=True)
df_cnefe = spark.read.csv("s3a://enderecos/bronze/cnefe.csv", header=True)
df_osm = spark.read.csv("s3a://enderecos/bronze/osm.csv", header=True)

# Criar Camada Ouro
df_camada_ouro = criar_camada_ouro()
```

### 5. Executar Motor de Correspondência

```python
# Usar notebook 05_motor_correspondencia.ipynb
df_matches = executar_motor_correspondencia(df_normalizado)
```

### 6. Validar Geograficamente

```python
# Usar notebook 06_validacao_geografica.ipynb
df_validado = executar_validacao_geografica_completa(df_matches)
```

## Estatísticas dos Dados

### Endereços Livres
- Total: **1.500 registros**
- Cidades: Rio de Janeiro (RJ), São Paulo (SP), Recife (PE), Belo Horizonte (MG), Porto Alegre (RS), Brasília (DF)
- Variações: 7+ tipos diferentes de formatação (abreviado, completo, minúsculas, maiúsculas, texto livre, com referência, com complemento)

### Endereços com Erros
- Total: **1.500 registros**
- Tipos de erro: 18+ tipos diferentes
- Cobertura: Todos os tipos de erro mencionados na solução
- Distribuição uniforme entre tipos de erro

### Fontes de Referência
- DNE: **1.200 registros** (confiabilidade 0.90-0.95)
- CNEFE: **1.200 registros** (confiabilidade 0.95-0.98)
- OSM: **1.200 registros** (confiabilidade 0.75-0.85)
- Total: **3.600 registros canônicos**

### Dados Geográficos
- Total: **1.500 registros**
- Fontes: IBGE, Google, OSM (distribuição uniforme)
- Precisão: ALTA (~500), MEDIA (~500), BAIXA (~500)
- Inclui altitude (0-1000m)

### Variações de Endereços
- Total: **1.500 registros**
- Grupos: ~200 grupos de variações
- Variações por grupo: 5-15 variações
- Tipos de variação: 10 tipos diferentes

## Casos de Teste Específicos

### Teste 1: Match Exato
- Input: "Rua do Ouvidor, 120, Centro, Rio de Janeiro"
- Esperado: Match com score 1.0

### Teste 2: Match com Abreviação
- Input: "r. do ouvidor, 120, centro, rj"
- Esperado: Match com score > 0.90

### Teste 3: Match com Numeral
- Input: "rua xv de novembro 50"
- Esperado: Match com "Rua Quinze de Novembro, 50"

### Teste 4: Match com Erro Fonético
- Input: "rua souza lima 200"
- Esperado: Match com "Rua Sousa Lima, 200"

### Teste 5: Validação Geográfica
- Input: Endereço com coordenadas de múltiplas fontes
- Esperado: Score aumentado quando 3+ fontes concordam

## Gerador de Dados

Os dados foram gerados usando o script `gerar_dados_massa.py` que cria dados sintéticos realistas.

### Como Regenerar os Dados

```bash
cd dados-exemplo
python3 gerar_dados_massa.py
```

O script gera:
- Endereços livres: 1.500 registros
- Endereços com erros: 1.500 registros
- DNE: 1.200 registros
- CNEFE: 1.200 registros
- OSM: 1.200 registros
- Dados geográficos: 1.500 registros
- Variações: 1.500 registros

**Total: ~9.600 registros**

### Personalização

Você pode modificar o script `gerar_dados_massa.py` para:
- Aumentar/diminuir a quantidade de registros
- Adicionar mais cidades e logradouros
- Criar novos tipos de erros
- Ajustar distribuições de confiabilidade

## Notas

1. **Dados Sintéticos**: Estes são dados de exemplo/sintéticos para testes
2. **Coordenadas**: Coordenadas são aproximadas e podem não corresponder a endereços reais
3. **CEPs**: CEPs são exemplos e podem não ser válidos
4. **Produção**: Em produção, use dados reais das fontes oficiais
5. **Seed**: O gerador usa seed=42 para reprodutibilidade

## Extensão dos Dados

Para testes mais robustos, você pode:

1. **Aumentar volume**: Duplicar registros com pequenas variações
2. **Adicionar cidades**: Incluir mais cidades brasileiras
3. **Mais erros**: Criar mais variações de erros
4. **Dados reais**: Substituir por dados reais das fontes oficiais

## Licença

Estes dados são apenas para fins de teste e demonstração do sistema.
