import { AppShell, Group, Text, Anchor, ActionIcon, Tooltip } from '@mantine/core';
import { Zap, FileText, Linkedin, GitHub } from 'react-feather';

export default function Header() {
  return (
    <AppShell.Header p="md" style={{ borderBottom: '1px solid #2e2e2e' }}>
      <Group justify="space-between" h="100%">
        {/* Left Side: Brand/Logo */}
        <Group gap="xs">
          <Zap color="#60a5fa" size={20} />
          <Text fw={600} size="lg" c="white">
            Resume Intelligence
          </Text>
        </Group>

        {/* Right Side: External Links */}
        <Group gap="md">
          <Tooltip label="View LinkedIn Profile" withArrow>
            <ActionIcon
              component="a"
              href="https://linkedin.com/in/your-profile"
              target="_blank"
              variant="subtle"
              color="gray"
            >
              <Linkedin size={20} />
            </ActionIcon>
          </Tooltip>

          <Tooltip label="View GitHub" withArrow>
            <ActionIcon
              component="a"
              href="https://github.com/your-username"
              target="_blank"
              variant="subtle"
              color="gray"
            >
              <GitHub size={20} />
            </ActionIcon>
          </Tooltip>

          <Anchor href="/resume.pdf" target="_blank" underline="never">
            <Group gap={5} style={{ color: '#60a5fa' }}>
              <FileText size={18} />
              <Text size="sm" fw={500}>
                Resume
              </Text>
            </Group>
          </Anchor>
        </Group>
      </Group>
    </AppShell.Header>
  );
}
