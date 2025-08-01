declare global {
  interface Window {
    [key: string]: any;
  }
}

// Fix for binding element errors
declare module '*.tsx' {
  const component: any;
  export default component;
}

declare module '*.ts' {
  const module: any;
  export default module;
}

// Fix for class-variance-authority
declare module 'class-variance-authority' {
  export function cva(base?: string, config?: any): (...args: any[]) => string;
  export type VariantProps<T> = any;
}

// Fix for clsx
declare module 'clsx' {
  function clsx(...args: any[]): string;
  export default clsx;
}

// Fix for tailwind-merge
declare module 'tailwind-merge' {
  export function twMerge(...args: any[]): string;
}

// Fix for react-hook-form
declare module 'react-hook-form' {
  export function useForm(options?: any): any;
  export const Controller: any;
  export type FieldValues = any;
  export type Control<T = any> = any;
}

// Fix for @lottiefiles/react-lottie-player
declare module '@lottiefiles/react-lottie-player' {
  export const Player: any;
}

// Additional React types
declare namespace React {
  type FC<P = {}> = FunctionComponent<P>;
  type PropsWithChildren<P = unknown> = P & { children?: ReactNode };
  interface HTMLAttributes<T> {
    [key: string]: any;
  }
  interface ButtonHTMLAttributes<T> extends HTMLAttributes<T> {
    [key: string]: any;
  }
  interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
    [key: string]: any;
  }
  interface TextareaHTMLAttributes<T> extends HTMLAttributes<T> {
    [key: string]: any;
  }
  interface FormHTMLAttributes<T> extends HTMLAttributes<T> {
    [key: string]: any;
  }
}

export {};