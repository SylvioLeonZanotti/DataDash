from flask import Flask, request, jsonify, send_file, render_template
from functions import carregar_arquivo, processar_dados, gerar_dashboard, realizar_download
import os
import tempfile
import threading
import queue

app = Flask(__name__)
q = queue.Queue()

@app.route('/')
def index():
    return render_template('index.html')

# Rota para carregar o arquivo
@app.route('/carregar_arquivo', methods=['POST'])
def carregar_arquivo_route():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    file_path = os.path.join(tempfile.gettempdir(), file.filename)
    file.save(file_path)
    
    return jsonify({"message": "Arquivo carregado com sucesso", "file_path": file_path})

# Rota para processar dados e gerar gráficos
@app.route('/processar_dados', methods=['POST'])
def processar_dados_route():
    data = request.json
    file_path = data.get("file_path")
    coluna = data.get("coluna")
    grafico_tipo = data.get("grafico_tipo")

    if not file_path or not coluna or not grafico_tipo:
        return jsonify({"error": "Parâmetros faltando"}), 400
    
    try:
        threading.Thread(target=executar_processamento, args=(file_path, coluna, grafico_tipo, q)).start()
        return jsonify({"message": "Processamento iniciado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Função para execução do processamento
def executar_processamento(file_path, coluna, grafico_tipo, q):
    try:
        temp_dir = tempfile.mkdtemp()
        df = pd.read_excel(file_path, engine='xlrd' if file_path.endswith('.xls') else None)
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

        output_path = os.path.join(temp_dir, f"{coluna}_{grafico_tipo}.png")
        plt.savefig(output_path)
        plt.close()

        q.put((output_path, "graph"))
    except Exception as e:
        q.put((str(e), "error"))

# Rota para gerar dashboard
@app.route('/gerar_dashboard', methods=['POST'])
def gerar_dashboard_route():
    data = request.json
    file_path = data.get("file_path")

    if not file_path:
        return jsonify({"error": "Parâmetros faltando"}), 400
    
    try:
        threading.Thread(target=executar_dashboard, args=(file_path, q)).start()
        return jsonify({"message": "Geração do dashboard iniciada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Função para execução do dashboard
def executar_dashboard(file_path, q):
    try:
        temp_dir = tempfile.mkdtemp()
        df = pd.read_excel(file_path, engine='xlrd' if file_path.endswith('.xls') else None)
        plots = []
        for coluna in df.select_dtypes(include=[float, int]).columns:
            plt.figure(figsize=(10, 6))  # Define o tamanho do gráfico
            sns.histplot(df[coluna].dropna(), kde=True)
            plt.title(f"Distribuição de {coluna}")
            plot_path = os.path.join(temp_dir, f"{coluna}_hist.png")
            plt.savefig(plot_path)
            plt.close()
            plots.append(plot_path)

        pdf_path = os.path.join(temp_dir, "dashboard.pdf")
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        for plot in plots:
            pdf.add_page()
            pdf.image(plot, x=10, y=10, w=pdf.w - 20)
        pdf.output(pdf_path)

        q.put((pdf_path, "dashboard"))
    except Exception as e:
        q.put((str(e), "error"))

# Rota para fazer download do arquivo gerado
@app.route('/download', methods=['GET'])
def download_route():
    try:
        item = q.get_nowait()
        if item[1] == "error":
            return jsonify({"error": item[0]}), 500
        return send_file(item[0], as_attachment=True)
    except queue.Empty:
        return jsonify({"error": "Nenhum arquivo para download"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
