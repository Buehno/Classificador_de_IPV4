import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import sqlite3

def criar_tabela():
    conn = sqlite3.connect('meu_banco_de_dados.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS informacoes_ip (
                      id INTEGER PRIMARY KEY,
                      ip_address TEXT,
                      classe_ip TEXT,
                      classe_rede TEXT,
                      status_sub_rede TEXT,
                      mascara_sub_rede TEXT,
                      id_rede TEXT,
                      wild_card TEXT,
                      broadcast TEXT)''')
    conn.commit()
    conn.close()

def salvar_informacoes_ip():
    ip = ip_entry.get()

    # Conecte-se ao banco de dados SQLite
    conn = sqlite3.connect('meu_banco_de_dados.db')
    cursor = conn.cursor()

    # Execute consultas SQL para inserir as informações
    cursor.execute("INSERT INTO informacoes_ip (ip_address, classe_ip, classe_rede, status_sub_rede, mascara_sub_rede, id_rede, wild_card, broadcast) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (ip, Classe_IP(ip), Classe_Rede(ip), classe_sub_rede(ip), calculo_mascara(ip), Id_da_rede(ip), wild_card(), broad_cast()))

    conn.commit()
    conn.close()

    messagebox.showinfo("Sucesso", "As informações foram salvas no banco de dados.")

def abrir_arquivo():
    ip = ip_entry.get()

    # Conecte-se ao banco de dados SQLite
    conn = sqlite3.connect('meu_banco_de_dados.db')
    cursor = conn.cursor()

    # Execute uma consulta SQL para buscar as informações com base no IP
    cursor.execute("SELECT * FROM informacoes_ip WHERE ip_address = ?", (ip,))
    data = cursor.fetchone()

    conn.close()

    if data:
        info_text.delete(1.0, tk.END)  # Limpa o widget de texto
        # Insira as informações do banco de dados no widget de texto
        info_text.insert(tk.END, f"Classe de IP: {data[2]}\n")
        info_text.insert(tk.END, f"Classe de Rede: {data[3]}\n")
        info_text.insert(tk.END, f"Status: {data[4]}\n")
        info_text.insert(tk.END, f"Máscara de Sub-rede: {data[5]}\n")
        info_text.insert(tk.END, f"ID de Rede: {data[6]}\n")
        info_text.insert(tk.END, f"Wild Card: {data[7]}\n")
        info_text.insert(tk.END, f"Broadcast: {data[8]}\n")
    else:
        messagebox.showerror("Erro", "As informações não foram encontradas no banco de dados.")

def Classe_IP(ip):
     ip_parts = ip.split('/')
        prefixo = int(ip_parts[-1])

        if prefixo < 16:
            classe_rede = "Classe A"
        elif prefixo < 24:
            classe_rede = "Classe B"
        else:
            classe_rede = "Classe C"

        return classe_rede
def Classe_Rede(ip):
    # ... (seu código para determinar a classe da rede)

def classe_sub_rede(ip):
    # ... (seu código para determinar a classe da sub-rede)

def calculo_mascara(ip):
    # ... (seu código para calcular a máscara de sub-rede)

def Id_da_rede(ip):
    # ... (seu código para determinar o ID da rede)

def wild_card():
    # ... (seu código para determinar o wild card)

def broad_cast():
    # ... (seu código para determinar o broadcast)

criar_tabela()

# Configuração da janela Tkinter
root = tk.Tk()
root.title("Análise de IP")

# Rótulo e campo de entrada para o IP
ip_label = tk.Label(root, text="Digite o endereço IP no formato X.X.X.X/X:")
ip_label.pack()
ip_entry = tk.Entry(root)
ip_entry.pack()

# Botão para processar e mostrar as informações
process_button = tk.Button(
    root, text="Processar e Mostrar", command=salvar_informacoes_ip)
process_button.pack()

# Botão para abrir o arquivo
open_button = tk.Button(root, text="Abrir Arquivo", command=abrir_arquivo)
open_button.pack()

# Widget de texto para mostrar as informações
info_text = tk.Text(root, height=10, width=40)
info_text.pack()

root.mainloop()
