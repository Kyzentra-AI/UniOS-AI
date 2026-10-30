
import PublicPage from '@/components/public/PublicPage';

export default function CareerGuidesPage() {
  return (
    <PublicPage
      eyebrow="Resources"
      title="Career Guides"
      description="Explore practical guidance for developing professional skills, building projects, and preparing for career opportunities."
      sections={[
        {
          title: 'Career planning',
          description: 'Identify goals and break them into actionable steps.',
        },
        {
          title: 'Project development',
          description: 'Understand how practical projects contribute to skill development.',
        },
        {
          title: 'Interview preparation',
          description: 'Organize your technical learning and interview practice.',
        },
      ]}
    />
  );
}
