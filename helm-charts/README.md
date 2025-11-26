# Helm Charts - Plataforma de Dados Endereços

Este diretório contém os charts Helm para implantar a plataforma completa de dados no Kubernetes, incluindo MinIO, Jupyter Notebook, Spark, DeltaLake e Keycloak para autenticação.

## Estrutura

```
helm-charts/
├── Chart.yaml                    # Chart principal
├── values.yaml                   # Valores globais
├── keycloak/                     # Keycloak para autenticação
├── minio/                        # MinIO Object Storage
├── jupyter/                      # Jupyter Notebook com PySpark
├── spark/                        # Apache Spark Cluster
└── README.md                     # Este arquivo
```

## Pré-requisitos

1. **Kubernetes Cluster** (1.24+)
2. **Helm 3.x** instalado
3. **Ingress Controller** (NGINX recomendado)
4. **Cert-Manager** (opcional, para TLS automático)
5. **StorageClass** configurado no cluster

## Instalação Rápida

### 1. Adicionar Repositórios Helm

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add minio https://charts.min.io/
helm repo add jupyterhub https://hub.jupyter.org/helm-chart/
helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
helm repo update
```

### 2. Criar Namespace

```bash
kubectl create namespace enderecos-platform
```

### 3. Configurar Valores

Edite o arquivo `values.yaml` com suas configurações específicas:

```yaml
global:
  namespace: enderecos-platform
  domain: seu-dominio.com
  
keycloak:
  auth:
    adminPassword: SENHA_SEGURA_AQUI
    clientSecret: SECRET_SEGURO_AQUI

minio:
  auth:
    rootPassword: SENHA_SEGURA_AQUI
```

### 4. Instalar Chart Principal

```bash
helm install enderecos-platform . \
  --namespace enderecos-platform \
  --create-namespace \
  -f values.yaml
```

### 5. Instalação Individual dos Componentes

#### Keycloak (deve ser instalado primeiro)

```bash
helm install keycloak ./keycloak \
  --namespace enderecos-platform \
  -f keycloak/values.yaml
```

#### MinIO

```bash
helm install minio ./minio \
  --namespace enderecos-platform \
  -f minio/values.yaml
```

#### Spark

```bash
helm install spark ./spark \
  --namespace enderecos-platform \
  -f spark/values.yaml
```

#### Jupyter

```bash
helm install jupyter ./jupyter \
  --namespace enderecos-platform \
  -f jupyter/values.yaml
```

## Configuração do Keycloak

Após instalar o Keycloak, você precisa configurar:

### 1. Acessar o Console Admin

```bash
# Port-forward temporário
kubectl port-forward svc/keycloak 8080:8080 -n enderecos-platform
```

Acesse: http://localhost:8080

### 2. Criar Realm

1. Login com `admin` / `admin` (ou senha configurada)
2. Criar novo Realm: `enderecos-realm`

### 3. Criar Clients

Para cada serviço, criar um client:

#### MinIO Client
- Client ID: `minio-client`
- Client Protocol: `openid-connect`
- Access Type: `confidential`
- Valid Redirect URIs: `https://minio-console.seu-dominio.com/oauth_callback`
- Web Origins: `*`

#### Jupyter Client
- Client ID: `jupyter-client`
- Client Protocol: `openid-connect`
- Access Type: `confidential`
- Valid Redirect URIs: `https://jupyter.seu-dominio.com/*`

#### Spark Client
- Client ID: `spark-client`
- Client Protocol: `openid-connect`
- Access Type: `public`

### 4. Criar Usuários

1. Ir em Users → Add User
2. Preencher username e email
3. Na aba Credentials, definir senha
4. Desabilitar "Temporary" se necessário

## Integração com Keycloak

### MinIO

MinIO está configurado para usar OIDC com Keycloak. Após configurar o client no Keycloak:

1. Obter o Client Secret do Keycloak
2. Atualizar o secret no Kubernetes:

```bash
kubectl create secret generic minio-keycloak-secret \
  --from-literal=clientSecret=SEU_CLIENT_SECRET \
  -n enderecos-platform \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Jupyter

Jupyter usa autenticação via Ingress com Keycloak. O Ingress está configurado com annotations do NGINX para autenticação OIDC.

### Spark UI

Spark UI também usa autenticação via Ingress com Keycloak.

## Configuração de DNS

Adicione os seguintes registros DNS apontando para o IP do Ingress Controller:

```
keycloak.seu-dominio.com    → IP do Ingress
minio.seu-dominio.com       → IP do Ingress
minio-console.seu-dominio.com → IP do Ingress
jupyter.seu-dominio.com     → IP do Ingress
spark.seu-dominio.com        → IP do Ingress
```

## Verificação

### Verificar Pods

```bash
kubectl get pods -n enderecos-platform
```

Todos os pods devem estar em status `Running`.

### Verificar Serviços

```bash
kubectl get svc -n enderecos-platform
```

### Verificar Ingress

```bash
kubectl get ingress -n enderecos-platform
```

## Acessos

Após a instalação:

- **Keycloak**: https://keycloak.seu-dominio.com
- **MinIO Console**: https://minio-console.seu-dominio.com
- **Jupyter**: https://jupyter.seu-dominio.com
- **Spark UI**: https://spark.seu-dominio.com

## Troubleshooting

### Pods não iniciam

```bash
# Ver logs
kubectl logs <pod-name> -n enderecos-platform

# Descrever pod
kubectl describe pod <pod-name> -n enderecos-platform
```

### Problemas de autenticação Keycloak

1. Verificar se o realm está criado
2. Verificar se os clients estão configurados corretamente
3. Verificar secrets no Kubernetes:

```bash
kubectl get secrets -n enderecos-platform
```

### Problemas de conexão MinIO

1. Verificar se os buckets foram criados:

```bash
kubectl logs job/minio-create-buckets -n enderecos-platform
```

2. Testar conexão:

```bash
kubectl run -it --rm minio-client --image=minio/mc --restart=Never -- \
  alias set minio http://minio:9000 minioadmin minioadmin && \
  mc ls minio
```

### Problemas de Spark

1. Verificar se o master está rodando:

```bash
kubectl logs deployment/spark-master -n enderecos-platform
```

2. Verificar workers:

```bash
kubectl logs deployment/spark-worker -n enderecos-platform
```

## Atualização

Para atualizar os charts:

```bash
helm upgrade enderecos-platform . \
  --namespace enderecos-platform \
  -f values.yaml
```

## Desinstalação

```bash
helm uninstall enderecos-platform --namespace enderecos-platform
```

**ATENÇÃO**: Isso não remove os PVCs. Para remover completamente:

```bash
kubectl delete pvc --all -n enderecos-platform
kubectl delete namespace enderecos-platform
```

## Segurança

### ⚠️ IMPORTANTE - Alterar Senhas Padrão

Antes de usar em produção, altere TODAS as senhas padrão:

1. Keycloak admin password
2. MinIO root password
3. Todos os client secrets
4. PostgreSQL password (se usado)

### Usar Secrets Externos

Para produção, considere usar:
- **Sealed Secrets**
- **External Secrets Operator**
- **Vault**

### Network Policies

Adicione Network Policies para restringir comunicação entre pods:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: jupyter-network-policy
spec:
  podSelector:
    matchLabels:
      app: jupyter
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: enderecos-platform
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: minio
    ports:
    - protocol: TCP
      port: 9000
```

## Monitoramento

### Métricas

- Keycloak expõe métricas em `/metrics`
- Spark expõe métricas via Prometheus
- MinIO expõe métricas em `/minio/v2/metrics/cluster`

### Logs

Use um agregador de logs como:
- **Loki + Grafana**
- **ELK Stack**
- **Fluentd**

## Backup

### Keycloak

```bash
# Backup do PostgreSQL do Keycloak
kubectl exec -it keycloak-postgres-0 -- pg_dump -U keycloak keycloak > keycloak-backup.sql
```

### MinIO

```bash
# Backup usando mc
mc mirror minio/enderecos /backup/enderecos
```

### Jupyter Notebooks

Os notebooks são persistidos em PVCs. Faça backup do PVC:

```bash
kubectl get pvc jupyter-notebooks-pvc -n enderecos-platform -o yaml > jupyter-pvc-backup.yaml
```

## Suporte

Para problemas ou dúvidas, consulte:
- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [MinIO Documentation](https://min.io/docs)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Jupyter Documentation](https://jupyter.org/documentation)
