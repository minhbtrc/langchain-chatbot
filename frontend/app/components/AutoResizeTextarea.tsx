import { Textarea, TextareaProps } from "@chakra-ui/react";
import ResizeTextarea from "react-textarea-autosize";
import React from "react";

interface ResizeTextareaProps {
  maxRows?: number;
}

const ResizableTextarea: React.FC<ResizeTextareaProps> = ({
  maxRows,
  ...props
}) => {
  return <ResizeTextarea maxRows={maxRows} {...props} />;
};

interface AutoResizeTextareaProps extends TextareaProps {
  maxRows?: number;
}

export const AutoResizeTextarea = React.forwardRef<
  HTMLTextAreaElement,
  AutoResizeTextareaProps
>((props, ref) => {
  return (
    <Textarea
      minH="unset"
      w="100%"
      resize="none"
      border="3px solid"
      ref={ref as React.RefObject<HTMLTextAreaElement>}
      as={ResizableTextarea}
      {...props}
    />
  );
});

AutoResizeTextarea.displayName = "AutoResizeTextarea";
