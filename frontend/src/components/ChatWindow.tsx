import React from 'react';
import { ScrollArea, Container, Stack } from '@mantine/core';
import type { Message } from '../types/chat';
import MessageBubble from './MessageBubble';

interface ChatWindowProps {
  messages: Message[];
  scrollRef: React.RefObject<HTMLDivElement | null>;
}

export default function ChatWindow({ messages, scrollRef }: ChatWindowProps) {
  return (
    <ScrollArea flex={1} p="md" offsetScrollbars scrollbarSize={8} style={{ width: '100%' }}>
      <Container size="md">
        <Stack gap="xl">
          {messages.map((msg, index) => (
            <MessageBubble key={`${msg.role}-${index}`} msg={msg} />
          ))}

          {/* The scrollRef anchor is placed at the bottom of the stack.
             When new messages arrive, App.tsx triggers a smooth scroll to this div.
          */}
          <div ref={scrollRef} style={{ height: 1 }} />
        </Stack>
      </Container>
    </ScrollArea>
  );
}
