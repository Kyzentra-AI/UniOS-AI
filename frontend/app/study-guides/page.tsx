
import PublicPage from '@/components/public/PublicPage';

export default function StudyGuidesPage() {
  return (
    <PublicPage
      eyebrow="Resources"
      title="Study Guides"
      description="Organize your academic preparation with structured approaches to learning, revision, and subject planning."
      sections={[
        {
          title: 'Study planning',
          description: 'Learn how to divide subjects into manageable study sessions.',
        },
        {
          title: 'Revision strategies',
          description: 'Explore approaches to reviewing concepts and retaining knowledge.',
        },
        {
          title: 'Learning routines',
          description: 'Develop a consistent routine around your academic priorities.',
        },
      ]}
    />
  );
}
