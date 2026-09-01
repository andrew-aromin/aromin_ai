import { AppShell, Group, Text, Anchor, Tooltip, Avatar } from '@mantine/core';
import { FileText, Linkedin, GitHub } from 'react-feather';

export default function Header() {
  return (
    <AppShell.Header p="md" bg="#131314" style={{ borderBottom: '1px solid #2e2e2e' }}>
      <Group justify="space-between" h="100%">
        <Anchor href="/" underline="never">
          <Avatar
            src="/avatar.png" // Path to your photo in the public folder
            alt="Andrew Aromin"
            radius="xl"
            size="md"
          />
        </Anchor>
        <Group gap="md">
          <Tooltip label="View LinkedIn Profile" withArrow>
            <Anchor href="https://linkedin.com/in/andrew-aromin" target="_blank" underline="never">
              <Group gap={5} style={{ color: '#60a5fa' }}>
                <Linkedin size={18} />
                <Text size="sm" fw={500} visibleFrom="sm">
                  LinkedIn
                </Text>
              </Group>
            </Anchor>
          </Tooltip>

          <Tooltip label="View GitHub" withArrow>
            <Anchor href="https://github.com/andrew-aromin" target="_blank" underline="never">
              <Group gap={5} style={{ color: '#60a5fa' }}>
                <GitHub size={18} />
                <Text size="sm" fw={500} visibleFrom="sm">
                  GitHub
                </Text>
              </Group>
            </Anchor>
          </Tooltip>

          <Anchor href="/resume.pdf" target="_blank" underline="never">
            <Group gap={5} style={{ color: '#60a5fa' }}>
              <FileText size={18} />
              <Text size="sm" fw={500} visibleFrom="sm">
                Resume
              </Text>
            </Group>
          </Anchor>
        </Group>
      </Group>
    </AppShell.Header>
  );
}
