import { AppShell, ScrollArea, Container, Stack, Box } from '@mantine/core';
import { useState, useRef, useEffect } from 'react';
import { useChat } from './hooks/useChat';
import MessageBubble from './components/MessageBubble';
import InputArea from './components/UserInput';
import Header from './components/layout/Header';

export default function App() {
  const [input, setInput] = useState('');
  const { messages, sendMessage, isLoading } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);
  const isInitialState = messages.length === 0;

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
  };

  return (
    <AppShell
      header={{ height: 60 }}
      styles={{
        main: {
          // backgroundColor: '#131314',
          // color: '#e3e3e3',
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          padding: 0,
        },
      }}
    >
      <AppShell.Header p="md" bg="#131314" style={{ borderBottom: '1px solid #2e2e2e' }}>
        <Header />
      </AppShell.Header>

      <AppShell.Main>
        <Box
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: isInitialState ? 'center' : 'flex-end',
            overflow: 'hidden',
          }}
        >
          {!isInitialState && (
            <ScrollArea flex={1} p="md">
              <Container size="md">
                <Stack gap="xl">
                  {messages.map((msg, i) => (
                    <MessageBubble key={i} msg={msg} />
                  ))}
                  <div ref={scrollRef} />
                </Stack>
              </Container>
            </ScrollArea>
          )}

          <InputArea
            input={input}
            setInput={setInput}
            onSend={handleSend}
            isLoading={isLoading}
            isInitial={isInitialState}
          />
        </Box>
      </AppShell.Main>
    </AppShell>
  );
}
