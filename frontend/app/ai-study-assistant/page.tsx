
import PublicPage from '@/components/public/PublicPage';

export default function AIStudyAssistantPage() {
  return (
    <PublicPage
      eyebrow="Product"
      title="AI Study Assistant"
      description="A study companion to help students understand concepts, organize their learning, and work through academic questions."
      sections={[
        {
          title: 'Understand concepts',
          description: 'Get support while learning difficult academic topics.',
        },
        {
          title: 'Organize learning',
          description: 'Keep your study goals and learning priorities clear.',
        },
        {
          title: 'Study consistently',
          description: 'Build a more structured approach to daily learning.',
        },
      ]}
    />
  );
}
