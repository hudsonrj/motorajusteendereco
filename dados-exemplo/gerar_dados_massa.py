#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar dados de exemplo em massa para testes do motor de correspondência.
Gera pelo menos 1000 registros para cada tipo de dado.
"""

import csv
import random
from datetime import datetime, timedelta
from typing import List, Tuple

# Seed para reprodutibilidade
random.seed(42)

# Dados base para geração
TIPOS_LOGRADOURO = ["RUA", "AVENIDA", "ESTRADA", "TRAVESSA", "ALAMEDA", "PRAÇA", "VIELA", "LARGO"]
ABREVIACOES = {
    "RUA": ["R.", "R", "Rua", "rua", "RUA"],
    "AVENIDA": ["Av.", "Av", "Avenida", "avenida", "AVENIDA", "Av", "av"],
    "ESTRADA": ["Est.", "Est", "Estrada", "estrada"],
    "TRAVESSA": ["Tv.", "Tv", "Travessa", "travessa"],
    "ALAMEDA": ["Al.", "Al", "Alameda", "alameda"],
    "PRAÇA": ["Pç.", "Pç", "Praça", "praça"],
}

LOGRADOUROS_BRASIL = [
    # Rio de Janeiro
    ("DO OUVIDOR", "CENTRO", "Rio de Janeiro", "RJ", -22.902778, -43.172778),
    ("DAS FLORES", "JARDIM", "Rio de Janeiro", "RJ", -22.910000, -43.180000),
    ("ATLANTICA", "COPACABANA", "Rio de Janeiro", "RJ", -22.971389, -43.182222),
    ("OSWALDO CRUZ", "BOTAFOGO", "Rio de Janeiro", "RJ", -22.950000, -43.190000),
    ("COPACABANA", "COPACABANA", "Rio de Janeiro", "RJ", -22.970000, -43.185000),
    ("RIO BRANCO", "CENTRO", "Rio de Janeiro", "RJ", -22.904000, -43.175000),
    ("PRESIDENTE VARGAS", "CENTRO", "Rio de Janeiro", "RJ", -22.906000, -43.178000),
    ("PRIMEIRO DE MARÇO", "CENTRO", "Rio de Janeiro", "RJ", -22.903000, -43.176000),
    ("URUGUAIANA", "CENTRO", "Rio de Janeiro", "RJ", -22.901000, -43.174000),
    ("SETEMBRO", "CENTRO", "Rio de Janeiro", "RJ", -22.905000, -43.177000),
    
    # São Paulo
    ("PAULISTA", "BELA VISTA", "São Paulo", "SP", -23.561399, -46.656499),
    ("QUINZE DE NOVEMBRO", "CENTRO", "São Paulo", "SP", -23.550520, -46.633308),
    ("REBOUCAS", "PINHEIROS", "São Paulo", "SP", -23.561000, -46.680000),
    ("CONSOLACAO", "CONSOLACAO", "São Paulo", "SP", -23.550000, -46.660000),
    ("BRIGADEIRO FARIA LIMA", "ITAM BIBI", "São Paulo", "SP", -23.584000, -46.690000),
    ("IPIRANGA", "REPUBLICA", "São Paulo", "SP", -23.543000, -46.640000),
    ("NOVE DE JULHO", "REPUBLICA", "São Paulo", "SP", -23.544000, -46.641000),
    ("VINTE E TRES DE MAIO", "LIBERDADE", "São Paulo", "SP", -23.545000, -46.642000),
    ("SAO JOAO", "REPUBLICA", "São Paulo", "SP", -23.546000, -46.643000),
    ("MARQUES DE ITU", "VILA BUARQUE", "São Paulo", "SP", -23.547000, -46.644000),
    
    # Recife
    ("BOA VIAGEM", "BOA VIAGEM", "Recife", "PE", -8.119000, -34.906000),
    ("BOAVISTA", "BOA VIAGEM", "Recife", "PE", -8.120000, -34.907000),
    ("DA AURORA", "BOA VISTA", "Recife", "PE", -8.063000, -34.881000),
    ("CONDE DA BOA VISTA", "DERBY", "Recife", "PE", -8.055000, -34.888000),
    ("DO COMERCIO", "SAO JOSE", "Recife", "PE", -8.060000, -34.875000),
    ("AGAMENON MAGALHAES", "DERBY", "Recife", "PE", -8.050000, -34.890000),
    
    # Belo Horizonte
    ("AFONSO PENA", "CENTRO", "Belo Horizonte", "MG", -19.916667, -43.934444),
    ("AMAZONAS", "CENTRO", "Belo Horizonte", "MG", -19.917000, -43.935000),
    ("BAHIA", "CENTRO", "Belo Horizonte", "MG", -19.918000, -43.936000),
    ("TUPIS", "CENTRO", "Belo Horizonte", "MG", -19.919000, -43.937000),
    
    # Porto Alegre
    ("DOS ANDRADAS", "CENTRO", "Porto Alegre", "RS", -30.034722, -51.230556),
    ("BORGES DE MEDEIROS", "CENTRO", "Porto Alegre", "RS", -30.035000, -51.231000),
    ("PROTASIO ALVES", "PETROPOLIS", "Porto Alegre", "RS", -30.036000, -51.232000),
    
    # Brasília
    ("W3 SUL", "ASA SUL", "Brasília", "DF", -15.794167, -47.882222),
    ("W3 NORTE", "ASA NORTE", "Brasília", "DF", -15.795000, -47.883000),
    ("EIXO MONUMENTAL", "ASA NORTE", "Brasília", "DF", -15.796000, -47.884000),
]

NUMEROS_EXTENSO = {
    1: "UM", 2: "DOIS", 3: "TRES", 4: "QUATRO", 5: "CINCO",
    6: "SEIS", 7: "SETE", 8: "OITO", 9: "NOVE", 10: "DEZ",
    11: "ONZE", 12: "DOZE", 13: "TREZE", 14: "QUATORZE", 15: "QUINZE",
    20: "VINTE", 25: "VINTE E CINCO", 30: "TRINTA"
}

NUMEROS_ROMANOS = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
    6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X",
    11: "XI", 12: "XII", 13: "XIII", 14: "XIV", 15: "XV",
    20: "XX", 25: "XXV", 30: "XXX"
}

COMPLEMENTOS = ["", "apto 101", "apto 201", "apto 301", "sala 10", "sala 20", "loja 1", "loja 2", "bloco A", "bloco B"]
REFERENCIAS_LOCAIS = ["", "perto da praça", "próximo ao mercado", "em frente ao banco", "ao lado da escola", "perto do metrô"]

def gerar_cep(uf: str) -> str:
    """Gera um CEP válido para a UF"""
    ceps = {
        "RJ": "20000-000",
        "SP": "01000-000",
        "PE": "50000-000",
        "MG": "30000-000",
        "RS": "90000-000",
        "DF": "70000-000"
    }
    base = ceps.get(uf, "00000-000")
    num = random.randint(100, 999)
    return f"{base[:5]}-{num:03d}"

def gerar_timestamp(base_dias: int = 30) -> str:
    """Gera timestamp aleatório"""
    dias_antes = random.randint(0, base_dias)
    horas = random.randint(0, 23)
    minutos = random.randint(0, 59)
    data = datetime.now() - timedelta(days=dias_antes, hours=horas, minutes=minutos)
    return data.strftime("%Y-%m-%d %H:%M:%S")

def gerar_enderecos_livres(n: int = 1000) -> List[dict]:
    """Gera endereços livres com variações"""
    enderecos = []
    
    for i in range(1, n + 1):
        logradouro_info = random.choice(LOGRADOUROS_BRASIL)
        nome_log, bairro, cidade, uf, lat, lon = logradouro_info
        
        tipo_log = random.choice(TIPOS_LOGRADOURO)
        numero = random.randint(1, 5000)
        
        # Variações de formatação
        formato = random.choice([
            "abreviado", "completo", "minusculas", "maiusculas", 
            "texto_livre", "com_referencia", "com_complemento"
        ])
        
        if formato == "abreviado":
            abreviacao = random.choice(ABREVIACOES.get(tipo_log, [tipo_log]))
            endereco = f"{abreviacao} {nome_log.lower()}, {numero}"
        elif formato == "completo":
            endereco = f"{tipo_log} {nome_log}, {numero}, {bairro}, {cidade}"
        elif formato == "minusculas":
            endereco = f"{tipo_log.lower()} {nome_log.lower()}, {numero}, {bairro.lower()}"
        elif formato == "maiusculas":
            endereco = f"{tipo_log} {nome_log}, {numero}, {bairro}"
        elif formato == "texto_livre":
            ref = random.choice(REFERENCIAS_LOCAIS)
            endereco = f"entregar na {tipo_log.lower()} {nome_log.lower()}, {numero} {ref}, {bairro.lower()}"
        elif formato == "com_referencia":
            ref = random.choice(REFERENCIAS_LOCAIS)
            endereco = f"{tipo_log} {nome_log}, {numero}, {ref}, {bairro}, {cidade}"
        else:  # com_complemento
            comp = random.choice(COMPLEMENTOS)
            endereco = f"{tipo_log} {nome_log}, {numero}, {comp}, {bairro}, {cidade}"
        
        enderecos.append({
            "id": i,
            "endereco_livre": endereco,
            "uf": uf,
            "cidade": cidade,
            "timestamp": gerar_timestamp()
        })
    
    return enderecos

def gerar_enderecos_com_erros(n: int = 1000) -> List[dict]:
    """Gera endereços com diferentes tipos de erros"""
    tipos_erro = [
        "abreviacao", "abreviacao_numeral", "sem_tipo_logradouro",
        "erro_fonetico", "minusculas", "maiusculas", "numeral_por_extenso",
        "numeral_arabico", "cidade_incompleta", "tipo_logradouro_ausente",
        "complemento", "texto_livre", "formato_completo", "referencia_local",
        "bairro_ausente", "uf_ausente", "numero_ausente", "formato_sequencial"
    ]
    
    erros_foneticos = {
        "SOUSA": "SOUZA",
        "SOUZA": "SOUSA",
        "CONSOLACAO": "CONSOLAÇÃO",
        "CONSOLAÇÃO": "CONSOLACAO",
        "ATLANTICA": "ATLÂNTICA",
        "ATLÂNTICA": "ATLANTICA"
    }
    
    enderecos = []
    
    for i in range(1, n + 1):
        logradouro_info = random.choice(LOGRADOUROS_BRASIL)
        nome_log, bairro, cidade, uf, lat, lon = logradouro_info
        tipo_log = random.choice(TIPOS_LOGRADOURO)
        numero = random.randint(1, 5000)
        tipo_erro = random.choice(tipos_erro)
        
        if tipo_erro == "abreviacao":
            abreviacao = random.choice(ABREVIACOES.get(tipo_log, [tipo_log]))
            endereco = f"{abreviacao} {nome_log.lower()}, {numero}"
        elif tipo_erro == "abreviacao_numeral":
            abreviacao = random.choice(ABREVIACOES.get(tipo_log, [tipo_log]))
            endereco = f"{abreviacao} xv de novembro, {numero}"
        elif tipo_erro == "sem_tipo_logradouro":
            endereco = f"{nome_log.lower()}, {numero}, {bairro.lower()}"
        elif tipo_erro == "erro_fonetico":
            nome_errado = erros_foneticos.get(nome_log, nome_log)
            endereco = f"{tipo_log.lower()} {nome_errado.lower()}, {numero}"
        elif tipo_erro == "minusculas":
            endereco = f"{tipo_log.lower()} {nome_log.lower()}, {numero}, {bairro.lower()}, {cidade.lower()}"
        elif tipo_erro == "maiusculas":
            endereco = f"{tipo_log} {nome_log}, {numero}, {bairro}, {cidade}"
        elif tipo_erro == "numeral_por_extenso":
            num_extenso = NUMEROS_EXTENSO.get(numero, str(numero))
            endereco = f"{tipo_log.lower()} {nome_log.lower()}, {num_extenso.lower()}"
        elif tipo_erro == "numeral_arabico":
            endereco = f"{tipo_log.lower()} {numero} de novembro, {numero}"
        elif tipo_erro == "cidade_incompleta":
            cidade_abrev = cidade.split()[0] if " " in cidade else cidade[:5]
            endereco = f"{tipo_log.lower()} {nome_log.lower()}, {numero}, {bairro.lower()}, {cidade_abrev.lower()}"
        elif tipo_erro == "tipo_logradouro_ausente":
            endereco = f"{nome_log.lower()}, {numero}, {bairro.lower()}"
        elif tipo_erro == "complemento":
            comp = random.choice(COMPLEMENTOS)
            endereco = f"{tipo_log.lower()} {nome_log.lower()}, {numero}, {comp}, {bairro.lower()}"
        elif tipo_erro == "texto_livre":
            ref = random.choice(REFERENCIAS_LOCAIS)
            endereco = f"entregar na {tipo_log.lower()} {nome_log.lower()}, {numero} {ref}, {bairro.lower()}"
        elif tipo_erro == "formato_completo":
            endereco = f"{tipo_log} {nome_log}, {numero}, {bairro}, {cidade} - {uf}"
        elif tipo_erro == "referencia_local":
            ref = random.choice(REFERENCIAS_LOCAIS)
            endereco = f"{tipo_log.lower()} {nome_log.lower()}, {numero}, {ref}, {bairro.lower()}"
        elif tipo_erro == "bairro_ausente":
            endereco = f"{tipo_log.lower()} {nome_log.lower()}, {numero}, {cidade.lower()}"
        elif tipo_erro == "uf_ausente":
            endereco = f"{tipo_log.lower()} {nome_log.lower()}, {numero}, {bairro.lower()}, {cidade.lower()}"
        elif tipo_erro == "numero_ausente":
            endereco = f"{tipo_log.lower()} {nome_log.lower()}, {bairro.lower()}, {cidade.lower()}"
        else:  # formato_sequencial
            endereco = f"{tipo_log.lower()} {nome_log.lower()} {numero} {bairro.lower()} {cidade.lower()} {uf.lower()}"
        
        enderecos.append({
            "id": f"ERR{i:06d}",
            "endereco_livre": endereco,
            "uf": uf if tipo_erro != "uf_ausente" else "",
            "cidade": cidade if tipo_erro != "cidade_incompleta" else cidade.split()[0],
            "timestamp": gerar_timestamp(),
            "tipo_erro": tipo_erro
        })
    
    return enderecos

def gerar_fonte_referencia(n: int = 1000, fonte: str = "DNE") -> List[dict]:
    """Gera dados de fonte de referência (DNE, CNEFE, OSM)"""
    confiabilidades = {
        "DNE": (0.90, 0.95),
        "CNEFE": (0.95, 0.98),
        "OSM": (0.75, 0.85)
    }
    
    conf_min, conf_max = confiabilidades.get(fonte, (0.80, 0.90))
    
    registros = []
    
    for i in range(1, n + 1):
        logradouro_info = random.choice(LOGRADOUROS_BRASIL)
        nome_log, bairro, cidade, uf, lat, lon = logradouro_info
        
        # Adicionar pequena variação nas coordenadas
        lat_var = lat + random.uniform(-0.001, 0.001)
        lon_var = lon + random.uniform(-0.001, 0.001)
        
        tipo_log = random.choice(TIPOS_LOGRADOURO)
        numero = random.randint(1, 5000)
        confiabilidade = round(random.uniform(conf_min, conf_max), 2)
        
        # Variação de formato para OSM
        if fonte == "OSM":
            nome_log = nome_log.title() if random.random() > 0.5 else nome_log
            bairro = bairro.title() if random.random() > 0.5 else bairro
        
        registros.append({
            "id_fonte": f"{fonte}{i:06d}",
            "tipo_logradouro": tipo_log,
            "nome_logradouro": nome_log,
            "numero": numero,
            "bairro": bairro,
            "cidade": cidade,
            "uf": uf,
            "cep": gerar_cep(uf),
            "latitude": round(lat_var, 6),
            "longitude": round(lon_var, 6),
            "confiabilidade": confiabilidade
        })
    
    return registros

def gerar_dados_geograficos(n: int = 1000) -> List[dict]:
    """Gera dados geográficos para validação"""
    fontes = ["IBGE", "GOOGLE", "OSM"]
    precisoes = ["ALTA", "MEDIA", "BAIXA"]
    
    registros = []
    
    for i in range(1, n + 1):
        logradouro_info = random.choice(LOGRADOUROS_BRASIL)
        nome_log, bairro, cidade, uf, lat, lon = logradouro_info
        
        tipo_log = random.choice(TIPOS_LOGRADOURO)
        numero = random.randint(1, 5000)
        fonte = random.choice(fontes)
        precisao = random.choice(precisoes)
        
        # Variação de coordenadas baseada na precisão
        if precisao == "ALTA":
            lat_var = lat + random.uniform(-0.0001, 0.0001)
            lon_var = lon + random.uniform(-0.0001, 0.0001)
        elif precisao == "MEDIA":
            lat_var = lat + random.uniform(-0.001, 0.001)
            lon_var = lon + random.uniform(-0.001, 0.001)
        else:  # BAIXA
            lat_var = lat + random.uniform(-0.01, 0.01)
            lon_var = lon + random.uniform(-0.01, 0.01)
        
        altitude = random.randint(0, 1000)
        
        registros.append({
            "id": f"GEO{i:06d}",
            "tipo_logradouro": tipo_log,
            "nome_logradouro": nome_log,
            "numero": numero,
            "bairro": bairro,
            "cidade": cidade,
            "uf": uf,
            "latitude": round(lat_var, 6),
            "longitude": round(lon_var, 6),
            "precisao": precisao,
            "altitude": altitude,
            "fonte_geografica": fonte
        })
    
    return registros

def gerar_variacoes_enderecos(n: int = 1000) -> List[dict]:
    """Gera variações de endereços para clusterização"""
    registros = []
    uid_counter = 1
    
    # Criar grupos de variações - usar todos os logradouros e criar múltiplos grupos
    grupos = {}
    num_grupos = min(200, len(LOGRADOUROS_BRASIL) * 10)  # Criar até 200 grupos
    
    for i in range(num_grupos):
        log_info = random.choice(LOGRADOUROS_BRASIL)
        nome_log, bairro, cidade, uf, lat, lon = log_info
        uid = f"UID_{nome_log.replace(' ', '_').replace('-', '_')}_{uid_counter:04d}"
        # Cada grupo terá 5-15 variações
        grupos[uid] = (log_info, random.randint(5, 15))
        uid_counter += 1
    
    var_id = 1
    tipos_variacao = [
        "abreviacao", "completo", "minusculas", "maiusculas",
        "numeral_romano", "numeral_extenso", "sem_pontuacao",
        "com_complemento", "com_referencia", "formato_sequencial"
    ]
    
    for uid, (log_info, num_variacoes) in grupos.items():
        nome_log, bairro, cidade, uf, lat, lon = log_info
        tipo_log = random.choice(TIPOS_LOGRADOURO)
        numero = random.randint(1, 5000)
        
        for v in range(num_variacoes):
            variacao_tipo = random.choice(tipos_variacao)
            
            if variacao_tipo == "abreviacao":
                abreviacao = random.choice(ABREVIACOES.get(tipo_log, [tipo_log]))
                variacao = f"{abreviacao} {nome_log.lower()}, {numero}"
                descricao = "Abreviação com ponto"
            elif variacao_tipo == "completo":
                variacao = f"{tipo_log} {nome_log}, {numero}, {bairro}"
                descricao = "Formato completo"
            elif variacao_tipo == "minusculas":
                variacao = f"{tipo_log.lower()} {nome_log.lower()}, {numero}"
                descricao = "Minúsculas"
            elif variacao_tipo == "maiusculas":
                variacao = f"{tipo_log} {nome_log}, {numero}"
                descricao = "Maiúsculas"
            elif variacao_tipo == "numeral_romano":
                num_romano = NUMEROS_ROMANOS.get(numero, str(numero))
                variacao = f"{tipo_log.lower()} {nome_log.lower()}, {num_romano}"
                descricao = "Numeral romano"
            elif variacao_tipo == "numeral_extenso":
                num_extenso = NUMEROS_EXTENSO.get(numero, str(numero))
                variacao = f"{tipo_log.lower()} {nome_log.lower()}, {num_extenso.lower()}"
                descricao = "Numeral por extenso"
            elif variacao_tipo == "sem_pontuacao":
                variacao = f"{tipo_log.lower()} {nome_log.lower()} {numero} {bairro.lower()}"
                descricao = "Sem pontuação"
            elif variacao_tipo == "com_complemento":
                comp = random.choice(COMPLEMENTOS)
                variacao = f"{tipo_log.lower()} {nome_log.lower()}, {numero}, {comp}"
                descricao = "Com complemento"
            elif variacao_tipo == "com_referencia":
                ref = random.choice(REFERENCIAS_LOCAIS)
                variacao = f"{tipo_log.lower()} {nome_log.lower()}, {numero}, {ref}"
                descricao = "Com referência local"
            else:  # formato_sequencial
                variacao = f"{tipo_log.lower()} {nome_log.lower()} {numero} {bairro.lower()} {cidade.lower()}"
                descricao = "Formato sequencial"
            
            registros.append({
                "id": f"VAR{var_id:06d}",
                "uid_base": uid,
                "tipo_logradouro": tipo_log,
                "nome_logradouro": nome_log,
                "numero": numero,
                "bairro": bairro,
                "cidade": cidade,
                "uf": uf,
                "variacao": variacao,
                "descricao_variacao": descricao
            })
            var_id += 1
            
            if var_id > n:
                break
        
        if var_id > n:
            break
    
    return registros

def salvar_csv(nome_arquivo: str, dados: List[dict], campo_headers: List[str]):
    """Salva dados em arquivo CSV"""
    caminho = f"bronze/{nome_arquivo}"
    print(f"Gerando {nome_arquivo}... ({len(dados)} registros)")
    
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campo_headers)
        writer.writeheader()
        writer.writerows(dados)
    
    print(f"  ✓ {nome_arquivo} gerado com sucesso!")

def main():
    print("="*60)
    print("GERADOR DE DADOS EM MASSA")
    print("="*60)
    print()
    
    # Gerar endereços livres (1000+)
    enderecos_livres = gerar_enderecos_livres(1500)
    salvar_csv("enderecos_livres.csv", enderecos_livres, 
               ["id", "endereco_livre", "uf", "cidade", "timestamp"])
    
    # Gerar endereços com erros (1000+)
    enderecos_erros = gerar_enderecos_com_erros(1500)
    salvar_csv("enderecos_com_erros.csv", enderecos_erros,
               ["id", "endereco_livre", "uf", "cidade", "timestamp", "tipo_erro"])
    
    # Gerar DNE (1000+)
    dne = gerar_fonte_referencia(1200, "DNE")
    salvar_csv("dne.csv", dne,
               ["id_fonte", "tipo_logradouro", "nome_logradouro", "numero", "bairro",
                "cidade", "uf", "cep", "latitude", "longitude", "confiabilidade"])
    
    # Gerar CNEFE (1000+)
    cnefe = gerar_fonte_referencia(1200, "CNEFE")
    salvar_csv("cnefe.csv", cnefe,
               ["id_fonte", "tipo_logradouro", "nome_logradouro", "numero", "bairro",
                "cidade", "uf", "cep", "latitude", "longitude", "confiabilidade"])
    
    # Gerar OSM (1000+)
    osm = gerar_fonte_referencia(1200, "OSM")
    salvar_csv("osm.csv", osm,
               ["id_fonte", "tipo_logradouro", "nome_logradouro", "numero", "bairro",
                "cidade", "uf", "cep", "latitude", "longitude", "confiabilidade"])
    
    # Gerar dados geográficos (1000+)
    geograficos = gerar_dados_geograficos(1500)
    salvar_csv("dados_geograficos.csv", geograficos,
               ["id", "tipo_logradouro", "nome_logradouro", "numero", "bairro",
                "cidade", "uf", "latitude", "longitude", "precisao", "altitude", "fonte_geografica"])
    
    # Gerar variações (1000+)
    variacoes = gerar_variacoes_enderecos(1500)
    salvar_csv("variacoes_enderecos.csv", variacoes,
               ["id", "uid_base", "tipo_logradouro", "nome_logradouro", "numero",
                "bairro", "cidade", "uf", "variacao", "descricao_variacao"])
    
    print()
    print("="*60)
    print("RESUMO")
    print("="*60)
    print(f"Endereços Livres:        {len(enderecos_livres):>6} registros")
    print(f"Endereços com Erros:     {len(enderecos_erros):>6} registros")
    print(f"DNE:                     {len(dne):>6} registros")
    print(f"CNEFE:                   {len(cnefe):>6} registros")
    print(f"OSM:                     {len(osm):>6} registros")
    print(f"Dados Geográficos:       {len(geograficos):>6} registros")
    print(f"Variações:               {len(variacoes):>6} registros")
    print("="*60)
    print(f"TOTAL:                   {sum([len(enderecos_livres), len(enderecos_erros), len(dne), len(cnefe), len(osm), len(geograficos), len(variacoes)]):>6} registros")
    print("="*60)

if __name__ == "__main__":
    main()
