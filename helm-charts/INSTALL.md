# Guia de Instalação - Plataforma de Dados Endereços

Este guia fornece instruções passo a passo para instalar a plataforma completa no Kubernetes.

## Pré-requisitos

### 1. Kubernetes Cluster

- Versão mínima: 1.24+
- Pelo menos 4 nodes recomendados
- 16GB RAM e 4 CPUs por node mínimo

### 2. Ferramentas Necessárias

```bash
# Helm 3.x
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# kubectl
# Instalar conforme sua distribuição
```

### 3. Ingress Controller

```bash
# NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

### 4. Cert-Manager (Opcional, para TLS automático)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

## Instalação Passo a Passo

### Passo 1: Preparar Namespace

```bash
kubectl create namespace enderecos-platform
```

### Passo 2: Configurar StorageClass

Verifique se há um StorageClass disponível:

```bash
kubectl get storageclass
```

Se não houver, crie um (exemplo para local-path):

```bash
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: rancher.io/local-path
volumeBindingMode: WaitForFirstConsumer
EOF
```

### Passo 3: Configurar Valores

Edite `values.yaml` com suas configurações:

```bash
cp values.yaml values-production.yaml
# Edite values-production.yaml com suas configurações
```

**IMPORTANTE**: Altere todas as senhas padrão!

### Passo 4: Instalar Keycloak (Primeiro)

```bash
cd keycloak
helm install keycloak . \
  --namespace enderecos-platform \
  -f values.yaml \
  --wait

# Aguardar Keycloak estar pronto
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=keycloak \
  -n enderecos-platform --timeout=300s
cd ..
```

### Passo 5: Configurar Keycloak

#### 5.1. Port-forward para acesso temporário

```bash
kubectl port-forward svc/keycloak 8080:8080 -n enderecos-platform
```

Acesse: http://localhost:8080

#### 5.2. Login no Console Admin

- Usuário: `admin`
- Senha: (a configurada no values.yaml)

#### 5.3. Criar Realm

1. Clique em "Create Realm"
2. Nome: `enderecos-realm`
3. Enabled: ON
4. Create

#### 5.4. Criar Clients

Para cada serviço, criar um client:

**MinIO Client:**
1. Clients → Create Client
2. Client ID: `minio-client`
3. Client Protocol: `openid-connect`
4. Next → Access Type: `confidential`
5. Valid Redirect URIs: `https://minio-console.*/oauth_callback`
6. Web Origins: `*`
7. Save
8. Na aba Credentials, copiar o Secret

**Jupyter Client:**
1. Clients → Create Client
2. Client ID: `jupyter-client`
3. Client Protocol: `openid-connect`
4. Access Type: `confidential`
5. Valid Redirect URIs: `https://jupyter.*/*`
6. Save
7. Copiar Secret

**Spark Client:**
1. Clients → Create Client
2. Client ID: `spark-client`
3. Client Protocol: `openid-connect`
4. Access Type: `public`
5. Valid Redirect URIs: `https://spark.*/*`
6. Save

#### 5.5. Criar Usuários

1. Users → Add User
2. Username: `usuario-teste`
3. Email: `usuario@exemplo.com`
4. Enabled: ON
5. Save
6. Na aba Credentials:
   - Password: definir senha
   - Temporary: OFF
   - Set Password

### Passo 6: Atualizar Secrets com Client Secrets

```bash
# MinIO
kubectl create secret generic minio-keycloak-secret \
  --from-literal=clientSecret=SEU_CLIENT_SECRET_MINIO \
  -n enderecos-platform \
  --dry-run=client -o yaml | kubectl apply -f -

# Jupyter
kubectl create secret generic jupyter-keycloak-secret \
  --from-literal=clientSecret=SEU_CLIENT_SECRET_JUPYTER \
  -n enderecos-platform \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Passo 7: Instalar MinIO

```bash
cd minio
helm install minio . \
  --namespace enderecos-platform \
  -f values.yaml \
  --wait

# Verificar buckets criados
kubectl logs job/minio-create-buckets -n enderecos-platform
cd ..
```

### Passo 8: Instalar Spark

```bash
cd spark
helm install spark . \
  --namespace enderecos-platform \
  -f values.yaml \
  --wait

# Verificar status
kubectl get pods -l app.kubernetes.io/name=spark -n enderecos-platform
cd ..
```

### Passo 9: Instalar Jupyter

```bash
cd jupyter
helm install jupyter . \
  --namespace enderecos-platform \
  -f values.yaml \
  --wait
cd ..
```

### Passo 10: Configurar DNS

Adicione os seguintes registros DNS apontando para o IP do Ingress:

```bash
# Obter IP do Ingress
kubectl get ingress -n enderecos-platform

# Adicionar em /etc/hosts (para teste local) ou DNS:
# <IP> keycloak.enderecos.local
# <IP> minio.enderecos.local
# <IP> minio-console.enderecos.local
# <IP> jupyter.enderecos.local
# <IP> spark.enderecos.local
```

## Verificação

### Verificar Todos os Pods

```bash
kubectl get pods -n enderecos-platform
```

Todos devem estar `Running`.

### Verificar Serviços

```bash
kubectl get svc -n enderecos-platform
```

### Verificar Ingress

```bash
kubectl get ingress -n enderecos-platform
```

### Testar Acessos

```bash
# Keycloak
curl -k https://keycloak.enderecos.local

# MinIO API
curl -k https://minio.enderecos.local/minio/health/live

# Jupyter
curl -k https://jupyter.enderecos.local/api

# Spark UI
curl -k https://spark.enderecos.local
```

## Configuração Pós-Instalação

### 1. Configurar MinIO com Keycloak

Após instalar, configure o OIDC no MinIO:

1. Acesse MinIO Console: https://minio-console.enderecos.local
2. Login com credenciais root
3. Identity → OpenID
4. Preencher:
   - Config URL: `http://keycloak:8080/realms/enderecos-realm/.well-known/openid-configuration`
   - Client ID: `minio-client`
   - Client Secret: (o secret configurado)
   - Claim Name: `preferred_username`
5. Save

### 2. Configurar Jupyter

Os notebooks já estão configurados para usar:
- Spark Master: `spark://spark-master:7077`
- MinIO: `minio:9000`

Verifique as variáveis de ambiente no pod:

```bash
kubectl exec -it deployment/jupyter -n enderecos-platform -- env | grep -E "SPARK|MINIO"
```

## Troubleshooting

### Problemas Comuns

#### Pods não iniciam

```bash
# Ver eventos
kubectl describe pod <pod-name> -n enderecos-platform

# Ver logs
kubectl logs <pod-name> -n enderecos-platform
```

#### Keycloak não conecta ao PostgreSQL

```bash
# Verificar PostgreSQL
kubectl get pods -l app=postgresql -n enderecos-platform

# Ver logs
kubectl logs <postgresql-pod> -n enderecos-platform
```

#### MinIO não cria buckets

```bash
# Ver logs do job
kubectl logs job/minio-create-buckets -n enderecos-platform

# Executar manualmente
kubectl run -it --rm minio-client --image=minio/mc --restart=Never -n enderecos-platform -- \
  alias set minio http://minio:9000 minioadmin minioadmin && \
  mc mb minio/enderecos
```

#### Spark Workers não conectam ao Master

```bash
# Verificar master
kubectl logs deployment/spark-master -n enderecos-platform

# Verificar workers
kubectl logs deployment/spark-worker -n enderecos-platform

# Verificar DNS
kubectl run -it --rm test --image=busybox --restart=Never -- \
  nslookup spark-master
```

## Próximos Passos

1. **Configurar Backup**: Configure backups regulares dos PVCs
2. **Monitoramento**: Instale Prometheus e Grafana
3. **Logging**: Configure Loki ou ELK Stack
4. **Alertas**: Configure alertas para recursos críticos
5. **Network Policies**: Implemente políticas de rede para segurança

## Desinstalação

```bash
# Desinstalar todos os charts
helm uninstall jupyter -n enderecos-platform
helm uninstall spark -n enderecos-platform
helm uninstall minio -n enderecos-platform
helm uninstall keycloak -n enderecos-platform

# Remover PVCs (CUIDADO: apaga dados!)
kubectl delete pvc --all -n enderecos-platform

# Remover namespace
kubectl delete namespace enderecos-platform
```

## Suporte

Para problemas, consulte:
- README.md principal
- Logs dos pods
- Documentação oficial de cada componente
