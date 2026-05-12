import { Text, Avatar, Stack } from '@mantine/core';

export default function Title() {
  return (
    <>
      <Stack justify="center" align="center" gap="md" pb="md">
        <Text size="3.5rem" fw={500} color="white">
          Hi, I'm Andrew.
        </Text>
        <Avatar src="/avatar.png" alt="Andrew Aromin" radius="xl" size="10rem" />
      </Stack>
      <Text size="xl" fw={500} ta="center" color={'white'}>
        I built this project with React, FastAPI, and Ollama. This agent leverages local LLM
        orchestration to provide answers about my career in software engineering. Ask it anything!
      </Text>
    </>
  );
}
