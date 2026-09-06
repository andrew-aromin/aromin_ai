import { Group, Avatar, Box } from '@mantine/core';
import { User, Cpu } from 'react-feather';
import ReactMarkdown from 'react-markdown';
import type { Message } from '../types/chat';

export interface MessageBubbleProps {
  msg: Message;
}

export default function MessageBubble({ msg }: MessageBubbleProps) {
  const isUser = msg.role === 'user';

  return (
    <Group
      align="flex-start"
      justify={isUser ? 'flex-end' : 'flex-start'}
      data-testid="message-bubble"
      data-role={msg.role}
    >
      <Group
        align="flex-start"
        gap="md"
        style={{
          flexDirection: isUser ? 'row-reverse' : 'row',
          maxWidth: '85%',
        }}
      >
        <Avatar
          radius="xl"
          size="md"
          color={isUser ? 'purple' : 'blue'}
          variant="filled"
          aria-label={isUser ? 'User avatar' : 'Assistant avatar'}
        >
          {isUser ? (
            <User size={16} data-testid="user-icon" />
          ) : (
            <Cpu size={16} data-testid="cpu-icon" />
          )}
        </Avatar>
        <Box style={{ flex: 1 }}>
          <ReactMarkdown
            components={{
              a: ({ ...props }) => (
                <a
                  {...props}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: '#4dabf7' }}
                />
              ),
            }}
          >
            {msg.content}
          </ReactMarkdown>
        </Box>
      </Group>
    </Group>
  );
}
