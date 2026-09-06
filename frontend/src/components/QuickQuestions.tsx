import { Group, Button, Box } from '@mantine/core';
import { DEFAULT_QUESTIONS } from '../constants/questions';

export interface QuickQuestionsProps {
  onQuestionClick: (question: string) => void;
  disabled?: boolean;
  questions?: string[];
}

export default function QuickQuestions({
  onQuestionClick,
  disabled = false,
  questions = DEFAULT_QUESTIONS,
}: QuickQuestionsProps) {
  return (
    <Box style={{ overflowX: 'auto', paddingBottom: '8px' }}>
      <Group
        justify="flex-start"
        gap="xs"
        wrap="nowrap"
        style={{ width: 'max-content', margin: '0 auto' }}
      >
        {questions.map((q) => (
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
