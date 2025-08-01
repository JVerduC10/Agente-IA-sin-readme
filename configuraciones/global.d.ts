declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
      div: any;
      button: any;
      input: any;
      textarea: any;
      form: any;
      span: any;
      p: any;
      h1: any;
      h2: any;
      h3: any;
      img: any;
      a: any;
      ul: any;
      li: any;
      nav: any;
      header: any;
      footer: any;
      section: any;
      main: any;
    }
    interface Element extends React.ReactElement<any, any> { }
    interface ElementClass extends React.Component<any> {
      render(): React.ReactNode;
    }
    interface ElementAttributesProperty {
      props: {};
    }
    interface ElementChildrenAttribute {
      children: {};
    }
    type LibraryManagedAttributes<C, P> = P;
  }

  interface Window {
    [key: string]: any;
  }

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
}

export {};