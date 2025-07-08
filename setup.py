import subprocess
import sys
import os

REQUIREMENTS = [
    "PyMuPDF>=1.23.0",
    "openai>=1.0.0",
    "lxml>=4.9.0",
    "pyinstaller"
]

def install_requirements():
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    print(f"Installazione delle librerie da {req_file} ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])

def set_openai_api_key():
    api_key = input("Inserisci la tua OpenAI API Key: ").strip()
    if api_key:
        with open(".env", "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print("API Key salvata nel file .env.")
    else:
        print("Nessuna API Key inserita. Procedura interrotta.")
        sys.exit(1)

def build_executable():
    print("Generazione dell'eseguibile...")
    subprocess.check_call([
        "pyinstaller",
        "--onefile",
        "--name", "ai_parser",
        "ai_parser.py"
    ])
    print("Eseguibile generato nella cartella dist/.")

if __name__ == "__main__":
    install_requirements()
    set_openai_api_key()
    build_executable()