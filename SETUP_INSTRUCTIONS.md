# Instrucciones de Configuración

## Problema Actual
El proyecto tiene errores de TypeScript porque las dependencias de Node.js no están instaladas. Los errores que ves son:

- Cannot find module 'react'
- Cannot find module 'framer-motion' 
- Cannot find module 'lucide-react'
- Cannot find module 'next/dynamic'

## Solución

### 1. Instalar Node.js
Primero necesitas instalar Node.js en tu sistema:

1. Ve a https://nodejs.org/
2. Descarga la versión LTS (recomendada)
3. Ejecuta el instalador y sigue las instrucciones
4. Reinicia tu terminal/IDE después de la instalación

### 2. Verificar la instalación
Después de instalar Node.js, verifica que esté correctamente instalado:

```bash
node --version
npm --version
```

### 3. Instalar dependencias del proyecto
Una vez que Node.js esté instalado, ejecuta:

```bash
npm install
```

Esto instalará todas las dependencias listadas en `package.json`:
- react
- framer-motion
- lucide-react
- Y todas las demás dependencias necesarias

### 4. Ejecutar el proyecto
Después de instalar las dependencias:

```bash
npm run dev
```

## Dependencias del Proyecto
El proyecto usa las siguientes tecnologías principales:
- React 18.2.0
- TypeScript
- Vite (build tool)
- Framer Motion (animaciones)
- Lucide React (iconos)
- Tailwind CSS (estilos)

## Notas Adicionales
- El archivo `package.json` ya tiene todas las dependencias correctamente definidas
- La configuración de TypeScript en `tsconfig.json` está correcta
- Solo falta instalar Node.js y las dependencias para resolver los errores