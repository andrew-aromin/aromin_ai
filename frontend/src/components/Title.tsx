import { Text, Avatar, Stack, Anchor, Divider, Space } from '@mantine/core';

export default function Title() {
  return (
    <>
      <Stack justify="center" align="center" gap="xs" pb="0">
        <Text size="3.5rem" fw={500} color="white">
          Hi, I'm Andrew.
        </Text>
        <Avatar src="/avatar.png" alt="Andrew Aromin" radius="xl" size="10rem" />
      </Stack>
      <Text size="xl" fw={500} ta="center" color={'white'}>
        Ask questions about my software engineering career and background. Built using React, FastAPI, and Ollama with local LLM orchestration. 
        <Divider my="xs" />
        <Text fs="italic">Note: Hosted on low-power hardware; response generation may take a moment.</Text>
        <Space h="xs" />
        Source Code: <Anchor href="https://github.com/andrew-aromin/aromin_ai" target="_blank">
          <Text size="lg" fw={500}>
            Aromin AI
          </Text>
        </Anchor>
      </Text>
    </>
  );
}
