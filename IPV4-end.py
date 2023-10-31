import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import sqlite3
from tkinter import Text
from ttkthemes import ThemedStyle
from tkinter import ttk
import socket
import os
import psutil
import ctypes
import subprocess
import speedtest
from getmac import get_mac_address
import geocoder
import platform
import nmap
from ping3 import ping, verbose_ping

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


def salvar_e_mostrar_informacoes():
    ip = ip_entry.get()

    if not ip:
        messagebox.showerror(
            "Erro", "Por favor, insira um endereço IP válido.")
        return

    def Classe_IP(ip):
        if int(ip.split('.')[0]) < 128:
            return "Classe A"
        elif int(ip.split('.')[0]) < 192:
            return "Classe B"
        else:
            return "Classe C"

    def Classe_Rede(ip):
        ip_parts = ip.split('/')
        prefixo = int(ip_parts[-1])

        if prefixo < 16:
            classe_rede = "Classe A"
        elif prefixo < 24:
            classe_rede = "Classe B"
        else:
            classe_rede = "Classe C"

        return classe_rede
# sub redes são os numros de 1 a 32 exeto os numeros  8, 16, 32

    def classe_sub_rede(ip):
        ip_parts = ip.split('/')
        prefixo = int(ip_parts[-1])
        if prefixo == 16 or prefixo == 24 or prefixo == 8:
            status = "Não é Uma Sub Rede"
        else:
            status = "É uma Sub Rede"
        return status

    def calculo_mascara(ip):
        ip_parts = ip.split('/')
        prefixo = int(ip_parts[-1])
# pega o prefixo apos a barraa e subtrai de acordo  com   o tamnho seguindo  a lei das classes ex:/19
        if prefixo < 16:
            calc = prefixo - 8
        elif prefixo <= 24:
            calc = prefixo - 16
        else:
            calc = prefixo - 32
# segindo com o ex: /19 pertence a classe B da sub rede então  faremos assim 19 - 16 sobrando 3 a quantidade de bits que iremos somar de acordo com a  tabela 1 - 128 2 - 64 ...
        if calc == 1:
            CM = 2**7
        elif calc == 2:
            CM = 2**7 + 2**6
        elif calc == 3:
            CM = 2**7 + 2**6 + 2**5
        elif calc == 4:
            CM = 2**7 + 2**6 + 2**5 + 2**4
        elif calc == 5:
            CM = 2**7 + 2**6 + 2**5 + 2**4 + 2**3
        elif calc == 6:
            CM = 2**7 + 2**6 + 2**5 + 2**4 + 2**3 + 2**2
        elif calc == 7:
            CM = 2**7 + 2**6 + 2**5 + 2**4 + 2**3 + 2**2 + 2**1
        else:
            CM = "erro"  # Definindo um valor padrão para o caso de calc ser inválido
# aki definimos qual o tipo de classe sera a nossa maskara no caso qual layout vamos usar de acordo com a CLasse da Rede
        if Classe_Rede(ip) == "Classe A":
            mascara_rede = f"255.{CM}.0.0"
        elif Classe_Rede(ip) == "Classe B":
            mascara_rede = f"255.255.{CM}.0"
        elif Classe_Rede(ip) == "Classe C":
            mascara_rede = f"255.255.255.{CM}"
        else:
            mascara_rede = "erro"  # Definindo um valor padrão para o caso de classe de rede inválida

        return mascara_rede
# aki pegaremos o id da rede que seria a primeira parte do ip fora o prefixo ex:/19

    def Id_da_rede(ip):
        partes = ip.split('/')
        parte_ip = partes[0]
        return parte_ip
# para acharmos o wild card é nessesario subtrair 255.255.255.255 - mascara de rede que achamos  anteriormente.

    def wild_card():
        mascara = calculo_mascara(ip)
        partes_mascara = mascara.split('.')
        wildcard = []

        for parte in partes_mascara:
            octeto_wildcard = 255 - int(parte)
            wildcard.append(str(octeto_wildcard))

        wildcard_str = ".".join(wildcard)
        return wildcard_str
# ao somar o id da rede com o wildcard temos o broadcast

    def broad_cast():
        wildcard_parts = wild_card().split('.')
        id_parts = Id_da_rede(ip).split('.')

        broadcast_parts = []

        for w, id in zip(wildcard_parts, id_parts):
            broadcast_part = str(int(w) + int(id))
            broadcast_parts.append(broadcast_part)

        broadcast = ".".join(broadcast_parts)
        return broadcast

    conn = sqlite3.connect('meu_banco_de_dados.db')
    cursor = conn.cursor()

    # Execute consultas SQL para inserir as informações
    cursor.execute("INSERT INTO informacoes_ip (ip_address, classe_ip, classe_rede, status_sub_rede, mascara_sub_rede, id_rede, wild_card, broadcast) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (ip, Classe_IP(ip), Classe_Rede(ip), classe_sub_rede(ip), calculo_mascara(ip), Id_da_rede(ip), wild_card(), broad_cast()))

    conn.commit()

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
        messagebox.showerror(
            "Erro", "As informações não foram encontradas no banco de dados.")
# Função para obter informações do roteador
def obter_gateway_info():
    gateways = psutil.net_if_addrs()
    gateway_info = "Não foi possível obter informações do roteador"

    for interface, addrs in gateways.items():
        if "Wi-Fi" in interface or "Wireless" in interface:
            connection_type = "Conectado via Wi-Fi"
        elif "Ethernet" in interface:
            connection_type = "Conectado via Ethernet"
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                gateway_info = f"Endereço MAC do Roteador: {addr.address}"

    return connection_type, gateway_info

# Função para obter a localização com base no IP
def obter_ip_location(ip_address):
    try:
        location = geocoder.ip(ip_address)
        return f"Localização: {location.country} - {location.region} - {location.city}\nLatitude: {location.lat}, Longitude: {location.lng}"
    except Exception as e:
        return f"Erro ao obter localização: {str(e)}"

# Função para obter informações de rede
def obter_informacoes_de_rede():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    system_info = f"Nome do Host: {host_name}\nEndereço IP Local: {ip_address}\nSistema Operacional: {platform.system()} {platform.release()}"

    # Obtenha o nome da rede Wi-Fi e a latência (ping)
    wifi_name = "Não conectado à Wi-Fi"
    ping_result = "Erro ao medir a latência"

    try:
        wifi_name = "Substitua por seu método de obter o nome da rede Wi-Fi"

        # Medir a latência
        target_host = "8.8.8.8"  # Exemplo: servidor DNS do Google
        response_time = ping(target_host)
        if response_time is not None:
            ping_result = f"Latência (Ping) para {target_host}: {response_time:.2f} ms"
        else:
            ping_result = "Erro ao medir a latência"

    except Exception as e:
        wifi_name = "Erro ao obter o nome da rede Wi-Fi"
        ping_result = "Erro ao medir a latência"

    # Obtenha informações do roteador
    connection_type, gateway_info = obter_gateway_info()

    location_info = obter_ip_location(ip_address)

    network_info = f"Nome da Rede Wi-Fi: {wifi_name}\n"
    network_info += f"Latência (Ping): {ping_result}\n"
    network_info += f"Tipo de Conexão: {connection_type}\n{gateway_info}"

    # Inserir os dados coletados no banco de dados
    conn = sqlite3.connect('dados_users.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users_data (host_name, ip_address, system_info, wifi_name, ping_result, connection_type, gateway_info, location_info)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (host_name, ip_address, system_info, wifi_name, ping_result, connection_type, gateway_info, location_info))

    conn.commit()
    conn.close()

    info_text2.delete('1.0', tk.END)  # Limpe o texto anterior, se houver
    info_text2.insert('1.0', system_info + "\n" + network_info + "\n" + location_info)

# Crie a janela principal
root = tk.Tk()
root.title("Informações de Rede")

# Configuração da janela Tkinter
root = tk.Tk()
root.title("Minhas Definições IP")

# Configure a janela para tela cheia
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()
root.geometry(f"{largura_tela}x{altura_tela}")
root.attributes('-fullscreen', True)

# Personalize o estilo da janela
style = ttk.Style()
# Use um tema diferente da ttk para melhor integração com o Tkinter
style.theme_use("clam")

# Crie um frame para agrupar os elementos
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Configure o fundo com a cor branca
frame.configure(bg="white")

# Rótulo e campo de entrada para o IP
ip_label = tk.Label(
    frame, text="Digite o endereço IP no formato X.X.X.X/X:", font=('Helvetica', 20))
ip_label.pack(pady=20)

ip_entry = tk.Entry(frame, font=('Helvetica', 18), width=40)
ip_entry.pack(ipadx=20, pady=20)

# Botão para salvar e mostrar informações
process_button = tk.Button(
    frame, text="Salvar e Mostrar", command=salvar_e_mostrar_informacoes, font=('Helvetica', 20), bg='blue', fg='white')
process_button.pack(pady=20)

# Widget de texto para mostrar as informações
info_text = tk.Text(frame, height=15, width=60, font=(
    'Helvetica', 18), bg='black', fg='white')
info_text.pack()

# Crie um segundo frame para as informações de rede
frame2 = tk.Frame(root)
frame2.pack(side=tk.BOTTOM, fill=tk.BOTH)

# Configure o fundo com a cor preta e letras brancas
frame2.configure(bg="black")
style.configure("TLabel", foreground="white")  # Configura o estilo da label

# Widget de texto para mostrar as informações de rede
info_text2 = tk.Text(frame2, height=10, width=largura_tela,
                     font=('Helvetica', 18), bg='black', fg='white')
info_text2.pack()

# Botão para obter informações de rede

# Alinhe o conteúdo ao centro da janela
root.grid_rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

info_text.insert('1.0', "Insira um endereço IP para exibir informações.")
# Chame a função para exibir informações de rede automaticamente
obter_informacoes_de_rede()
root.mainloop()
# Desenvolvido  By: Buehno :)
# contato:  https://linktr.ee/Ronaldo.Bueeno
