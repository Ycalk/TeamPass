/// <reference types="vite/client" />

declare module '@editorjs/editorjs' {
    export default class EditorJS {
        constructor(config?: any);
        destroy(): Promise<void>;
        save(): Promise<any>;
        clear(): Promise<void>;
        render(data: any): Promise<void>;
        isReady: Promise<void>;
    }
}

declare module '@editorjs/header' {
    const Header: any;
    export default Header;
}

declare module '@editorjs/list' {
    const List: any;
    export default List;
}

declare module '@editorjs/quote' {
    const Quote: any;
    export default Quote;
}

declare module '@editorjs/code' {
    const Code: any;
    export default Code;
}

declare module '@editorjs/delimiter' {
    const Delimiter: any;
    export default Delimiter;
}

declare module '@editorjs/paragraph' {
    const Paragraph: any;
    export default Paragraph;
}

declare module '@editorjs/inline-code' {
    const InlineCode: any;
    export default InlineCode;
}

declare module '@editorjs/underline' {
    const Underline: any;
    export default Underline;
}
