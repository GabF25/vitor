import pandas as pd
from datetime import datetime

ACESSO_MAP = {
    'PERMITIDO': 1,
    'NÃO PERMITIDO': 2,
    'NAO PERMITIDO': 2,
    'NEGADO': 3,
}


def _escape(valor: str) -> str:
    return valor.replace("'", "''")


def _mapear_acesso(valor):
    if pd.isna(valor):
        return None
    normalizado = str(valor).strip().upper()
    return ACESSO_MAP.get(normalizado)


def _agrupar(linhas: list) -> dict:
    grupos: dict = {}
    for regra, sql in linhas:
        grupos.setdefault(regra, []).append(sql)
    return grupos


def gerar_sql(df: pd.DataFrame, nome_arquivo_origem: str) -> tuple:
    linhas_features = []
    linhas_transact = []
    ignorados = 0

    for _, row in df.iterrows():
        if pd.isna(row['REGRA_DESCRICAO']) or pd.isna(row['ROTINA_NOME']):
            ignorados += 1
            continue

        regra_raw = str(row['REGRA_DESCRICAO']).strip()
        regra = _escape(regra_raw)
        rotina = _escape(str(row['ROTINA_NOME']).strip())
        opcao = row['ROTINA_OPCAO']

        tem_opcao = not pd.isna(opcao) and str(opcao).strip() != ''

        if tem_opcao:
            acesso = _mapear_acesso(row['ROTINA_ACESSA'])
            if acesso is None:
                ignorados += 1
                continue
            menuid = _escape(str(opcao).strip())
            sql = (
                f"UPDATE SYS_RULES_FEATURES SET RL__ACESSO = {acesso}\n"
                f"WHERE RL__ID = (SELECT TOP 1 RL__ID FROM SYS_RULES WHERE RL__DESCRI = '{regra}')\n"
                f"AND RL__ROTINA = '{rotina}'\n"
                f"AND RL__MENUID = '{menuid}';"
            )
            linhas_features.append((regra_raw, sql))
        else:
            acesso = _mapear_acesso(row['MENU_ACESSA'])
            if acesso is None:
                ignorados += 1
                continue
            sql = (
                f"UPDATE SYS_RULES_TRANSACT SET RL__ACESSO = {acesso}\n"
                f"WHERE RL__ID = (SELECT TOP 1 RL__ID FROM SYS_RULES WHERE RL__DESCRI = '{regra}')\n"
                f"AND RL__ROTINA = '{rotina}';"
            )
            linhas_transact.append((regra_raw, sql))

    total_features = len(linhas_features)
    total_transact = len(linhas_transact)
    total_geral = total_features + total_transact
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    partes = []

    partes.append(
        f"-- ============================================================\n"
        f"-- SCRIPT DE CORREÇÃO DE ACESSOS - PROTHEUS\n"
        f"-- Arquivo de origem: {nome_arquivo_origem}\n"
        f"-- Gerado em: {agora}\n"
        f"-- Total SYS_RULES_FEATURES: {total_features} UPDATEs\n"
        f"-- Total SYS_RULES_TRANSACT: {total_transact} UPDATEs\n"
        f"-- Total geral: {total_geral} UPDATEs\n"
        f"-- ============================================================\n"
    )

    if linhas_features:
        for regra, sqls in _agrupar(linhas_features).items():
            partes.append(
                f"\n-- ------------------------------------------------------------\n"
                f"-- REGRA: {regra}  ({len(sqls)} rotinas)\n"
                f"-- ------------------------------------------------------------\n"
            )
            for sql in sqls:
                partes.append(f"\n{sql}\n")

    if linhas_transact:
        partes.append(
            f"\n-- ============================================================\n"
            f"-- SYS_RULES_TRANSACT\n"
            f"-- ============================================================\n"
        )
        for regra, sqls in _agrupar(linhas_transact).items():
            partes.append(
                f"\n-- ------------------------------------------------------------\n"
                f"-- REGRA: {regra}  ({len(sqls)} rotinas)\n"
                f"-- ------------------------------------------------------------\n"
            )
            for sql in sqls:
                partes.append(f"\n{sql}\n")

    partes.append(
        f"\n-- ============================================================\n"
        f"-- FIM DO SCRIPT — {total_geral} registros atualizados\n"
        f"-- ============================================================\n"
    )

    conteudo = "".join(partes)
    stats = {
        'features': total_features,
        'transact': total_transact,
        'total': total_geral,
        'ignorados': ignorados,
    }
    return conteudo, stats
