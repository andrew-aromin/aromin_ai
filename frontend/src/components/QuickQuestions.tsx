import { Group, Button, Box } from '@mantine/core';

interface QuickQuestionsProps {
  onQuestionClick: (question: string) => void;
  disabled?: boolean;
}

const QUESTIONS = [
  "Summarize Andrew's background",
  "Building 'Balto' ($100K+ savings)",
  "Serverless & Event-Driven design",
  "AI-augmented workflows",
  "Modernizing Artiva at Credit Acceptance"
];

export default function QuickQuestions({ onQuestionClick, disabled }: QuickQuestionsProps) {
  return (
    <Box style={{ overflowX: 'auto', paddingBottom: '8px' }}>
      <Group justify="flex-start" gap="xs" wrap="nowrap" style={{ width: 'max-content', margin: '0 auto' }}>
        {QUESTIONS.map((q) => (
          <Button
            key={q}
            variant="default"
            radius="xl"
            size="sm"
            disabled={disabled}
            onClick={() => onQuestionClick(q)}
            styles={{
              root: {
                backgroundColor: '#1e1e1f',
                borderColor: '#3e3e3e',
                color: '#e3e3e3',
                '&:hover': {
                  backgroundColor: '#2e2e2e',
                },
              },
            }}
          >
            {q}
          </Button>
        ))}
      </Group>
    </Box>
  );
}
