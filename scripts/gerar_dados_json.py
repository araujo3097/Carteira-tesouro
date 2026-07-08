"""
Gera dados.json com o PU de venda mais recente de cada vencimento da
NTN-B Principal, a partir do arquivo oficial do Tesouro Nacional.

Usado pelo workflow do GitHub Actions (.github/workflows/atualizar.yml),
que roda este script todo dia e publica o dados.json atualizado no site.
"""

import json
import re
import sys
from datetime import datetime

import requests
import pandas as pd

ANO = 2026
ARQUIVO_TEMP = "_download.xls"
ARQUIVO_SAIDA = "dados.json"

# Cada título tem seu próprio arquivo no CDN do Tesouro, com o mesmo padrão
# de nome. Para adicionar outro título no futuro, basta incluir uma entrada
# aqui com o "slug" usado na URL (a parte do nome do arquivo antes de
# "_2026.xls") e o nome de exibição.
TITULOS = [
    {"slug": "NTN-B_Principal", "nome": "Tesouro IPCA+"},
    {"slug": "NTN-F", "nome": "Tesouro Prefixado com Juros Semestrais"},
    {"slug": "Tesouro_Renda+_Aposentadoria_Extra", "nome": "Tesouro Renda+ Aposentadoria Extra"},
]


def url_do_titulo(slug):
    return f"https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/sistd/{ANO}/{slug}_{ANO}.xls"


def baixar(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    with open(ARQUIVO_TEMP, "wb") as f:
        f.write(resp.content)


def formatar_vencimento(aba):
    # O nome da aba sempre termina em DDMMAA (ex: "NTN-B Princ 150826",
    # "NTN-B1 151230"). Extrai esses 6 dígitos finais, não importa o prefixo.
    m = re.search(r"(\d{6})\s*$", aba)
    if not m:
        return aba  # não achou o padrão esperado; devolve o nome cru
    v = m.group(1)
    return f"{v[0:2]}/{v[2:4]}/20{v[4:6]}"


def extrair_ultimo_pu(nome_titulo):
    xl = pd.ExcelFile(ARQUIVO_TEMP)
    resultado = []
    for aba in xl.sheet_names:
        df = pd.read_excel(ARQUIVO_TEMP, sheet_name=aba, header=None, skiprows=2)
        df.columns = ["Dia", "TaxaCompra", "TaxaVenda", "PUCompra", "PUVenda", "PUBase"]
        df = df.dropna(subset=["Dia"])
        df["Dia"] = pd.to_datetime(df["Dia"], format="%d/%m/%Y", errors="coerce")
        df = df.dropna(subset=["Dia"]).sort_values("Dia")

        ultima = df.iloc[-1]
        resultado.append({
            "titulo": nome_titulo,
            "vencimento": formatar_vencimento(aba),
            "puVenda": round(float(ultima["PUVenda"]), 2),
            "taxaVenda": round(float(ultima["TaxaVenda"]) * 100, 4),
            "dataRef": ultima["Dia"].strftime("%d/%m/%Y"),
        })
    return resultado


def main():
    todos = []
    for t in TITULOS:
        try:
            baixar(url_do_titulo(t["slug"]))
            todos.extend(extrair_ultimo_pu(t["nome"]))
        except Exception as e:
            print(f"ERRO ao processar {t['nome']}: {e}", file=sys.stderr)
            # continua para os outros títulos mesmo se um falhar

    if not todos:
        print("ERRO: nenhum título foi processado com sucesso.", file=sys.stderr)
        sys.exit(1)

    saida = {
        "atualizadoEm": datetime.utcnow().isoformat() + "Z",
        "titulos": todos,
    }
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print(f"dados.json atualizado com {len(todos)} linhas (vencimentos de todos os títulos).")


if __name__ == "__main__":
    main()
