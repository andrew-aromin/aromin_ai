import { Group, Avatar, Box } from '@mantine/core';
import { Cpu } from 'react-feather';

export default function TypingIndicator() {
  return (
    <Group align="flex-start" justify="flex-start">
      <Group
        align="flex-start"
        gap="md"
        style={{
          maxWidth: '85%',
        }}
      >
        <Avatar radius="xl" size="md" color="blue" variant="filled">
          <Cpu size={16} />
        </Avatar>
        <Box 
          bg="#2e2e2e" 
          p="sm" 
          style={{ 
            borderRadius: '12px',
            display: 'flex',
            gap: '4px',
            alignItems: 'center',
            minHeight: '40px'
          }}
        >
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
        </Box>
      </Group>
    </Group>
  );
}
