import tkinter as tk
from ttkbootstrap import Style, ttk
from PIL import Image, ImageTk
import queue

def criar_interface(root, carregar_arquivo, processar_dados, gerar_dashboard, realizar_download, q):
    style = Style(theme="darkly")
    canvas = tk.Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    frame = ttk.Frame(scrollable_frame, padding="20")
    frame.pack(fill='both', expand=True)

    titulo = ttk.Label(frame, text="DataDash", font=('Helvetica', 20, 'bold'))
    titulo.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

    upload_frame = ttk.LabelFrame(frame, text="Carregar Arquivo", padding="10")
    upload_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky='ew')

    btn_procurar = ttk.Button(upload_frame, text="Procurar", command=carregar_arquivo, bootstyle="primary-outline")
    btn_procurar.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    lbl_arquivo = ttk.Label(upload_frame, text="Local do arquivo:", width=50)
    lbl_arquivo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    btn_play = ttk.Button(upload_frame, text="Gerar Gráfico", command=processar_dados, state='disabled', bootstyle="success-outline")
    btn_play.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    btn_dashboard = ttk.Button(upload_frame, text="Gerar Dashboard", command=gerar_dashboard, state='disabled', bootstyle="info-outline")
    btn_dashboard.grid(row=1, column=2, padx=5, pady=5, sticky='ew')

    ttk.Label(upload_frame, text="Coluna:").grid(row=2, column=0, padx=5, pady=5, sticky='ew')
    coluna_combo = ttk.Combobox(upload_frame, bootstyle="info")
    coluna_combo.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

    ttk.Label(upload_frame, text="Tipo de Gráfico:").grid(row=3, column=0, padx=5, pady=5, sticky='ew')
    grafico_combo = ttk.Combobox(upload_frame, values=["Barras", "Pizza", "Linha"], bootstyle="info")
    grafico_combo.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
    grafico_combo.current(0)

    status_frame = ttk.LabelFrame(frame, text="Status do Processo", padding="10")
    status_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky='ew')

    lbl_status = ttk.Label(status_frame, text="")
    lbl_status.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    progress_bar = ttk.Progressbar(status_frame, mode='indeterminate', bootstyle="info-striped")
    progress_bar.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

    preview_frame = ttk.LabelFrame(frame, text="Preview do Gráfico", padding="10")
    preview_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky='ew')

    lbl_preview = ttk.Label(preview_frame)
    lbl_preview.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    download_frame = ttk.LabelFrame(frame, text="Download", padding="10")
    download_frame.grid(row=6, column=0, columnspan=3, pady=10, sticky='ew')

    btn_download = ttk.Button(download_frame, text="Download", command=realizar_download, bootstyle="success-outline", state='disabled')
    btn_download.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    # Função de preview do gráfico
    def atualizar_preview():
        try:
            while not q.empty():
                output_path, tipo = q.get_nowait()
                if tipo == "graph":
                    img = Image.open(output_path)
                    img = img.resize((200, 200), Image.LANCZOS)
                    img = ImageTk.PhotoImage(img)
                    lbl_preview.config(image=img)
                    lbl_preview.image = img
                elif tipo == "dashboard":
                    lbl_status.config(text=f"Dashboard gerado em: {output_path}")
                lbl_status.config(text="Processamento concluído!")
                progress_bar.stop()
                btn_download.config(state='normal')
        except queue.Empty:
            pass
        root.after(100, atualizar_preview)

    root.after(100, atualizar_preview)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return {
        "lbl_arquivo": lbl_arquivo,
        "btn_play": btn_play,
        "btn_dashboard": btn_dashboard,
        "coluna_combo": coluna_combo,
        "grafico_combo": grafico_combo,
        "lbl_status": lbl_status,
        "progress_bar": progress_bar,
        "btn_download": btn_download,
        "lbl_preview": lbl_preview
    }
