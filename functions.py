import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import threading
import tempfile
import shutil
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import queue
from fpdf import FPDF

# Variável global para armazenar o diretório temporário
temp_dir = None

def carregar_arquivo(interface_elements):
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xls *.xlsx")])
    if file_path:
        interface_elements["lbl_arquivo"].config(text=file_path)
        interface_elements["btn_play"].config(state='normal')
        interface_elements["btn_dashboard"].config(state='normal')
        carregar_colunas(file_path, interface_elements["coluna_combo"])

def carregar_colunas(file_path, coluna_combo):
    try:
        df = pd.read_excel(file_path, engine='xlrd' if file_path.endswith('.xls') else None)
        colunas = df.columns.tolist()
        coluna_combo['values'] = colunas
        coluna_combo.current(0)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar colunas do arquivo: {e}")

def processar_dados(interface_elements, q):
    file_path = interface_elements["lbl_arquivo"].cget("text")
    coluna = interface_elements["coluna_combo"].get()
    grafico_tipo = interface_elements["grafico_combo"].get()

    if file_path and coluna and grafico_tipo:
        try:
            threading.Thread(target=executar_processamento, args=(file_path, coluna, grafico_tipo, interface_elements, q)).start()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao processar o arquivo: {e}")

def executar_processamento(file_path, coluna, grafico_tipo, interface_elements, q):
    global temp_dir

    # Mostrar mensagem de processamento
    interface_elements["lbl_status"].config(text="Processando...")
    interface_elements["progress_bar"].start()

    try:
        # Carregar o arquivo Excel
        df = pd.read_excel(file_path, engine='xlrd' if file_path.endswith('.xls') else None)

        # Criar pasta temporária para salvar os gráficos
        temp_dir = tempfile.mkdtemp()

        # Gerar gráfico conforme seleção do usuário
        plt.figure(figsize=(10, 6))  # Define o tamanho do gráfico
        if grafico_tipo == 'Barras':
            df[coluna].value_counts().plot(kind='bar')
        elif grafico_tipo == 'Pizza':
            df[coluna].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=90)
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        elif grafico_tipo == 'Linha':
            df[coluna].value_counts().sort_index().plot(kind='line')

        plt.title(coluna)
        plt.xlabel('Valores')
        plt.ylabel('Frequência')
        plt.tight_layout()

        # Salvar gráfico
        output_path = os.path.join(temp_dir, f"{coluna}_{grafico_tipo}.png")
        plt.savefig(output_path)
        plt.close()

        # Enviar o caminho da imagem para a fila
        q.put((output_path, "graph"))
    except Exception as e:
        interface_elements["lbl_status"].config(text="Erro durante o processamento!")
        interface_elements["progress_bar"].stop()
        messagebox.showerror("Erro", f"Ocorreu um erro durante o processamento: {e}")

def gerar_dashboard(interface_elements, q):
    file_path = interface_elements["lbl_arquivo"].cget("text")

    if file_path:
        try:
            threading.Thread(target=executar_dashboard, args=(file_path, interface_elements, q)).start()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o dashboard: {e}")

def executar_dashboard(file_path, interface_elements, q):
    global temp_dir

    # Mostrar mensagem de processamento
    interface_elements["lbl_status"].config(text="Gerando dashboard...")
    interface_elements["progress_bar"].start()

    try:
        # Carregar o arquivo Excel
        df = pd.read_excel(file_path, engine='xlrd' if file_path.endswith('.xls') else None)

        # Criar pasta temporária para salvar os gráficos
        temp_dir = tempfile.mkdtemp()

        # Gerar gráficos
        plots = []
        for coluna in df.select_dtypes(include=[float, int]).columns:
            plt.figure(figsize=(10, 6))  # Define o tamanho do gráfico
            sns.histplot(df[coluna].dropna(), kde=True)
            plt.title(f"Distribuição de {coluna}")
            plt.tight_layout()
            plot_path = os.path.join(temp_dir, f"{coluna}_hist.png")
            plt.savefig(plot_path)
            plt.close()
            plots.append(plot_path)

        # Gerar um PDF com os gráficos
        pdf_path = os.path.join(temp_dir, "dashboard.pdf")
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        for plot in plots:
            pdf.add_page()
            pdf.image(plot, x=10, y=10, w=pdf.w - 20)
        pdf.output(pdf_path)

        # Enviar o caminho do PDF para a fila
        q.put((pdf_path, "dashboard"))
    except Exception as e:
        interface_elements["lbl_status"].config(text="Erro durante a geração do dashboard!")
        interface_elements["progress_bar"].stop()
        messagebox.showerror("Erro", f"Ocorreu um erro durante a geração do dashboard: {e}")

def realizar_download(interface_elements):
    global temp_dir
    if temp_dir:
        save_dir = filedialog.askdirectory(title="Selecione o diretório para salvar os gráficos")
        if save_dir:
            try:
                for filename in os.listdir(temp_dir):
                    shutil.move(os.path.join(temp_dir, filename), os.path.join(save_dir, filename))
                messagebox.showinfo("Sucesso", f"Gráficos salvos em: {save_dir}")
                shutil.rmtree(temp_dir)  # Remover a pasta temporária
                temp_dir = None
                interface_elements["btn_download"].config(state='disabled')
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar os gráficos: {e}")
        else:
            messagebox.showinfo("Informação", "O salvamento foi cancelado.")
