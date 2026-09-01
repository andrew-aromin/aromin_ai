import { Text, Avatar, Stack, Anchor, Divider, Space } from '@mantine/core';

export default function Title() {
  return (
    <>
      <Stack justify="center" align="center" gap="xs" pb="0">
        <Text
          fz={{ base: '2rem', sm: '2.75rem', md: '3.5rem' }}
          fw={500}
          c="white"
          ta="center"
        >
          Hi, I'm Andrew.
        </Text>
        <Avatar
          src="/avatar.png"
          alt="Andrew Aromin"
          radius="xl"
          className="hero-avatar"
        />
      </Stack>
      <Text
        component="div"
        fz={{ base: 'md', sm: 'lg', md: 'xl' }}
        fw={500}
        ta="center"
        c="white"
      >
        Ask questions about my software engineering career and background. Built using React, FastAPI, and Ollama with local LLM orchestration. 
        <Divider my="xs" />
        <Text fs="italic" fz={{ base: 'xs', sm: 'sm', md: 'md' }}>
          Note: Hosted on low-power hardware; response generation may take a moment.
        </Text>
        <Space h="xs" />
        Source Code:{' '}
        <Anchor href="https://github.com/andrew-aromin/aromin_ai" target="_blank">
          <Text span fz={{ base: 'sm', sm: 'md', md: 'lg' }} fw={500}>
            Aromin AI
          </Text>
        </Anchor>
      </Text>
    </>
  );
}
