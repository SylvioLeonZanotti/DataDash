import tkinter as tk
from interface import criar_interface
from functions import carregar_arquivo, processar_dados, gerar_dashboard, realizar_download
import queue
from PIL import Image, ImageTk
import requests
import os

def download_image(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download image: {response.status_code}")

def main():
    root = tk.Tk()
    root.title("DataDash")
    root.geometry("800x600")

    # URL da imagem do ícone
    icon_url = "https://cdn.discordapp.com/attachments/1108965932069564416/1260647835871870976/icons8-ms-excel-64.png?ex=66901549&is=668ec3c9&hm=ee861fd0daa9eb079a678b70ffb1b6ddeb4561e85aafb076176cc978ceb50703&"  # Substitua pelo URL da sua imagem
    icon_path = "icon.png"

    # Baixar a imagem do ícone
    # try:
    #     download_image(icon_url, icon_path)
    # except Exception as e:
    #     print(f"Erro ao baixar o ícone: {e}")
    #     return

    # Adicionar ícone personalizado
    try:
        img = Image.open(icon_path)
        img = ImageTk.PhotoImage(img)
        root.iconphoto(False, img)  # Para formatos de imagem como .png
    except Exception as e:
        print(f"Erro ao definir o ícone: {e}")

    q = queue.Queue()

    interface_elements = criar_interface(
        root, 
        lambda: carregar_arquivo(interface_elements), 
        lambda: processar_dados(interface_elements, q), 
        lambda: gerar_dashboard(interface_elements, q),
        lambda: realizar_download(interface_elements),
        q
    )

    root.mainloop()

if __name__ == "__main__":
    main()
