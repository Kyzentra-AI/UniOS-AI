import ProtectedRoute from '@/components/ProtectedRoute';

import Landing from '@/pages/Landing';
export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <section className  = "px-10 py-10">
        <h1 className = "text-center">Welcome to Unios</h1>
      </section>
    </ProtectedRoute>
  );
}