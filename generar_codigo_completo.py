#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar un archivo con todo el código del proyecto
para subirlo a ChatGPT de manera organizada.
"""

import os
import datetime
from pathlib import Path

def should_include_file(filepath):
    """Determina si un archivo debe incluirse en el resumen."""
    # Extensiones de archivos a incluir
    include_extensions = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html', '.md', 
        '.txt', '.json', '.yml', '.yaml', '.toml', '.ini', '.env.example'
    }
    
    # Directorios a excluir
    exclude_dirs = {
        '__pycache__', '.pytest_cache', 'node_modules', '.git', 
        '.vscode', '.idea', 'dist', 'build', '.next', 'coverage'
    }
    
    # Archivos específicos a excluir
    exclude_files = {
        '.env', '.env.admin', 'chroma.sqlite3', '.gitignore'
    }
    
    path = Path(filepath)
    
    # Verificar si está en un directorio excluido
    for part in path.parts:
        if part in exclude_dirs:
            return False
    
    # Verificar archivos específicos excluidos
    if path.name in exclude_files:
        return False
    
    # Verificar extensión
    return path.suffix in include_extensions

def generar_resumen_proyecto():
    """Genera un archivo con todo el código del proyecto."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"codigo_completo_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Escribir encabezado
        f.write("=" * 80 + "\n")
        f.write("CÓDIGO COMPLETO DEL PROYECTO\n")
        f.write(f"Generado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # Escribir estructura del proyecto
        f.write("ESTRUCTURA DEL PROYECTO:\n")
        f.write("-" * 40 + "\n")
        
        # Generar árbol de directorios
        for root, dirs, files in os.walk('.'):
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if d not in {'__pycache__', '.pytest_cache', 'node_modules', '.git'}]
            
            level = root.replace('.', '').count(os.sep)
            indent = '  ' * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            
            subindent = '  ' * (level + 1)
            for file in files:
                if should_include_file(os.path.join(root, file)):
                    f.write(f"{subindent}{file}\n")
        
        f.write("\n" + "=" * 80 + "\n\n")
        
        # Archivos principales primero
        priority_files = [
            'readme.md',
            'configuraciones/requirements.txt',
            'servidor/main.py',
            'servidor/settings.py',
            'servidor/routers/chat.py',
            'herramientas/model_manager.py',
            'herramientas/groq_client.py',
            'herramientas/bing_client.py'
        ]
        
        # Escribir archivos prioritarios
        f.write("ARCHIVOS PRINCIPALES:\n")
        f.write("=" * 80 + "\n\n")
        
        for priority_file in priority_files:
            if os.path.exists(priority_file):
                escribir_archivo(f, priority_file)
        
        # Escribir resto de archivos
        f.write("\n" + "=" * 80 + "\n")
        f.write("RESTO DE ARCHIVOS:\n")
        f.write("=" * 80 + "\n\n")
        
        archivos_procesados = set(priority_files)
        
        for root, dirs, files in os.walk('.'):
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if d not in {'__pycache__', '.pytest_cache', 'node_modules', '.git'}]
            
            for file in files:
                filepath = os.path.join(root, file).replace('\\', '/').replace('./', '')
                
                if should_include_file(filepath) and filepath not in archivos_procesados:
                    escribir_archivo(f, filepath)
    
    print(f"\n✅ Archivo generado: {output_file}")
    print(f"📁 Tamaño: {os.path.getsize(output_file) / 1024:.1f} KB")
    print(f"\n📋 Instrucciones para ChatGPT:")
    print("1. Abre el archivo generado")
    print("2. Copia todo el contenido")
    print("3. Pégalo en ChatGPT con un mensaje como:")
    print('   "Aquí tienes el código completo de mi proyecto. ¿Puedes ayudarme a [tu pregunta]?"')
    
    return output_file

def escribir_archivo(f, filepath):
    """Escribe el contenido de un archivo al archivo de salida."""
    try:
        f.write(f"\n{'='*20} {filepath} {'='*20}\n")
        
        with open(filepath, 'r', encoding='utf-8') as code_file:
            content = code_file.read()
            
            # Limitar tamaño de archivos muy grandes
            if len(content) > 10000:  # 10KB
                f.write(f"[ARCHIVO GRANDE - Primeras 10000 caracteres]\n\n")
                content = content[:10000] + "\n\n[... contenido truncado ...]\n"
            
            f.write(content)
            
        f.write(f"\n{'='*len(filepath)+42}\n\n")
        
    except Exception as e:
        f.write(f"❌ Error leyendo archivo: {e}\n\n")

if __name__ == "__main__":
    print("🚀 Generando archivo con código completo del proyecto...")
    archivo_generado = generar_resumen_proyecto()
    print(f"\n🎉 ¡Listo! Archivo generado: {archivo_generado}")