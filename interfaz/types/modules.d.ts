declare module 'react' {
  export = React;
  export as namespace React;
  namespace React {
    interface Component<P = {}, S = {}, SS = any> {}
    interface ComponentClass<P = {}, S = {}> {}
    interface FunctionComponent<P = {}> {}
    interface ReactElement<P = any, T extends string | JSXElementConstructor<any> = string | JSXElementConstructor<any>> {}
    type JSXElementConstructor<P> = ((props: P) => ReactElement<any, any> | null) | (new (props: P) => Component<any, any>);
    function createElement<P extends {}>(type: FunctionComponent<P> | ComponentClass<P> | string, props?: (P & { children?: ReactNode }) | null, ...children: ReactNode[]): ReactElement<P>;
    type ReactNode = ReactElement | string | number | ReactFragment | ReactPortal | boolean | null | undefined;
    type ReactFragment = {} | ReactNodeArray;
    interface ReactNodeArray extends Array<ReactNode> {}
    type ReactPortal = any;
    const Fragment: any;
    const StrictMode: any;
    function useState<S>(initialState: S | (() => S)): [S, (value: S | ((prevState: S) => S)) => void];
    function useEffect(effect: () => void | (() => void), deps?: any[]): void;
    function useRef<T>(initialValue: T): { current: T };
    function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;
    function useMemo<T>(factory: () => T, deps: any[]): T;
    function createContext<T>(defaultValue: T): any;
    function useContext<T>(context: any): T;
    function forwardRef<T, P = {}>(render: (props: P, ref: any) => ReactElement | null): any;
    interface Ref<T> {}
    interface ButtonHTMLAttributes<T> { [key: string]: any; }
    interface HTMLAttributes<T> { [key: string]: any; }
    interface DetailedHTMLProps<E, T> extends E { [key: string]: any; }
    interface InputHTMLAttributes<T> extends HTMLAttributes<T> { [key: string]: any; }
    interface TextareaHTMLAttributes<T> extends HTMLAttributes<T> { [key: string]: any; }
    interface FormHTMLAttributes<T> extends HTMLAttributes<T> { [key: string]: any; }
    interface LiHTMLAttributes<T> extends HTMLAttributes<T> { [key: string]: any; }
    interface ImgHTMLAttributes<T> extends HTMLAttributes<T> { [key: string]: any; }
    interface AnchorHTMLAttributes<T> extends HTMLAttributes<T> { [key: string]: any; }
    type FC<P = {}> = FunctionComponent<P>;
    type ComponentType<P = {}> = ComponentClass<P> | FunctionComponent<P>;
    interface ChangeEvent<T = Element> {
      target: T;
    }
    interface KeyboardEvent<T = Element> {
      key: string;
      preventDefault(): void;
    }
  }
  export const StrictMode: any;
  export interface DetailedHTMLProps<T, U> {
    [key: string]: any;
  }
  export interface InputHTMLAttributes<T> {
    [key: string]: any;
  }
  export interface TextareaHTMLAttributes<T> {
    [key: string]: any;
  }
  export interface FormHTMLAttributes<T> {
    [key: string]: any;
  }
  export interface LiHTMLAttributes<T> {
    [key: string]: any;
  }
  export interface ImgHTMLAttributes<T> {
    [key: string]: any;
  }
  export interface AnchorHTMLAttributes<T> {
    [key: string]: any;
  }
  export type ComponentType<P = {}> = any;
  export interface ChangeEvent<T = Element> {
    target: T;
  }
  export interface KeyboardEvent<T = Element> {
    key: string;
    preventDefault(): void;
  }
  export interface ReactElement<P = any, T = any> {
    type: T;
    props: P;
    key: any;
  }
  export interface ReactNode {}
  export interface Component<P = {}, S = {}> {
    props: P;
    state: S;
    render(): ReactNode;
  }
  export interface FC<P = {}> {
    (props: P): ReactElement | null;
  }
  export interface FunctionComponent<P = {}> {
    (props: P): ReactElement | null;
  }
  const _default: any;
  export default _default;
}

declare module 'framer-motion' {
  export interface MotionProps {
    [key: string]: any;
  }
  
  export const motion: {
    [K in keyof JSX.IntrinsicElements]: any;
  };
  
  export const AnimatePresence: any;
  export const LazyMotion: any;
  export const domAnimation: any;
  export function useAnimation(): any;
  export function useMotionValue(initialValue: any): any;
  export function useTransform(value: any, from: any, to: any): any;
  export function useViewportScroll(): any;
  export function useSpring(value: any): any;
  export function useInView(options?: any): any;
  export function useScroll(): any;
  export function useCycle(...args: any[]): any;
  export function usePresence(): any;
  export function useReducedMotion(): any;
  export function useWillChange(): any;
  export function useVelocity(value: any): any;
  export function useTime(): any;
  export function useMotionTemplate(...args: any[]): any;
  export function useIsPresent(): any;
  export function useElementScroll(ref: any): any;
  export function useTransformControls(): any;
  export function useSpring(value: any, springConfig?: any): any;
  export function useMotionValueEvent(value: any, event: any, callback: any): any;
  export function useAnimate(): any;
  export function useAnimationControls(): any;
  export function useForceUpdate(): any;
  export function useInstantTransition(): any;
  export function useIsomorphicLayoutEffect(callback: any, deps?: any[]): any;
  export function useMotionTemplate(...args: any[]): any;
  export function useMotionValue(initialValue: any): any;
  export function usePresence(): any;
  export function useReducedMotion(): any;
  export function useScroll(): any;
  export function useSpring(value: any, springConfig?: any): any;
  export function useTime(): any;
  export function useTransform(value: any, from: any, to: any): any;
  export function useVelocity(value: any): any;
  export function useViewportScroll(): any;
  export function useWillChange(): any;
  export function useAnimationFrame(callback: any): any;
  export function useDeprecatedAnimatedState(initialState: any): any;
  export function useDeprecatedInvertedScale(scale?: any): any;
  export function useUnmountEffect(callback: any): any;
  export const wrap: any;
  export const animate: any;
  export const useAnimatedState: any;
  export const createMotionComponent: any;
  export const useInvertedScale: any;
  export const usePresence: any;
  export const useElementScroll: any;
  export const useViewportScroll: any;
  export const useIsPresent: any;
  export const useMotionValue: any;
  export const useTransform: any;
  export const useAnimation: any;
  export const useCycle: any;
  export const useSpring: any;
  export const useMotionTemplate: any;
  export const useReducedMotion: any;
  export const useWillChange: any;
  export const useVelocity: any;
  export const useTime: any;
  export const useScroll: any;
  export const useInView: any;
  export const useAnimationControls: any;
  export const useAnimate: any;
  export const useForceUpdate: any;
  export const useInstantTransition: any;
  export const useIsomorphicLayoutEffect: any;
  export const useMotionValueEvent: any;
  export const useTransformControls: any;
  export const useUnmountEffect: any;
  export const useAnimationFrame: any;
  export const useDeprecatedAnimatedState: any;
  export const useDeprecatedInvertedScale: any;
  export const AnimatePresence: any;
  export const LazyMotion: any;
  export const domAnimation: any;
  export const m: any;
  export const MotionConfig: any;
  export const MotionConfigContext: any;
  export const MotionContext: any;
  export const MotionValue: any;
  export const PresenceContext: any;
  export const Reorder: any;
  export const Variants: any;
  export const VisualElement: any;
  export const VisualElementContext: any;
  export const createDomMotionComponent: any;
  export const isValidMotionProp: any;
  export const transform: any;
  export const useMotionProps: any;
  export const useVisualElementContext: any;
  export const visualElement: any;
  export const wrapHandler: any;
  export const AnimateSharedLayout: any;
  export const LayoutGroup: any;
  export const MotionPluginContext: any;
  export const MotionPlugins: any;
  export const MotionValue: any;
  export const Presence: any;
  export const SharedLayoutContext: any;
  export const VisibilityAction: any;
  export const addScaleCorrection: any;
  export const animationControls: any;
  export const animations: any;
  export const anticipate: any;
  export const backIn: any;
  export const backInOut: any;
  export const backOut: any;
  export const bounceIn: any;
  export const bounceInOut: any;
  export const bounceOut: any;
  export const circIn: any;
  export const circInOut: any;
  export const circOut: any;
  export const createMotionComponent: any;
  export const cubicBezier: any;
  export const easeIn: any;
  export const easeInOut: any;
  export const easeOut: any;
  export const inView: any;
  export const isValidMotionProp: any;
  export const linear: any;
  export const mirrorEasing: any;
  export const mix: any;
  export const motion: any;
  export const motionValue: any;
  export const resolveMotionValue: any;
  export const reverseEasing: any;
  export const scroll: any;
  export const spring: any;
  export const stagger: any;
  export const startAnimation: any;
  export const sync: any;
  export const transform: any;
  export const useAnimatedState: any;
  export const useInvertedScale: any;
  export const usePresence: any;
  export const useElementScroll: any;
  export const useViewportScroll: any;
  export const useIsPresent: any;
  export const useMotionValue: any;
  export const useTransform: any;
  export const useAnimation: any;
  export const useCycle: any;
  export const useSpring: any;
  export const useMotionTemplate: any;
  export const useReducedMotion: any;
  export const useWillChange: any;
  export const useVelocity: any;
  export const useTime: any;
  export const useScroll: any;
  export const useInView: any;
  export const useAnimationControls: any;
  export const useAnimate: any;
  export const useForceUpdate: any;
  export const useInstantTransition: any;
  export const useIsomorphicLayoutEffect: any;
  export const useMotionValueEvent: any;
  export const useTransformControls: any;
  export const useUnmountEffect: any;
  export const useAnimationFrame: any;
  export const useDeprecatedAnimatedState: any;
  export const useDeprecatedInvertedScale: any;
  export const wrap: any;
  export const animate: any;
  export const createMotionComponent: any;
  export const m: any;
  export const MotionConfig: any;
  export const MotionConfigContext: any;
  export const MotionContext: any;
  export const MotionValue: any;
  export const PresenceContext: any;
  export const Reorder: any;
  export const Variants: any;
  export const VisualElement: any;
  export const VisualElementContext: any;
  export const createDomMotionComponent: any;
  export const isValidMotionProp: any;
  export const transform: any;
  export const useMotionProps: any;
  export const useVisualElementContext: any;
  export const visualElement: any;
  export const wrapHandler: any;
  export const AnimateSharedLayout: any;
  export const LayoutGroup: any;
  export const MotionPluginContext: any;
  export const MotionPlugins: any;
  export const MotionValue: any;
  export const Presence: any;
  export const SharedLayoutContext: any;
  export const VisibilityAction: any;
  export const addScaleCorrection: any;
  export const animationControls: any;
  export const animations: any;
  export const anticipate: any;
  export const backIn: any;
  export const backInOut: any;
  export const backOut: any;
  export const bounceIn: any;
  export const bounceInOut: any;
  export const bounceOut: any;
  export const circIn: any;
  export const circInOut: any;
  export const circOut: any;
  export const createMotionComponent: any;
  export const cubicBezier: any;
  export const easeIn: any;
  export const easeInOut: any;
  export const easeOut: any;
  export const inView: any;
  export const isValidMotionProp: any;
  export const linear: any;
  export const mirrorEasing: any;
  export const mix: any;
  export const motionValue: any;
  export const resolveMotionValue: any;
  export const reverseEasing: any;
  export const scroll: any;
  export const spring: any;
  export const stagger: any;
  export const startAnimation: any;
  export const sync: any;
}

declare module 'lucide-react' {
  export const Search: any;
  export const MessageCircle: any;
  export const Zap: any;
  export const Shield: any;
  export const BarChart3: any;
  export const Users: any;
  export const Clock: any;
  export const CheckCircle: any;
  export const ArrowRight: any;
  export const Play: any;
  export const Volume2: any;
  export const Send: any;
  export const User: any;
  export const Bot: any;
  export const Sun: any;
  export const Moon: any;
  export const Menu: any;
  export const X: any;
  export const Github: any;
  export const Twitter: any;
  export const Linkedin: any;
  export const Mail: any;
  export const MessageSquare: any;
  export const Sparkles: any;
  export const ChevronDown: any;
  export const Minimize2: any;
  export const Maximize2: any;
  export const Loader2: any;
  export const Brain: any;
  export type LucideIcon = any;
  export interface LucideProps {
    size?: string | number;
    color?: string;
    strokeWidth?: string | number;
  }
  const _default: { [key: string]: any };
  export default _default;
}

declare module '@radix-ui/react-slot' {
  export const Slot: React.ComponentType<any>;
  export const Slottable: React.ComponentType<any>;
}

declare module 'class-variance-authority' {
  export function cva(...args: any[]): any;
  export type VariantProps<T> = any;
}

declare module 'react/jsx-runtime' {
  export function jsx(type: any, props: any, key?: any): any;
  export function jsxs(type: any, props: any, key?: any): any;
  export function Fragment(props: { children?: any }): any;
  export namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
    interface Element {
      type: any;
      props: any;
      key: any;
    }
  }
}

declare module 'react/jsx-dev-runtime' {
  export function jsx(type: any, props: any, key?: any): any;
  export function jsxs(type: any, props: any, key?: any): any;
  export function Fragment(props: { children?: any }): any;
}

declare module 'react-dom' {
  export function render(element: any, container: any): void;
  export function createRoot(container: any): any;
}

declare module 'react-dom/client' {
  export function createRoot(container: Element | DocumentFragment): {
    render(children: any): void;
    unmount(): void;
  };
  export function hydrateRoot(container: Element | Document, initialChildren: any): any;
}

declare module '@vite/client' {
  export interface ViteHotContext {
    readonly data: any;
    accept(): void;
    accept(cb: (mod: any) => void): void;
    accept(dep: string, cb: (mod: any) => void): void;
    accept(deps: readonly string[], cb: (mods: any[]) => void): void;
    dispose(cb: (data: any) => void): void;
    decline(): void;
    invalidate(): void;
    on<T extends string>(event: T, cb: (data: any) => void): void;
  }
  export const hot: ViteHotContext;
}

declare module 'vite/client' {
  interface ImportMetaEnv {
    readonly VITE_APP_TITLE: string;
    readonly BASE_URL: string;
    readonly MODE: string;
    readonly DEV: boolean;
    readonly PROD: boolean;
    readonly SSR: boolean;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
    readonly hot?: {
      readonly data: any;
      accept(): void;
      accept(cb: (mod: any) => void): void;
      accept(dep: string, cb: (mod: any) => void): void;
      accept(deps: readonly string[], cb: (mods: any[]) => void): void;
      dispose(cb: (data: any) => void): void;
      decline(): void;
      invalidate(): void;
      on<T extends string>(event: T, cb: (data: any) => void): void;
    };
  }
}

declare module './ui/button' {
  export const Button: any;
  export const buttonVariants: any;
  export type ButtonProps = any;
}

declare module '../ui/button' {
  export const Button: any;
  export const buttonVariants: any;
  export type ButtonProps = any;
}

declare module 'react-hook-form' {
  export function useForm(): any;
  export const Controller: any;
  export type FieldValues = any;
  export type Control<T = FieldValues> = any;
}

declare module '@lottiefiles/react-lottie-player' {
  export const Player: any;
}

declare module 'tailwind-merge' {
  export function cn(...args: any[]): string;
  export function twMerge(...inputs: any[]): string;
}

declare module 'clsx' {
  export type ClassValue = string | number | boolean | undefined | null | ClassArray | ClassDictionary;
  export interface ClassDictionary {
    [id: string]: any;
  }
  export interface ClassArray extends Array<ClassValue> {}
  export function clsx(...inputs: ClassValue[]): string;
  export default function clsx(...inputs: ClassValue[]): string;
}

declare module './ui' {
  export const Button: any;
}

declare module '../ui' {
  export const Button: any;
}

declare module './ui/button' {
  export const Button: any;
  export const buttonVariants: any;
  export type ButtonProps = any;
}

declare module '../ui/button' {
  export const Button: any;
  export const buttonVariants: any;
  export type ButtonProps = any;
}