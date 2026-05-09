import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk

from backend.generator import gerar_sql
from backend.reader import ler_planilha


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerador SQL — Revisão de Acessos Protheus")
        self.resizable(False, False)
        self._fila: queue.Queue = queue.Queue()
        self._construir_ui()

    def _construir_ui(self):
        pad = {'padx': 12, 'pady': 6}

        frame_entrada = ttk.LabelFrame(self, text="Arquivo de entrada (.xlsx)")
        frame_entrada.grid(row=0, column=0, sticky="ew", **pad)

        self._var_entrada = tk.StringVar()
        ttk.Entry(frame_entrada, textvariable=self._var_entrada, width=65).grid(
            row=0, column=0, padx=6, pady=6
        )
        ttk.Button(frame_entrada, text="Procurar", command=self._selecionar_entrada).grid(
            row=0, column=1, padx=6, pady=6
        )

        frame_saida = ttk.LabelFrame(self, text="Arquivo de saída (.sql)")
        frame_saida.grid(row=1, column=0, sticky="ew", **pad)

        self._var_saida = tk.StringVar()
        ttk.Entry(frame_saida, textvariable=self._var_saida, width=65).grid(
            row=0, column=0, padx=6, pady=6
        )
        ttk.Button(frame_saida, text="Salvar como", command=self._selecionar_saida).grid(
            row=0, column=1, padx=6, pady=6
        )

        self._btn_gerar = ttk.Button(self, text="  Gerar SQL  ", command=self._iniciar_geracao)
        self._btn_gerar.grid(row=2, column=0, pady=10)

        frame_log = ttk.LabelFrame(self, text="Resultado")
        frame_log.grid(row=3, column=0, sticky="nsew", **pad)

        self._txt_log = scrolledtext.ScrolledText(
            frame_log, width=85, height=14, state='disabled', font=('Consolas', 9)
        )
        self._txt_log.grid(row=0, column=0, padx=6, pady=6)

        self._var_status = tk.StringVar(value="Pronto.")
        ttk.Label(self, textvariable=self._var_status, foreground='gray').grid(
            row=4, column=0, pady=(0, 10)
        )

        self.columnconfigure(0, weight=1)

    def _selecionar_entrada(self):
        path = filedialog.askopenfilename(
            title="Selecionar planilha",
            filetypes=[("Planilhas Excel", "*.xlsx"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self._var_entrada.set(path)
            if not self._var_saida.get():
                self._var_saida.set(os.path.splitext(path)[0] + ".sql")

    def _selecionar_saida(self):
        path = filedialog.asksaveasfilename(
            title="Salvar arquivo SQL",
            defaultextension=".sql",
            filetypes=[("Arquivo SQL", "*.sql"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self._var_saida.set(path)

    def _iniciar_geracao(self):
        entrada = self._var_entrada.get().strip()
        saida = self._var_saida.get().strip()

        if not entrada:
            self._log("Erro: selecione o arquivo de entrada (.xlsx).")
            return
        if not saida:
            self._log("Erro: informe o caminho do arquivo de saída (.sql).")
            return

        self._btn_gerar.config(state='disabled')
        self._var_status.set("Processando...")
        self._limpar_log()

        threading.Thread(target=self._processar, args=(entrada, saida), daemon=True).start()
        self.after(100, self._checar_fila)

    def _processar(self, entrada: str, saida: str):
        try:
            df = ler_planilha(entrada)
            nome_origem = os.path.basename(entrada)
            sql, stats = gerar_sql(df, nome_origem)
            with open(saida, 'w', encoding='utf-8') as f:
                f.write(sql)
            self._fila.put({'ok': True, 'stats': stats, 'saida': saida})
        except Exception as exc:
            self._fila.put({'ok': False, 'erro': str(exc)})

    def _checar_fila(self):
        try:
            resultado = self._fila.get_nowait()
        except queue.Empty:
            self.after(100, self._checar_fila)
            return

        self._btn_gerar.config(state='normal')

        if resultado['ok']:
            s = resultado['stats']
            self._log(
                f"Concluído com sucesso!\n\n"
                f"  SYS_RULES_FEATURES : {s['features']} UPDATEs\n"
                f"  SYS_RULES_TRANSACT : {s['transact']} UPDATEs\n"
                f"  Total gerado       : {s['total']} UPDATEs\n"
                f"  Linhas ignoradas   : {s['ignorados']}\n\n"
                f"Arquivo salvo em:\n  {resultado['saida']}"
            )
            self._var_status.set("Pronto.")
        else:
            self._log(f"Erro durante o processamento:\n\n  {resultado['erro']}")
            self._var_status.set("Erro.")

    def _log(self, texto: str):
        self._txt_log.config(state='normal')
        self._txt_log.insert('end', texto + '\n')
        self._txt_log.config(state='disabled')
        self._txt_log.see('end')

    def _limpar_log(self):
        self._txt_log.config(state='normal')
        self._txt_log.delete('1.0', 'end')
        self._txt_log.config(state='disabled')
