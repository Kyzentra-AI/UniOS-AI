
import PublicPage from '@/components/public/PublicPage';

export default function ExamPreparationPage() {
  return (
    <PublicPage
      eyebrow="Solutions"
      title="For Exam Preparation"
      description="Create a more structured approach to exam preparation with clear study priorities, revision goals, and consistent learning."
      sections={[
        {
          title: 'Plan your syllabus',
          description: 'Break preparation into manageable study priorities.',
        },
        {
          title: 'Organize revision',
          description: 'Set aside time to revisit important concepts.',
        },
        {
          title: 'Track progress',
          description: 'Review your preparation and identify what needs attention.',
        },
      ]}
    />
  );
}
