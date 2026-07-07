"""
Gera dados.json com o PU de venda mais recente de cada vencimento da
NTN-B Principal, a partir do arquivo oficial do Tesouro Nacional.

Usado pelo workflow do GitHub Actions (.github/workflows/atualizar.yml),
que roda este script todo dia e publica o dados.json atualizado no site.
"""

import json
import sys
from datetime import datetime

import requests
import pandas as pd

ANO = 2026
URL = f"https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/sistd/{ANO}/NTN-B_Principal_{ANO}.xls"
ARQUIVO_TEMP = "_download.xls"
ARQUIVO_SAIDA = "dados.json"


def baixar():
    resp = requests.get(URL, timeout=30)
    resp.raise_for_status()
    with open(ARQUIVO_TEMP, "wb") as f:
        f.write(resp.content)


def extrair_ultimo_pu():
    xl = pd.ExcelFile(ARQUIVO_TEMP)
    resultado = []
    for aba in xl.sheet_names:
        df = pd.read_excel(ARQUIVO_TEMP, sheet_name=aba, header=None, skiprows=2)
        df.columns = ["Dia", "TaxaCompra", "TaxaVenda", "PUCompra", "PUVenda", "PUBase"]
        df = df.dropna(subset=["Dia"])
        df["Dia"] = pd.to_datetime(df["Dia"], format="%d/%m/%Y", errors="coerce")
        df = df.dropna(subset=["Dia"]).sort_values("Dia")

        ultima = df.iloc[-1]
        vencimento = aba.replace("NTN-B Princ ", "")
        vencimento_fmt = f"{vencimento[:2]}/{vencimento[2:4]}/20{vencimento[4:]}"

        resultado.append({
            "vencimento": vencimento_fmt,
            "puVenda": round(float(ultima["PUVenda"]), 2),
            "dataRef": ultima["Dia"].strftime("%d/%m/%Y"),
        })
    return resultado


def main():
    try:
        baixar()
        dados = extrair_ultimo_pu()
    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)

    saida = {
        "atualizadoEm": datetime.utcnow().isoformat() + "Z",
        "titulos": dados,
    }
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print(f"dados.json atualizado com {len(dados)} vencimentos.")


if __name__ == "__main__":
    main()
