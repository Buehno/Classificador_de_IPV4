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


def obter_informacoes_de_rede():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    system_info = f"Nome do Host: {host_name}\nEndereço IP Local: {ip_address}\nSistema Operacional: {os.name}"

    # Adicione as informações da rede
    try:
        interfaces = psutil.net_if_addrs()
        for interface, addrs in interfaces.items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    network_info = f"Nome da Rede: {interface}\nEndereço IP: {addr.address}\n"
                    if addr.broadcast:
                        network_info += f"Endereço de Broadcast: {addr.broadcast}\n"
                    if addr.netmask:
                        network_info += f"Máscara de Sub-rede: {addr.netmask}\n"

                    # Obtenha informações adicionais sobre a placa de rede
                    network_info += f"MAC Address: {psutil.net_if_stats()[interface].address}\n"

                    # Obtenha informações sobre o tipo de segurança da rede (você pode ajustar isso de acordo com suas necessidades)
                    # Substitua por suas informações reais
                    network_info += f"Tipo de Segurança: WPA2"

                    # Use a biblioteca ctypes para obter informações da rede no Windows
                    network_info += f"Operadora: {ctypes.windll.iphlpapi.GetNetworkParamsEx(None)}\n"

                    # Limpe o texto anterior, se houver
                    info_text2.delete('1.0', tk.END)
                    info_text2.insert('1.0', system_info + network_info)
                    return
    except Exception as e:
        # Lida com exceções ao obter informações da rede
        info_text2.delete('1.0', tk.END)
        info_text2.insert(
            '1.0', f"Erro ao obter informações de rede: {str(e)}")


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
