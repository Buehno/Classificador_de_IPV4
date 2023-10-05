import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog


def salvar_informacoes_ip():
    ip = ip_entry.get()
#o primeiro numero do ip  no  caso (ex:192.1.0.16/19) 192 se enquandra  em classe A: 1 - 128 CLasse B: 129 - 192 Classe C: 192 - 255. Nesse caso um  ip de  classe B
    def Classe_IP(ip):
        ip_parts = ip.split('.')

        if int(ip_parts[0]) < 128:
            classe = "Classe A"
        elif int(ip_parts[0]) < 192:
            classe = "Classe B"
        else:
            classe = "Classe C"

        return classe
#classificador de rede  segue a mesma logica sendo numeros de 8 a 16 considerados classe  A , 16 a 24 considerados  Classe B e 25 a 32 considerados classe C 
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
#sub redes são os numros de 1 a 32 exeto os numeros  8, 16, 32
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
#pega o prefixo apos a barraa e subtrai de acordo  com   o tamnho seguindo  a lei das classes ex:/19
        if prefixo < 16:
            calc = prefixo - 8
        elif prefixo <= 24:
            calc = prefixo - 16 
        else:
            calc = prefixo - 32
#segindo com o ex: /19 pertence a classe B da sub rede então  faremos assim 19 - 16 sobrando 3 a quantidade de bits que iremos somar de acordo com a  tabela 1 - 128 2 - 64 ... 
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
#aki definimos qual o tipo de classe sera a nossa maskara no caso qual layout vamos usar de acordo com a CLasse da Rede
        if Classe_Rede(ip) == "Classe A":
            mascara_rede = f"255.{CM}.0.0"
        elif Classe_Rede(ip) == "Classe B":
            mascara_rede = f"255.255.{CM}.0"
        elif Classe_Rede(ip) == "Classe C":
            mascara_rede = f"255.255.255.{CM}"
        else:
            mascara_rede = "erro"  # Definindo um valor padrão para o caso de classe de rede inválida

        return mascara_rede
#aki pegaremos o id da rede que seria a primeira parte do ip fora o prefixo ex:/19
    def Id_da_rede(ip):
        partes = ip.split('/')
        parte_ip = partes[0]
        return parte_ip
#para acharmos o wild card é nessesario subtrair 255.255.255.255 - mascara de rede que achamos  anteriormente.
    def wild_card():
        mascara = calculo_mascara(ip)
        partes_mascara = mascara.split('.')
        wildcard = []

        for parte in partes_mascara:
            octeto_wildcard = 255 - int(parte)
            wildcard.append(str(octeto_wildcard))

        wildcard_str = ".".join(wildcard)
        return wildcard_str
#ao somar o id da rede com o wildcard temos o broadcast
    def broad_cast():
        wildcard_parts = wild_card().split('.')
        id_parts = Id_da_rede(ip).split('.')

        broadcast_parts = []

        for w, id in zip(wildcard_parts, id_parts):
            broadcast_part = str(int(w) + int(id))
            broadcast_parts.append(broadcast_part)

        broadcast = ".".join(broadcast_parts)
        return broadcast
#aki apenas redireciona  o  local que vai  ser salvo o arqivo txt e as informações que serão atribuidas.
    desktop_path = os.path.expanduser('~/Desktop')

    # Nome do arquivo baseado no endereço IP
    filename = f"{ip.replace('/', '_')}.txt"

    # Caminho completo do arquivo
    file_path = os.path.join(desktop_path, filename)

    try:
        # Abre o arquivo para escrita e escreve as informações
        with open(file_path, 'w') as file:
            file.write("Classe de IP: {}\n".format(Classe_IP(ip)))
            file.write("Classe de Rede: {}\n".format(Classe_Rede(ip)))
            file.write("Status: {}\n".format(classe_sub_rede(ip)))
            file.write("Máscara de Sub-rede: {}\n".format(calculo_mascara(ip)))
            file.write("ID de Rede: {}\n".format(Id_da_rede(ip)))
            file.write("Wild Card: {}\n".format(wild_card()))
            file.write("Broadcast: {}\n".format(broad_cast()))

        messagebox.showinfo(
            "Sucesso", f"As informações foram salvas em:\n{file_path}")
    except Exception as e:
        messagebox.showerror(
            "Erro", f"Ocorreu um erro ao salvar o arquivo:\n{str(e)}")

#abre o arquivo na tela .
def abrir_arquivo():
    desktop_path = os.path.expanduser('~/Desktop')
    filename = f"{ip_entry.get().replace('/', '_')}.txt"
    file_path = os.path.join(desktop_path, filename)

    try:
        with open(file_path, 'r') as file:
            content = file.read()
            info_text.delete(1.0, tk.END)  # Limpa o widget de texto
            # Insere o conteúdo do arquivo no widget de texto
            info_text.insert(tk.END, content)
    except Exception as e:
        messagebox.showerror(
            "Erro", f"Ocorreu um erro ao abrir o arquivo:\n{str(e)}")


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

#sistema em Beta(1.0.0)
#Desenvolvido  By: Buehno :)
#contato:  https://linktr.ee/Ronaldo.Bueeno