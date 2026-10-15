import CompetitionDetails from '@/components/compete/detail/CompetitionDetails';

export default async function CompetitionDetailPage({
  params,
}: {
  params: Promise<{ competitionId: string }>;
}) {
  const { competitionId } = await params;
  return <CompetitionDetails competitionId={competitionId} />;
}
