# Quick Start - Motor de Correspondência

Guia rápido para começar em 5 minutos.

## 🚀 Início Rápido

### 1. Verificar Setup (30 segundos)

```bash
python3 verificar_setup.py
```

### 2. Configurar Variáveis de Ambiente

```bash
export MINIO_ENDPOINT="http://minio:9000"
export MINIO_ACCESS_KEY="seu_access_key"
export MINIO_SECRET_KEY="seu_secret_key"
export MINIO_BUCKET="enderecos"
```

### 3. Executar Notebooks em Ordem

No Jupyter Notebook, execute na ordem:

1. ✅ `00_configuracao_inicial.ipynb`
2. ✅ `00_carregar_dados_exemplo.ipynb`
3. ✅ `01_tratamento_inicial_ner.ipynb`
4. ✅ `02_normalizacao_camada_prata.ipynb`
5. ✅ `03_camada_ouro_deduplicacao.ipynb`
6. ✅ `04_clusterizacao.ipynb`
7. ✅ `05_motor_correspondencia.ipynb`
8. ✅ `06_validacao_geografica.ipynb`
9. ✅ `07_analise_resultados.ipynb`

## 📋 Checklist Rápido

- [ ] Variáveis de ambiente configuradas
- [ ] Arquivos CSV gerados (9.600 registros)
- [ ] SparkSession criado
- [ ] Dados carregados no MinIO
- [ ] Camadas Bronze → Silver → Gold criadas
- [ ] Motor executado
- [ ] Resultados analisados

## ⚡ Comandos Úteis

### Verificar dados carregados
```python
from pyspark.sql import SparkSession
df = spark.read.format("delta").load("s3a://enderecos/bronze/enderecos_livres")
print(f"Registros: {df.count()}")
```

### Listar tabelas Delta
```python
# Verificar tabelas criadas
import os
caminhos = [
    "s3a://enderecos/bronze/enderecos_livres",
    "s3a://enderecos/silver/enderecos_estruturados",
    "s3a://enderecos/gold/camada_ouro"
]
for caminho in caminhos:
    try:
        df = spark.read.format("delta").load(caminho)
        print(f"✓ {caminho}: {df.count()} registros")
    except:
        print(f"✗ {caminho}: não encontrado")
```

## 📚 Documentação Completa

Para guia detalhado passo a passo, consulte: **GUIA_PASSO_A_PASSO.md**

## 🆘 Problemas Comuns

**Erro de conexão MinIO:**
- Verifique variáveis de ambiente
- Teste conexão: `curl http://minio:9000`

**Erro ao ler Delta Table:**
- Verifique se dados foram carregados
- Confirme caminhos no MinIO

**Performance lenta:**
- Aumente partições: `df.repartition(200)`
- Use cache: `df.cache()`

## 📊 Resultados Esperados

- **Endereços processados:** 1.500
- **Matches encontrados:** ~1.200-1.400
- **Taxa de match:** ~80-95%
- **Score médio:** 0.75-0.85

---

**Tempo estimado total:** 30-60 minutos
