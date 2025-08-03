#!/usr/bin/env python3
"""
Script de verificación de configuración de VS Code
Verifica que todas las extensiones y configuraciones estén correctamente instaladas
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def check_vscode_installed():
    """Verifica si VS Code está instalado"""
    try:
        result = subprocess.run(['code', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"✅ VS Code instalado: {version}")
            return True
        else:
            print("❌ VS Code no encontrado")
            return False
    except FileNotFoundError:
        print("❌ VS Code no está en el PATH")
        return False


def check_extensions():
    """Verifica las extensiones instaladas"""
    required_extensions = [
        'ms-python.python',
        'ms-python.vscode-pylance',
        'sidthesloth.vscode-fastapi-snippets',
        'humao.rest-client',
        'ms-python.black-formatter',
        'ms-python.isort',
        'ritwickdey.liveserver',
        'esbenp.prettier-vscode',
        'bradlc.vscode-tailwindcss',
        'dbaeumer.vscode-eslint',
        'ms-toolsai.jupyter',
        'ms-toolsai.notebook-renderer',
        'dongli.python-pandas-snippets',
        'randomfractalsinc.vscode-data-preview',
        'anweber.httpyac',
        'foxundermoon.shell-format',
        'mikestead.dotenv',
        'yzhang.markdown-all-in-one',
        'LittleFoxTeam.vscode-python-test-adapter',
        'ms-azuretools.vscode-docker',
        'eamodio.gitlens',
        'github.copilot',
        'redhat.vscode-yaml',
        'gruntfuggly.todo-tree',
        'alefragnani.Bookmarks',
        'usernamehw.errorlens'
    ]
    
    try:
        result = subprocess.run(['code', '--list-extensions'], capture_output=True, text=True)
        if result.returncode == 0:
            installed = result.stdout.strip().split('\n')
            installed_lower = [ext.lower() for ext in installed]
            
            missing = []
            for ext in required_extensions:
                if ext.lower() not in installed_lower:
                    missing.append(ext)
                else:
                    print(f"✅ {ext}")
            
            if missing:
                print(f"\n❌ Extensiones faltantes ({len(missing)}):")
                for ext in missing:
                    print(f"   - {ext}")
                return False
            else:
                print(f"\n✅ Todas las extensiones están instaladas ({len(required_extensions)})")
                return True
        else:
            print("❌ Error al listar extensiones")
            return False
    except FileNotFoundError:
        print("❌ No se puede verificar extensiones")
        return False


def check_config_files():
    """Verifica que los archivos de configuración existan"""
    vscode_dir = Path('.vscode')
    required_files = [
        'extensions.json',
        'settings.json',
        'tasks.json',
        'launch.json',
        'api-tests.http',
        'README.md'
    ]
    
    missing = []
    for file in required_files:
        file_path = vscode_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            missing.append(file)
            print(f"❌ {file}")
    
    if missing:
        print(f"\n❌ Archivos de configuración faltantes ({len(missing)}):")
        for file in missing:
            print(f"   - {file}")
        return False
    else:
        print(f"\n✅ Todos los archivos de configuración presentes ({len(required_files)})")
        return True


def check_python_packages():
    """Verifica paquetes Python importantes"""
    important_packages = [
        'fastapi',
        'uvicorn',
        'pytest',
        'black',
        'isort',
        'flake8',
        'httpx',
        'pydantic',
        'python-dotenv'
    ]
    
    missing = []
    for package in important_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n❌ Paquetes Python faltantes ({len(missing)}):")
        for package in missing:
            print(f"   - {package}")
        print("\n💡 Instala con: pip install -r configuraciones/requirements.txt")
        return False
    else:
        print(f"\n✅ Todos los paquetes importantes están instalados ({len(important_packages)})")
        return True


def main():
    """Función principal"""
    print("🔍 Verificando configuración de VS Code para desarrollo de IA conversacional...\n")
    
    checks = [
        ("VS Code", check_vscode_installed),
        ("Archivos de configuración", check_config_files),
        ("Extensiones de VS Code", check_extensions),
        ("Paquetes Python", check_python_packages)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Verificando {name}:")
        print("-" * 50)
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    all_good = True
    for name, result in results:
        status = "✅ OK" if result else "❌ FALLO"
        print(f"{status:<8} {name}")
        if not result:
            all_good = False
    
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 ¡Configuración completa! Tu entorno está listo para desarrollo.")
        print("💡 Reinicia VS Code si no lo has hecho ya.")
    else:
        print("⚠️  Hay algunos problemas que necesitan atención.")
        print("💡 Revisa los elementos marcados con ❌ arriba.")
    
    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())