# Funcionalidad de Temperatura Dinámica

## Descripción

He implementado un sistema de temperatura dinámica que ajusta automáticamente la creatividad del modelo de IA basado en el tipo de consulta que envías. Esto te permite obtener respuestas más precisas para preguntas científicas o más creativas para sesiones de lluvia de ideas.

## Características Implementadas

### 1. Tipos de Consulta Automáticos

- **Scientific (Científica)**: Temperatura 0.1
  - Para preguntas que requieren respuestas precisas y factuales
  - Ideal para explicaciones técnicas, datos científicos, análisis detallados
  - Minimiza la "alucinación" del modelo

- **Creative (Creativa)**: Temperatura 1.3
  - Para sesiones de lluvia de ideas y pensamiento creativo
  - Genera respuestas más variadas e innovadoras
  - Perfecto para brainstorming, ideas de productos, soluciones creativas

- **General**: Temperatura 0.7
  - Equilibrio entre precisión y creatividad
  - Para consultas cotidianas y conversaciones normales

### 2. Control Manual de Temperatura

- **Temperatura Personalizada**: Rango 0.0 - 2.0
  - Puedes especificar manualmente la temperatura si necesitas un control más fino
  - Sobrescribe la temperatura automática del tipo de consulta
  - Accesible a través del panel "Advanced" en la interfaz

## Archivos Modificados

### Backend

1. **`app/routers/chat.py`**
   - Agregado soporte para `query_type` y `temperature` en el modelo `Msg`
   - Implementada lógica de mapeo automático de temperatura
   - Validación de temperatura entre 0 y 2

2. **`scripts/groq_client.py`**
   - Modificado `chat_completion()` para aceptar parámetro de temperatura
   - La temperatura se pasa directamente a la API de Groq

3. **`src/types/index.ts`**
   - Agregado tipo `QueryType` para TypeScript
   - Actualizada interfaz `ChatContextType` para incluir nuevos parámetros

### Frontend

4. **`src/context/ChatContext.tsx`**
   - Actualizado `sendMessage()` para enviar `query_type` y `temperature`
   - Corregida la respuesta del API (de `response` a `answer`)

5. **`src/components/forms/ChatWidget.tsx`**
   - Agregada interfaz de selección de tipo de consulta
   - Panel avanzado para temperatura personalizada
   - Chips de sugerencias actualizados con tipos específicos
   - Adaptado para usar el contexto de chat real

## Cómo Usar

### Interfaz Web (React)

1. **Selección Automática**:
   - Elige el tipo de consulta en el dropdown: "General", "Scientific", o "Creative"
   - El sistema aplicará automáticamente la temperatura apropiada

2. **Control Manual**:
   - Haz clic en "Advanced" para mostrar opciones avanzadas
   - Ingresa un valor de temperatura entre 0.0 y 2.0
   - Deja vacío para usar la temperatura automática del tipo de consulta

3. **Chips de Sugerencias**:
   - Los chips ahora están categorizados por tipo
   - Al hacer clic, automáticamente seleccionan el tipo apropiado

### API Directa

```json
{
  "prompt": "Tu pregunta aquí",
  "query_type": "scientific",  // opcional: "scientific", "creative", "general"
  "temperature": 0.5           // opcional: sobrescribe el tipo automático
}
```

## Ejemplos de Uso

### Consulta Científica (Temperatura 0.1)
```
Tipo: Scientific
Pregunta: "Explica el principio de incertidumbre de Heisenberg"
Resultado: Respuesta precisa y factual con mínima variación
```

### Consulta Creativa (Temperatura 1.3)
```
Tipo: Creative
Pregunta: "Dame 10 ideas innovadoras para una app móvil"
Resultado: Ideas variadas, originales y creativas
```

### Consulta General (Temperatura 0.7)
```
Tipo: General
Pregunta: "¿Cómo puedo mejorar mi productividad?"
Resultado: Respuesta equilibrada entre precisión y creatividad
```

## Configuración del Servidor

El servidor backend está configurado para:
- **Puerto**: 8000
- **Modelo**: compound-beta (incluye DeepSeek, Meta, y otros)
- **API**: Groq con streaming habilitado
- **Temperatura**: Dinámica basada en tipo de consulta

## Próximos Pasos

1. **Instalar Node.js** para ejecutar el frontend React
2. **Ejecutar `npm install`** para instalar dependencias del frontend
3. **Ejecutar `npm run dev`** para iniciar el servidor de desarrollo
4. **Probar la funcionalidad** en http://localhost:5173

## Estado Actual

✅ **Backend**: Funcionando en http://localhost:8000
✅ **Temperatura Dinámica**: Implementada y funcional
✅ **API**: Probada y operativa
⏳ **Frontend**: Requiere instalación de Node.js

La funcionalidad está completamente implementada y lista para usar. Solo necesitas instalar Node.js para probar la interfaz completa de React.