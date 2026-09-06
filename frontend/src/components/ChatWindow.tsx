import React from 'react';
import { ScrollArea, Container, Stack } from '@mantine/core';
import type { Message } from '../types/chat';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

export interface ChatWindowProps {
  messages: Message[];
  showTyping?: boolean;
  scrollRef: React.RefObject<HTMLDivElement | null>;
}

export default function ChatWindow({ messages, showTyping = false, scrollRef }: ChatWindowProps) {
  return (
    <ScrollArea flex={1} p="md" offsetScrollbars scrollbarSize={8} style={{ width: '100%' }}>
      <Container size="md">
        <Stack gap="xl" role="log" aria-live="polite">
          {messages.map((msg, index) => (
            <MessageBubble key={`${msg.role}-${index}`} msg={msg} />
          ))}
          {showTyping && <TypingIndicator />}
          <div ref={scrollRef} data-testid="scroll-anchor" style={{ height: 1 }} />
        </Stack>
      </Container>
    </ScrollArea>
  );
}
