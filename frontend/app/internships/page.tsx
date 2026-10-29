
import PublicPage from '@/components/public/PublicPage';

export default function InternshipsPage() {
  return (
    <PublicPage
      eyebrow="Product"
      title="Internship Tracker"
      description="Keep your internship preparation organized, from identifying opportunities to tracking your application progress."
      sections={[
        {
          title: 'Track applications',
          description: 'Keep track of the opportunities you are pursuing.',
        },
        {
          title: 'Prepare your profile',
          description: 'Work toward presenting your skills and experience clearly.',
        },
        {
          title: 'Stay organized',
          description: 'Keep your preparation and application tasks in order.',
        },
      ]}
    />
  );
}
