
import PublicPage from '@/components/public/PublicPage';

export default function CareerGuidancePage() {
  return (
    <PublicPage
      eyebrow="Product"
      title="Career Guidance"
      description="Explore career directions, identify skills to develop, and plan your next steps toward professional readiness."
      sections={[
        {
          title: 'Explore career paths',
          description: 'Understand possible directions for your interests.',
        },
        {
          title: 'Build relevant skills',
          description: 'Identify areas to focus on as you develop professionally.',
        },
        {
          title: 'Plan your next steps',
          description: 'Create a clearer direction for your career preparation.',
        },
      ]}
    />
  );
}
