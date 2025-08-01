# Source Code Structure

This document outlines the organized structure of the React application source code.

## Directory Structure

```
src/
├── components/          # React components organized by purpose
│   ├── common/         # Reusable components
│   │   ├── FeatureCard.tsx
│   │   └── index.ts
│   ├── forms/          # Form-related components
│   │   ├── ChatWidget.tsx
│   │   └── index.ts
│   ├── layout/         # Layout components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── index.ts
│   ├── sections/       # Page section components
│   │   ├── Hero.tsx
│   │   ├── Features.tsx
│   │   ├── VideoSection.tsx
│   │   ├── ChatSection.tsx
│   │   └── index.ts
│   ├── ui/            # Base UI components
│   │   └── button.tsx
│   └── index.ts       # Main component exports
├── constants/          # Application constants
│   └── index.ts
├── context/           # React contexts for state management
│   ├── ThemeContext.tsx
│   ├── ChatContext.tsx
│   └── index.ts
├── hooks/             # Custom React hooks
│   ├── theme/
│   │   ├── useDarkMode.ts
│   │   └── index.ts
│   └── index.ts
├── types/             # TypeScript type definitions
│   └── index.ts
├── utils/             # Utility functions
│   ├── cn.ts          # Class name utility
│   ├── format.ts      # Formatting utilities
│   ├── validation.ts  # Validation utilities
│   └── index.ts
├── App.tsx            # Main application component
├── main.tsx           # Application entry point
└── index.css          # Global styles
```

## Import Patterns

### Components
```typescript
// Import multiple components from organized structure
import { Header, Footer, Hero, Features } from './components'

// Import specific component types
import { ChatWidget } from './components/forms'
import { FeatureCard } from './components/common'
```

### Utilities
```typescript
// Import utilities
import { cn, formatDate, isValidEmail } from './utils'
```

### Contexts
```typescript
// Import contexts
import { useTheme, useChat } from './context'
```

### Types
```typescript
// Import types
import { Message, Feature, ThemeContextType } from './types'
```

### Constants
```typescript
// Import constants
import { APP_CONFIG, API_ENDPOINTS, COLORS } from './constants'
```

## Key Features

- **Organized Structure**: Components are categorized by purpose (layout, sections, forms, common, ui)
- **Centralized Exports**: Each directory has an index.ts file for clean imports
- **Type Safety**: Comprehensive TypeScript types in dedicated types directory
- **Context Management**: React contexts for theme and chat state management
- **Utility Functions**: Organized utilities for common operations
- **Constants**: Centralized application configuration and constants

## Best Practices

1. **Import from index files**: Use centralized exports for cleaner imports
2. **Follow naming conventions**: PascalCase for components, camelCase for utilities
3. **Use TypeScript types**: Import and use defined types for better type safety
4. **Leverage contexts**: Use React contexts for global state management
5. **Organize by purpose**: Keep related files together in appropriate directories
