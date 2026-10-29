
import PublicPage from '@/components/public/PublicPage';

export default function StudyResourcesPage() {
  return (
    <PublicPage
      eyebrow="Product"
      title="Study Resources"
      description="A dedicated space for students to organize their academic preparation and find useful learning material."
      sections={[
        {
          title: 'Course preparation',
          description: 'Keep your learning organized around your subjects.',
        },
        {
          title: 'Revision planning',
          description: 'Structure revision around your academic priorities.',
        },
        {
          title: 'Learning support',
          description: 'Make it easier to stay focused on your study goals.',
        },
      ]}
    />
  );
}
