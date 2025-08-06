# Conversor JSON a HTML - Resultados de Pruebas

## 📋 Descripción

Este proyecto incluye un conversor que transforma resultados de pruebas automatizadas desde formato JSON a páginas HTML visualmente atractivas y fáciles de leer.

## 🚀 Características

- ✅ **Conversión automática** de JSON a HTML
- 🎨 **Diseño responsivo** y visualmente atractivo
- 📊 **Tablas organizadas** para resumen general y categorías
- 🟢🔴 **Indicadores visuales** de éxito/fallo
- ⚠️ **Mensaje especial** cuando no hay pruebas ejecutadas
- 📱 **Compatible con dispositivos móviles**

## 📁 Archivos Incluidos

```
scripts/
├── json_to_html_converter.py  # Conversor principal
├── demo_converter.py          # Script de demostración
└── README.md                  # Esta documentación

# resultados/html_examples/ eliminado - directorio removido
├── sample_success.json        # JSON con pruebas exitosas
├── report_success.html        # HTML correspondiente
├── sample_no_tests.json       # JSON sin pruebas
├── report_no_tests.html       # HTML correspondiente
├── sample_failures.json       # JSON con fallos
└── report_failures.html       # HTML correspondiente
```

## 🔧 Uso

### Conversión Individual

```bash
# Convertir un archivo JSON específico
python scripts/json_to_html_converter.py input.json output.html
```

### Generar Ejemplos de Demostración

```bash
# Crear ejemplos con datos de prueba
python scripts/demo_converter.py
```

### Uso Programático

```python
from json_to_html_converter import convert_json_to_html
import json

# Cargar datos JSON
with open('resultados.json', 'r') as f:
    data = json.load(f)

# Convertir a HTML
html_content = convert_json_to_html(data)

# Guardar resultado
with open('reporte.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
```

## 📊 Formato JSON Esperado

El conversor espera un JSON con la siguiente estructura:

```json
{
  "timestamp": "2025-01-15T14:30:45.123456",
  "passed_tests": 15,
  "failed_tests": 1,
  "skipped_tests": 2,
  "total_tests": 18,
  "test_details": [
    "test_auth.py::test_valid_api_key",
    "test_rag.py::test_search_functionality"
  ],
  "categories": {
    "unit_tests": {
      "passed": 10,
      "failed": 1,
      "skipped": 1,
      "tests": ["lista_de_tests_unitarios"]
    },
    "integration_tests": {
      "passed": 5,
      "failed": 0,
      "skipped": 1,
      "tests": ["lista_de_tests_integracion"]
    }
  },
  "success": true
}
```

## 🎨 Características Visuales

### Indicadores de Estado
- 🟢 **Verde**: Pruebas exitosas (`success: true`)
- 🔴 **Rojo**: Pruebas fallidas (`success: false`)
- ⚠️ **Amarillo**: Advertencia cuando no hay pruebas

### Secciones del Reporte
1. **Encabezado**: Título, estado y timestamp
2. **Resumen General**: Métricas totales
3. **Pruebas Unitarias**: Estadísticas y lista detallada
4. **Pruebas de Integración**: Estadísticas y lista detallada

### Diseño Responsivo
- Diseño en columnas para pantallas grandes
- Apilamiento vertical en dispositivos móviles
- Tablas con scroll horizontal si es necesario

## 🛠️ Personalización

Puedes modificar el archivo `json_to_html_converter.py` para:

- Cambiar colores y estilos CSS
- Agregar nuevas secciones
- Modificar el formato de las tablas
- Incluir gráficos o visualizaciones adicionales

## 📝 Ejemplos de Uso

### Caso 1: Integración con CI/CD

```bash
# En tu pipeline de CI/CD
pytest --json-report --json-report-file=test_results.json
python scripts/json_to_html_converter.py test_results.json report.html
```

### Caso 2: Monitoreo Continuo

```python
# Script para generar reportes periódicos
import schedule
import time

def generate_daily_report():
    # Ejecutar pruebas y generar reporte
    os.system('pytest --json-report --json-report-file=daily_tests.json')
    os.system('python scripts/json_to_html_converter.py daily_tests.json daily_report.html')

schedule.every().day.at("09:00").do(generate_daily_report)
```

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa los cambios
4. Ejecuta las pruebas
5. Envía un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

---

**¡Disfruta creando reportes HTML hermosos y funcionales! 🎉**