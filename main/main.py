import sys
import os

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller.brightness_controller import start_gui

if __name__ == "__main__":
    start_gui()