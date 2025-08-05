#!/usr/bin/env python3
"""
Conversor de resultados de pruebas JSON a HTML
Genera una página HTML visualmente atractiva a partir de los datos de pruebas
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def convert_json_to_html(json_data):
    """
    Convierte datos JSON de pruebas a HTML
    
    Args:
        json_data (dict): Datos de pruebas en formato JSON
        
    Returns:
        str: Código HTML completo
    """
    
    # Determinar el color del estado
    status_color = "#10b981" if json_data.get("success", False) else "#ef4444"
    status_text = "Exitoso" if json_data.get("success", False) else "Fallido"
    
    # Verificar si no hay pruebas ejecutadas
    total_tests = json_data.get("total_tests", 0)
    no_tests_message = "" if total_tests > 0 else "<div class='no-tests'>⚠️ No se han ejecutado pruebas en esta sesión.</div>"
    
    # Obtener datos de categorías
    categories = json_data.get("categories", {})
    unit_tests = categories.get("unit_tests", {"passed": 0, "failed": 0, "skipped": 0, "tests": []})
    integration_tests = categories.get("integration_tests", {"passed": 0, "failed": 0, "skipped": 0, "tests": []})
    
    # Generar listas de tests
    def generate_test_list(tests):
        if not tests:
            return "<li>No hay tests en esta categoría</li>"
        return "\n".join([f"<li>{test}</li>" for test in tests])
    
    unit_test_list = generate_test_list(unit_tests.get("tests", []))
    integration_test_list = generate_test_list(integration_tests.get("tests", []))
    
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resumen de Pruebas</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: {status_color};
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .status {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .no-tests {{
            background: #fef3cd;
            border: 1px solid #fecba1;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 20px;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section h2 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.5rem;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .metric-value {{
            font-weight: bold;
            font-size: 1.1rem;
        }}
        
        .passed {{
            color: #10b981;
        }}
        
        .failed {{
            color: #ef4444;
        }}
        
        .skipped {{
            color: #f59e0b;
        }}
        
        .test-list {{
            max-height: 200px;
            overflow-y: auto;
            background: #f8f9fa;
            border-radius: 5px;
            padding: 10px;
        }}
        
        .test-list ul {{
            list-style-type: none;
        }}
        
        .test-list li {{
            padding: 5px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .test-list li:last-child {{
            border-bottom: none;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
        
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .container {{
                margin: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Resumen de Pruebas</h1>
            <div class="status">Estado: {status_text}</div>
            <div class="status">Fecha: {json_data.get('timestamp', 'No disponible')}</div>
        </div>
        
        <div class="content">
            {no_tests_message}
            
            <div class="section">
                <h2>Resumen General</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Métrica</th>
                            <th>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Total de Pruebas</td>
                            <td class="metric-value">{json_data.get('total_tests', 0)}</td>
                        </tr>
                        <tr>
                            <td>Pruebas Exitosas</td>
                            <td class="metric-value passed">{json_data.get('passed_tests', 0)}</td>
                        </tr>
                        <tr>
                            <td>Pruebas Fallidas</td>
                            <td class="metric-value failed">{json_data.get('failed_tests', 0)}</td>
                        </tr>
                        <tr>
                            <td>Pruebas Omitidas</td>
                            <td class="metric-value skipped">{json_data.get('skipped_tests', 0)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="grid">
                <div class="section">
                    <h2>Pruebas Unitarias</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Estado</th>
                                <th>Cantidad</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Exitosas</td>
                                <td class="metric-value passed">{unit_tests.get('passed', 0)}</td>
                            </tr>
                            <tr>
                                <td>Fallidas</td>
                                <td class="metric-value failed">{unit_tests.get('failed', 0)}</td>
                            </tr>
                            <tr>
                                <td>Omitidas</td>
                                <td class="metric-value skipped">{unit_tests.get('skipped', 0)}</td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="test-list">
                        <h3>Lista de Tests:</h3>
                        <ul>
                            {unit_test_list}
                        </ul>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Pruebas de Integración</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Estado</th>
                                <th>Cantidad</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Exitosas</td>
                                <td class="metric-value passed">{integration_tests.get('passed', 0)}</td>
                            </tr>
                            <tr>
                                <td>Fallidas</td>
                                <td class="metric-value failed">{integration_tests.get('failed', 0)}</td>
                            </tr>
                            <tr>
                                <td>Omitidas</td>
                                <td class="metric-value skipped">{integration_tests.get('skipped', 0)}</td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="test-list">
                        <h3>Lista de Tests:</h3>
                        <ul>
                            {integration_test_list}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_content


def main():
    """
    Función principal para ejecutar el conversor desde línea de comandos
    """
    if len(sys.argv) != 3:
        print("Uso: python json_to_html_converter.py <archivo_json> <archivo_html_salida>")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    html_file = Path(sys.argv[2])
    
    if not json_file.exists():
        print(f"Error: El archivo {json_file} no existe")
        sys.exit(1)
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        html_content = convert_json_to_html(json_data)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML generado exitosamente: {html_file}")
        
    except json.JSONDecodeError as e:
        print(f"Error al leer el archivo JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()