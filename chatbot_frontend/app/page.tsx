"use client";

import { ChatWindow } from "../app/components/ChatWindow";
import { ToastContainer } from "react-toastify";
import { v4 as uuidv4 } from "uuid";
import { ChakraProvider } from "@chakra-ui/react";

export default function Home() {
  const conversationId = uuidv4();
  return (
    <ChakraProvider>
      <ToastContainer />
      <ChatWindow
        titleText="Personality Chatbot"
        conversationId={conversationId}
      ></ChatWindow>
    </ChakraProvider>
  );
}
