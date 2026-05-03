import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import {
  AppShell,
  ActionIcon,
  Group,
  Text,
  ScrollArea,
  Avatar,
  Stack,
  Container,
  Box,
  Textarea,
  Typography,
  Loader,
} from '@mantine/core';
import { useChat } from './hooks/useChat';

export default function App() {
  const [input, setInput] = useState('');
  const { messages, sendMessage, isLoading } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Check if we are in the "Initial" state
  const isInitialState = messages.length === 0;

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <AppShell
      header={{ height: 60 }}
      padding="md"
      styles={{
        main: {
          backgroundColor: '#131314',
          color: '#e3e3e3',
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          padding: 0,
        },
      }}
    >
      <AppShell.Header p="md" bg="#131314" style={{ borderBottom: '1px solid #2e2e2e' }}>
        <Group gap="xs">
          <Sparkles color="#60a5fa" size={20} />
          <Text fw={600} size="lg">Resume Intelligence</Text>
        </Group>
      </AppShell.Header>

      <AppShell.Main>
        <Box 
          style={{ 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column', 
            justifyContent: isInitialState ? 'center' : 'flex-end', // Centers content when empty
            overflow: 'hidden' 
          }}
        >
          {/* ScrollArea only shows when there are messages */}
          {!isInitialState && (
            <ScrollArea flex={1} p="md">
              <Container size="md">
                <Stack gap="xl">
                  {messages.map((msg, i) => (
                    <Group
                      key={i}
                      align="flex-start"
                      justify={msg.role === 'user' ? 'flex-end' : 'flex-start'}
                    >
                      <Group
                        align="flex-start"
                        gap="md"
                        style={{
                          flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                          maxWidth: '85%',
                        }}
                      >
                        <Avatar
                          radius="xl"
                          size="md"
                          color={msg.role === 'user' ? 'purple' : 'blue'}
                          variant="filled"
                        >
                          {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                        </Avatar>
                        <Box style={{ flex: 1 }}>
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </Box>
                      </Group>
                    </Group>
                  ))}
                  <div ref={scrollRef} />
                </Stack>
              </Container>
            </ScrollArea>
          )}

          {/* This Container now moves based on the parent Box's justify-content */}
          <Container size="md" w="100%" py="xl">
            {isInitialState && (
              <Box mb={40}>
                <Text size="xl" fw={500} ta="center" style={{ fontSize: '2.5rem', color: '#fff' }}>
                  How can I help you today?
                </Text>
              </Box>
            )}
            
            <Box style={{ position: 'relative' }}>
              <Textarea
                size="xl" // Increased size for the "middle" look
                radius="xl"
                placeholder="Ask about my career..."
                autosize
                minRows={1}
                maxRows={4}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                styles={{
                  input: {
                    backgroundColor: '#1e1e1f',
                    border: '1px solid #3e3e3e',
                    paddingRight: '50px',
                    color: '#e3e3e3',
                    fontSize: '1.1rem',
                    '&:focus': {
                      borderColor: '#60a5fa',
                    },
                  },
                }}
              />
              <ActionIcon
                size={40}
                radius="xl"
                variant="filled"
                color="blue"
                disabled={isLoading || !input.trim()}
                onClick={handleSend}
                style={{
                  position: 'absolute',
                  right: 10,
                  bottom: 8,
                  zIndex: 2,
                }}
              >
                {isLoading ? <Loader size={18} color="white" /> : <Send size={20} />}
              </ActionIcon>
            </Box>
          </Container>
        </Box>
      </AppShell.Main>
    </AppShell>
  );
}
