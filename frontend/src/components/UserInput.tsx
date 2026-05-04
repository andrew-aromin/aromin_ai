import { Container, Box, Textarea, ActionIcon, Loader, Text } from '@mantine/core';
import { Send } from 'lucide-react';

interface InputAreaProps {
  input: string;
  setInput: (val: string) => void;
  onSend: () => void;
  isLoading: boolean;
  isInitial: boolean;
}

export default function UserInput({
  input,
  setInput,
  onSend,
  isLoading,
  isInitial,
}: InputAreaProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <Container size="md" w="100%" py="xl">
      {isInitial && (
        <Box mb={40}>
          <Text size="xl" fw={500} ta="center" style={{ fontSize: '2.5rem', color: '#fff' }}>
            What do you want to know about me?
          </Text>
        </Box>
      )}

      <Box style={{ position: 'relative' }}>
        <Textarea
          size="xl"
          radius="xl"
          placeholder="Ask about my career..."
          autosize
          minRows={1}
          maxRows={4}
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
          onKeyDown={handleKeyDown}
          styles={{
            input: {
              backgroundColor: '#1e1e1f',
              border: '1px solid #3e3e3e',
              paddingRight: '50px',
              color: '#e3e3e3',
            },
          }}
        />
        <ActionIcon
          size={40}
          radius="xl"
          variant="filled"
          disabled={isLoading || !input.trim()}
          onClick={onSend}
          style={{ position: 'absolute', right: 10, bottom: 8, zIndex: 2 }}
        >
          {isLoading ? <Loader size={18} color="white" /> : <Send size={20} />}
        </ActionIcon>
      </Box>
    </Container>
  );
}
