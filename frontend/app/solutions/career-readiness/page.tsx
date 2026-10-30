
import PublicPage from '@/components/public/PublicPage';

export default function CareerReadinessPage() {
  return (
    <PublicPage
      eyebrow="Solutions"
      title="For Career & Internship Readiness"
      description="Prepare for professional opportunities by organizing your skills, projects, applications, and technical learning."
      sections={[
        {
          title: 'Skills development',
          description: 'Identify and work on skills relevant to your goals.',
        },
        {
          title: 'Project experience',
          description: 'Build practical experience through meaningful projects.',
        },
        {
          title: 'Opportunity planning',
          description: 'Organize your preparation for internships and career opportunities.',
        },
      ]}
    />
  );
}
