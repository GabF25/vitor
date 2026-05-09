# Gerador SQL — Revisão de Acessos Protheus

Utilitário desktop que lê uma planilha `.xlsx` de revisão de acessos do ERP **Protheus (TOTVS)** e gera automaticamente um arquivo `.sql` com os `UPDATE`s prontos para execução no **SQL Server**.

---

## Como usar

### Requisitos

- Python 3.10+
- Instalar dependências:

```
pip install -r requirements.txt
```

### Rodar a interface

```
python main.py
```

1. Clique em **Procurar** e selecione a planilha `.xlsx`
2. Clique em **Salvar como** para escolher onde salvar o `.sql` (ou use o caminho preenchido automaticamente)
3. Clique em **Gerar SQL**
4. O resultado aparece na área de log com o total de UPDATEs gerados e linhas ignoradas

---

## Compilar para `.exe`

```
build.bat
```

O executável é gerado em `dist\GeradorSQL_Protheus.exe` e pode ser distribuído para qualquer máquina Windows sem instalar Python.

> Na primeira abertura o `.exe` demora ~3-5 segundos para iniciar — é comportamento normal do PyInstaller (`--onefile`), não é bug.

---

## Formato da planilha de entrada

A planilha `.xlsx` deve conter exatamente estas colunas:

| Coluna | Descrição |
|---|---|
| `REGRA_DESCRICAO` | Descrição da regra (campo `RL__DESCRI` na `SYS_RULES`) |
| `ROTINA_NOME` | Nome da rotina (`RL__ROTINA`) |
| `ROTINA_OPCAO` | Opção de menu (`RL__MENUID`) — pode ser vazio |
| `ROTINA_ACESSA` | `PERMITIDO`, `NÃO PERMITIDO` ou `NEGADO` — ignorado se `ROTINA_OPCAO` for vazio |
| `ROTINA_FUNCAO_MENU` | Função do menu (`RL__MENUDEF`) |
| `MENU_ACESSA` | `PERMITIDO`, `NÃO PERMITIDO` ou `NEGADO` |

---

## Regras de geração

- **`ROTINA_OPCAO` preenchida** → `UPDATE SYS_RULES_FEATURES` usando `ROTINA_ACESSA`
- **`ROTINA_OPCAO` vazia** → `UPDATE SYS_RULES_TRANSACT` usando `MENU_ACESSA`
- Linhas onde o valor de acesso relevante for vazio são **ignoradas**

Mapeamento de acesso: `PERMITIDO=1`, `NÃO PERMITIDO=2`, `NEGADO=3`

---

## Estrutura do projeto

```
├── main.py              # Entry point
├── backend/
│   ├── reader.py        # Leitura e validação da planilha
│   └── generator.py     # Geração das queries SQL
├── frontend/
│   └── app.py           # Interface Tkinter
├── requirements.txt
└── build.bat            # Compila o .exe
```
