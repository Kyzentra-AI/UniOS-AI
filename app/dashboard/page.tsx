import ProtectedRoute from '@/components/ProtectedRoute';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <main>
        <h1>Irfan</h1>
      </main>
    </ProtectedRoute>
  );
}