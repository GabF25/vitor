import pandas as pd

REQUIRED_COLUMNS = {
    'REGRA_DESCRICAO', 'ROTINA_NOME', 'ROTINA_OPCAO',
    'ROTINA_ACESSA', 'ROTINA_FUNCAO_MENU', 'MENU_ACESSA',
}


def ler_planilha(caminho: str) -> pd.DataFrame:
    df = pd.read_excel(caminho)
    df.columns = df.columns.str.strip()

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes na planilha: {', '.join(sorted(missing))}")

    for col in REQUIRED_COLUMNS:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    return df
