
import PublicPage from '@/components/public/PublicPage';

export default function BlogPage() {
  return (
    <PublicPage
      eyebrow="Resources"
      title="The UniOS Blog"
      description="Insights on learning, technical skills, projects, and career preparation."
      sections={[
        {
          title: 'Learning',
          description: 'Ideas for improving study habits and learning workflows.',
        },
        {
          title: 'Technology',
          description: 'Explore topics related to technical skills and development.',
        },
        {
          title: 'Careers',
          description: 'Perspectives on building skills and preparing for opportunities.',
        },
      ]}
    />
  );
}
