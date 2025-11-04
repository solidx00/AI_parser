import subprocess
import sys
import os
from pathlib import Path

def ensure_virtualenv(env_path: str) -> str:
    """Crea un virtualenv se non esiste e ritorna il path al suo python."""
    here = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(here, env_path)
    python_bin = os.path.join(venv_dir, "Scripts", "python.exe") if os.name == "nt" else os.path.join(venv_dir, "bin", "python")

    if not os.path.exists(python_bin):
        print(f"Creazione virtualenv in {venv_dir} ...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
    else:
        print(f"Virtualenv già presente: {venv_dir}")

    return python_bin


def install_requirements(python_exec: str):
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    print(f"Installazione delle librerie da {req_file} con {python_exec} ...")
    subprocess.check_call([python_exec, "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"]) 
    subprocess.check_call([python_exec, "-m", "pip", "install", "-r", req_file])

def set_openai_api_key():
    api_key = input("Inserisci la tua OpenAI API Key: ").strip()
    if api_key:
        with open(".env", "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print("API Key salvata nel file .env.")
    else:
        print("Nessuna API Key inserita. Procedura interrotta.")
        sys.exit(1)

def build_executables(python_exec: str):
    """Crea eseguibili standalone per ai_parser.py e ai_parser_extended.py."""
    here = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(here, "dist")
    build_dir = os.path.join(here, "build")

    # Pulisce build precedenti
    if os.path.exists(build_dir):
        print("Pulizia cartella build/ ...")
        subprocess.run(["rm", "-rf", build_dir], check=False)
    os.makedirs(dist_dir, exist_ok=True)

    targets = [
        ("ai_parser.py", "ai_parser"),
        ("ai_parser_extended.py", "ai_parser_extended"),
    ]

    for entry, name in targets:
        print(f"\n🏗️  Build eseguibile: {name}")
        cmd = [
            python_exec,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--name",
            name,
            entry,
        ]
        subprocess.check_call(cmd, cwd=here)

    print("\n✅ Build completata. Eseguibili in dist/ :")
    for _, name in targets:
        print(f" - dist/{name}{'.exe' if os.name == 'nt' else ''}")


if __name__ == "__main__":
    # 1) Crea/assicurati del virtualenv locale "myenv"
    venv_python = ensure_virtualenv("myenv")

    # 3) Installa requirements dentro il virtualenv
    install_requirements(venv_python)

    # 4) Salva la chiave OpenAI in .env nel root
    set_openai_api_key()

    # 5) Costruisci gli eseguibili usando il python del virtualenv
    build_executables(venv_python)

    print("\n🏁 Setup completato. Eseguibili in dist/. Per eseguire da terminale:")
    print("  ./dist/ai_parser")
    print("  ./dist/ai_parser_extended")