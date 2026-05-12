import { Group, Avatar, Box } from '@mantine/core';
import { User, Cpu } from 'react-feather';
import ReactMarkdown from 'react-markdown';
import type { Message } from '../types/chat';

interface MessageBubbleProps {
  msg: Message;
}

export default function MessageBubble({ msg }: MessageBubbleProps) {
  const isUser = msg.role === 'user';

  return (
    <Group align="flex-start" justify={isUser ? 'flex-end' : 'flex-start'}>
      <Group
        align="flex-start"
        gap="md"
        style={{
          flexDirection: isUser ? 'row-reverse' : 'row',
          maxWidth: '85%',
        }}
      >
        <Avatar radius="xl" size="md" color={isUser ? 'purple' : 'blue'} variant="filled">
          {isUser ? <User size={16} /> : <Cpu size={16} />}
        </Avatar>
        <Box style={{ flex: 1 }}>
          {/* Markdown support is essential for professional LLM responses. 
              We explicitly disable HTML rendering for security. */}
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
