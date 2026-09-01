import { AppShell, ScrollArea, Container, Stack, Box } from '@mantine/core';
import { useState, useRef, useEffect } from 'react';
import { useChat } from './hooks/useChat';
import MessageBubble from './components/MessageBubble';
import TypingIndicator from './components/TypingIndicator';
import InputArea from './components/UserInput';
import Header from './components/layout/Header';
import './App.css';

export default function App() {
  const [input, setInput] = useState('');
  const { messages, sendMessage, isLoading } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);
  const isInitialState = messages.length === 0;

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
            <ScrollArea flex={1} p="md">
              <Container size="md">
                <Stack gap="xl">
                  {messages.map((msg, i) => (
                    <MessageBubble key={i} msg={msg} />
                  ))}
                  {showTyping && <TypingIndicator />}
                  <div ref={scrollRef} />
                </Stack>
              </Container>
            </ScrollArea>
          )}

          <Box w="100%" style={{ flexShrink: 0 }}>
            <InputArea
              input={input}
              setInput={setInput}
              onSend={handleSend}
              isLoading={isLoading}
              isInitial={isInitialState}
              onQuickQuestion={sendMessage}
            />
          </Box>

          {isInitialState && <Box style={{ flexGrow: 1, minHeight: 0 }} />}
        </Box>
      </AppShell.Main>
    </AppShell>
  );
}
