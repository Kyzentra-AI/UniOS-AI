import ProtectedRoute from '@/components/ProtectedRoute';

import Landing from '@/pages/Landing';
export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <Landing/>
    </ProtectedRoute>
  );
}