import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Diretório absoluto para salvar relatórios e gráficos
REPORTS_DIR = Path(r"C:\Users\Couto\data-analyzer-ia\reports")
GRAFICOS_DIR = REPORTS_DIR / "graficos"

# Criar diretórios caso não existam
GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)

def carregar_dados(caminho_csv):
    df = pd.read_csv(caminho_csv, sep=';')
    return df.dropna()

def estatisticas(df):
    stats = df.describe().to_dict()
    corrs = df.corr().to_dict()
    return stats, corrs

def salvar_relatorios(stats, corrs, nome_base):
    txt_path = REPORTS_DIR / f"{nome_base}_relatorio.txt"
    json_path = REPORTS_DIR / f"{nome_base}_relatorio.json"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=== Estatísticas ===\n")
        f.write(json.dumps(stats, indent=4))
        f.write("\n\n=== Correlações ===\n")
        f.write(json.dumps(corrs, indent=4))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"estatisticas": stats, "correlacoes": corrs}, f, indent=4)

def gerar_graficos(df, nome_base):
    numeric = df.select_dtypes(include='number')
    for col in numeric.columns:
        plt.figure()
        sns.histplot(numeric[col], kde=True)
        plt.title(f'Histograma: {col}')
        plt.savefig(GRAFICOS_DIR / f"{nome_base}_hist_{col}.png")
        plt.close()

    plt.figure(figsize=(8,6))
    sns.heatmap(numeric.corr(), annot=True, fmt=".2f", cmap='coolwarm')
    plt.title('Mapa de Correlação')
    plt.savefig(GRAFICOS_DIR / f"{nome_base}_heatmap.png")
    plt.close()

def gerar_resumo_ia(df):
    resumo_textual = str(df.describe())
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um analista de dados experiente."},
                {"role": "user", "content": f"Analise os dados abaixo e gere um resumo em linguagem natural:\n{resumo_textual}"}
            ]
        )
        return resposta.choices[0].message['content']
    except Exception as e:
        return f"Falha ao gerar resumo via OpenAI. Erro: {e}"


def main():
    caminho_csv = input("Digite o caminho do CSV: ").strip()
    df = carregar_dados(caminho_csv)
    stats, corrs = estatisticas(df)
    nome_base = Path(caminho_csv).stem

    salvar_relatorios(stats, corrs, nome_base)
    gerar_graficos(df, nome_base)

    resumo = gerar_resumo_ia(df)
    resumo_path = REPORTS_DIR / f"{nome_base}_resumo.txt"
    with open(resumo_path, "w", encoding="utf-8") as f:
        f.write(resumo)

    print(f"Análise completa. Relatórios e gráficos salvos em '{REPORTS_DIR}'.")
    
if __name__ == "__main__":
    main()
