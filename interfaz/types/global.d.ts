/// <reference types="vite/client" />

declare global {
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
    function useState<S>(initialState: S | (() => S)): [S, (value: S | ((prevState: S) => S)) => void];
    function useEffect(effect: () => void | (() => void), deps?: any[]): void;
    function useRef<T>(initialValue: T): { current: T };
    function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;
    function useMemo<T>(factory: () => T, deps: any[]): T;
  }
  
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
    interface Element {
      type: any;
      props: any;
      key: any;
    }
    interface ElementClass {
      render(): Element | null;
    }
    interface ElementAttributesProperty {
      props: {};
    }
    interface ElementChildrenAttribute {
      children: {};
    }
    interface LibraryManagedAttributes<C, P> {
      [key: string]: any;
    }
  }
}

declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.jpeg' {
  const content: string;
  export default content;
}

declare module '*.gif' {
  const content: string;
  export default content;
}

declare module '*.webp' {
  const content: string;
  export default content;
}