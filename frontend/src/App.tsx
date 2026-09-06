import { AppShell, Box } from '@mantine/core';
import { useState, useRef, useEffect } from 'react';
import { useChat } from './hooks/useChat';
import ChatWindow from './components/ChatWindow';
import InputArea from './components/UserInput';
import Header from './components/layout/Header';
import { fetchQuickQuestions } from './services/chatApi';
import './App.css';

export default function App() {
  const [input, setInput] = useState('');
  const [questions, setQuestions] = useState<string[] | undefined>(undefined);
  const { messages, sendMessage, isLoading } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);
  const isInitialState = messages.length === 0;

  useEffect(() => {
    let isMounted = true;
    fetchQuickQuestions().then((fetched) => {
      if (isMounted && fetched.length > 0) {
        setQuestions(fetched);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
  };

  const lastMessage = messages[messages.length - 1];
  const showTyping = isLoading && (!lastMessage || lastMessage.role === 'user');

  return (
    <AppShell
      header={{ height: 60 }}
      styles={{
        main: {
          display: 'flex',
          flexDirection: 'column',
          height: '100dvh',
          padding: 0,
          paddingTop: 60,
          boxSizing: 'border-box',
        },
      }}
    >
      <Header />

      <AppShell.Main>
        <Box
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflowY: isInitialState ? 'auto' : 'hidden',
            padding: '1rem 0',
            boxSizing: 'border-box',
          }}
        >
          {isInitialState && <Box style={{ flexGrow: 1, minHeight: 0 }} />}

          {!isInitialState && (
            <ChatWindow messages={messages} showTyping={showTyping} scrollRef={scrollRef} />
          )}

          <Box w="100%" style={{ flexShrink: 0 }}>
            <InputArea
              input={input}
              setInput={setInput}
              onSend={handleSend}
              isLoading={isLoading}
              isInitial={isInitialState}
              onQuickQuestion={sendMessage}
              questions={questions}
            />
          </Box>

          {isInitialState && <Box style={{ flexGrow: 1, minHeight: 0 }} />}
        </Box>
      </AppShell.Main>
    </AppShell>
  );
}
