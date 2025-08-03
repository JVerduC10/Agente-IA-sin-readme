# 🛠️ Configuración de VS Code para Desarrollo de IA Conversacional

## 📋 Extensiones Instaladas

### 🐍 Python & FastAPI
- **Python** (`ms-python.python`) - Soporte completo para Python
- **Pylance** (`ms-python.vscode-pylance`) - IntelliSense avanzado
- **FastAPI Snippets** (`sidthesloth.vscode-fastapi-snippets`) - Snippets para FastAPI
- **Black Formatter** (`ms-python.black-formatter`) - Formateo automático
- **isort** (`ms-python.isort`) - Organización de imports
- **Python Test Adapter** (`LittleFoxTeam.vscode-python-test-adapter`) - Ejecutor de tests

### 🌐 Web Development & APIs
- **REST Client** (`humao.rest-client`) - Pruebas de API desde VS Code
- **httpYac** (`anweber.httpyac`) - Cliente HTTP avanzado
- **Live Server** (`ritwickdey.liveserver`) - Servidor local para desarrollo
- **Prettier** (`esbenp.prettier-vscode`) - Formateo de código web
- **Tailwind CSS** (`bradlc.vscode-tailwindcss`) - Soporte para Tailwind
- **ESLint** (`dbaeumer.vscode-eslint`) - Linting para JavaScript

### 🤖 Machine Learning & Data Science
- **Jupyter** (`ms-toolsai.jupyter`) - Notebooks interactivos
- **Notebook Renderer** (`ms-toolsai.notebook-renderer`) - Renderizado mejorado
- **Pandas Snippets** (`dongli.python-pandas-snippets`) - Snippets para Pandas
- **Data Preview** (`randomfractalsinc.vscode-data-preview`) - Vista previa de datos

### 🔧 DevOps & Utilidades
- **Docker** (`ms-azuretools.vscode-docker`) - Soporte para Docker
- **GitLens** (`eamodio.gitlens`) - Git supercharged
- **GitHub Copilot** (`github.copilot`) - IA para programación
- **YAML** (`redhat.vscode-yaml`) - Soporte para YAML
- **Shell Format** (`foxundermoon.shell-format`) - Formateo de scripts
- **DotEnv** (`mikestead.dotenv`) - Soporte para archivos .env
- **Markdown All in One** (`yzhang.markdown-all-in-one`) - Herramientas Markdown

### 🎯 Productividad
- **TODO Tree** (`gruntfuggly.todo-tree`) - Gestión de TODOs
- **Bookmarks** (`alefragnani.Bookmarks`) - Marcadores en código
- **Error Lens** (`usernamehw.errorlens`) - Errores inline

## 🚀 Tareas Configuradas

Accede a las tareas con `Ctrl+Shift+P` → "Tasks: Run Task":

- **Start FastAPI Server** - Inicia el servidor de desarrollo
- **Run Tests** - Ejecuta todas las pruebas
- **Run Tests with Coverage** - Pruebas con cobertura
- **Format Python Code** - Formatea código con Black
- **Sort Imports** - Organiza imports con isort
- **Lint Python Code** - Ejecuta flake8
- **Install Dependencies** - Instala dependencias
- **Encrypt API Keys** - Encripta claves API
- **Run Model Evaluation** - Ejecuta evaluación de modelos

## 🐛 Configuraciones de Debug

Accede con `F5` o `Ctrl+Shift+D`:

- **Debug FastAPI Server** - Debug del servidor principal
- **Debug Current Test File** - Debug del archivo de test actual
- **Debug All Tests** - Debug de todas las pruebas
- **Debug Groq Client** - Debug del cliente Groq
- **Debug Model Manager** - Debug del gestor de modelos
- **Debug Evaluation Script** - Debug del script de evaluación
- **Debug Current Python File** - Debug del archivo Python actual

## 🌐 Pruebas de API

Usa el archivo `api-tests.http` para probar endpoints:

1. Abre `.vscode/api-tests.http`
2. Haz clic en "Send Request" sobre cualquier endpoint
3. Ve los resultados en el panel lateral

### Endpoints disponibles:
- Health check
- Chat simple
- Chat científico
- Chat creativo
- Búsqueda web
- Modo competición
- Estadísticas de rendimiento
- Búsqueda RAG
- Subida de documentos

## ⚙️ Configuraciones Automáticas

### Python
- Intérprete por defecto: `./venv/Scripts/python.exe`
- Formateo automático al guardar
- Organización automática de imports
- Tests con pytest habilitados
- Directorio de tests: `pruebas/`

### Archivos
- Asociaciones automáticas para `.env`, `.yml`, `.yaml`
- Exclusión de `__pycache__`, `.pytest_cache`, `node_modules`
- Exclusión de búsqueda en `memoria_vectorial`, `base_datos`

### REST Client
- URL base configurada: `http://localhost:8002`
- Variables de entorno compartidas

## 🎨 Personalización

### TODO Tree
Busca automáticamente:
- `BUG`, `HACK`, `FIXME`, `TODO`, `XXX`
- Checkboxes: `[ ]`, `[x]`

### Error Lens
Muestra errores, warnings e info inline en el código

### GitLens
CodeLens deshabilitado por defecto (menos ruido visual)

## 🔄 Reinicio Requerido

**¡Importante!** Reinicia VS Code para aplicar todas las configuraciones y extensiones.

## 💡 Consejos de Uso

1. **Atajos útiles:**
   - `Ctrl+Shift+P` - Paleta de comandos
   - `Ctrl+Shift+E` - Explorer
   - `Ctrl+Shift+D` - Debug
   - `Ctrl+Shift+X` - Extensiones
   - `Ctrl+`` ` - Terminal

2. **Para pruebas de API:**
   - Usa `api-tests.http` para pruebas rápidas
   - Modifica la variable `@apiKey` si usas autenticación

3. **Para debugging:**
   - Pon breakpoints con `F9`
   - Inicia debug con `F5`
   - Step over con `F10`, step into con `F11`

4. **Para tests:**
   - Ejecuta tests desde la barra lateral de Testing
   - Usa `Ctrl+Shift+P` → "Python: Run All Tests"

¡Tu entorno de desarrollo está listo para construir sistemas de IA conversacional! 🚀