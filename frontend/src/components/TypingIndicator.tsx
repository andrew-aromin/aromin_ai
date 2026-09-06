import { Group, Avatar, Box } from '@mantine/core';
import { Cpu } from 'react-feather';

export default function TypingIndicator() {
  return (
    <Group
      align="flex-start"
      justify="flex-start"
      data-testid="typing-indicator"
      aria-label="Assistant is generating response"
    >
      <Group
        align="flex-start"
        gap="md"
        style={{
          maxWidth: '85%',
        }}
      >
        <Avatar radius="xl" size="md" color="blue" variant="filled" aria-label="Assistant avatar">
          <Cpu size={16} data-testid="cpu-icon" />
        </Avatar>
        <Box
          bg="#2e2e2e"
          p="sm"
          style={{
            borderRadius: '12px',
            display: 'flex',
            gap: '4px',
            alignItems: 'center',
            minHeight: '40px',
          }}
        >
          <div className="typing-dot" data-testid="typing-dot" />
          <div className="typing-dot" data-testid="typing-dot" />
          <div className="typing-dot" data-testid="typing-dot" />
        </Box>
      </Group>
    </Group>
  );
}
