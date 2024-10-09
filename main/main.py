import sys
import os
import subprocess
import signal
import atexit
from tkinter import Tk

# Adicionar o caminho do diretório pai ao sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from controller.brightness_controller import start_gui

# Variável para armazenar o processo do PowerShell
powershell_process = None

def start_powershell():
    global powershell_process
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "controller", "adjust_brightness.ps1")
    print(f"Iniciando o PowerShell com o script: {script_path}")
    powershell_process = subprocess.Popen(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Processo do PowerShell iniciado com PID: {powershell_process.pid}")

def stop_powershell():
    global powershell_process
    if powershell_process:
        print(f"Tentando finalizar o processo do PowerShell com PID: {powershell_process.pid}")
        powershell_process.terminate()
        try:
            powershell_process.wait(timeout=5)
            print(f"Processo do PowerShell com PID {powershell_process.pid} finalizado com sucesso.")
        except subprocess.TimeoutExpired:
            print(f"Tempo expirado. Forçando o término do processo com PID: {powershell_process.pid}")
            os.kill(powershell_process.pid, signal.SIGKILL)
            print(f"Processo do PowerShell com PID {powershell_process.pid} foi finalizado à força.")
        powershell_process = None
    else:
        print("Nenhum processo do PowerShell está em execução para ser finalizado.")

# Garantir que o PowerShell será finalizado ao encerrar o programa
atexit.register(stop_powershell)

def on_window_close():
    """ Função chamada ao fechar a janela do Tkinter """
    print("Janela do Tkinter foi fechada. Encerrando a aplicação e o PowerShell.")
    stop_powershell()
    root.quit()  # Fecha a janela do Tkinter
    root.destroy()  # Destroi a janela do Tkinter
    os._exit(0)  # Encerra o programa principal

if __name__ == "__main__":
    # Iniciar o PowerShell ao iniciar o aplicativo
    start_powershell()

    # Iniciar a interface gráfica e garantir que ao encerrar a janela o PowerShell seja finalizado
    root = Tk()  # Cria uma janela temporária do Tkinter para capturar eventos de fechamento
    root.protocol("WM_DELETE_WINDOW", on_window_close)  # Captura o evento de fechamento da janela

    start_gui(root)  # Passar o root para ser utilizado pelo controller
