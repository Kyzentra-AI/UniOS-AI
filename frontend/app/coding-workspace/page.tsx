
import PublicPage from '@/components/public/PublicPage';

export default function CodingWorkspacePage() {
  return (
    <PublicPage
      eyebrow="Product"
      title="Coding Workspace"
      description="A dedicated destination for students to organize coding practice, technical learning, and project work."
      sections={[
        {
          title: 'Practice coding',
          description: 'Keep your technical practice aligned with your goals.',
        },
        {
          title: 'Develop projects',
          description: 'Organize the work you do while building practical skills.',
        },
        {
          title: 'Prepare for interviews',
          description: 'Make space for consistent technical preparation.',
        },
      ]}
    />
  );
}
