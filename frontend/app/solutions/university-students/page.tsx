
import PublicPage from '@/components/public/PublicPage';

export default function UniversityStudentsPage() {
  return (
    <PublicPage
      eyebrow="Solutions"
      title="For University Students"
      description="Bring academic planning, skill development, projects, and career preparation into a more organized workflow."
      sections={[
        {
          title: 'Academic planning',
          description: 'Keep coursework and study priorities organized.',
        },
        {
          title: 'Practical skills',
          description: 'Make time for technical learning and project development.',
        },
        {
          title: 'Career preparation',
          description: 'Work toward internships and future opportunities.',
        },
      ]}
    />
  );
}
