import { useEffect, useRef } from "react";
import EditorJS from "@editorjs/editorjs";

import Header from "@editorjs/header";
import List from "@editorjs/list";
import Quote from "@editorjs/quote";
import Code from "@editorjs/code";
import Delimiter from "@editorjs/delimiter";
import Paragraph from "@editorjs/paragraph";
import InlineCode from "@editorjs/inline-code";
import Underline from "@editorjs/underline";

type Props = {
  data?: any;
  onChange: (data: any) => void;
};

export const DealReportEditor = ({
  data,
  onChange,
}: Props) => {
  const editorRef = useRef<EditorJS | null>(
    null
  );

  useEffect(() => {
    if (editorRef.current) {
      return;
    }

    const editor = new EditorJS({
      holder: "editorjs",

      data,

      async onChange(api) {
        const saved = await api.saver.save();

        onChange(saved);
      },

      tools: {
        header: Header,
        list: List,
        quote: Quote,
        code: Code,
        delimiter: Delimiter,
        paragraph: Paragraph,
        inlineCode: InlineCode,
        underline: Underline,
      },
    });

    editorRef.current = editor;

    return () => {
      editor.destroy();
      editorRef.current = null;
    };
  }, []);

  return (
    <div
      id="editorjs"
      className="bg-white text-black rounded-2xl p-4"
    />
  );
};