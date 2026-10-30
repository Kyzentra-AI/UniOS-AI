import CompeteWorkspace from '@/components/compete/workspace/CompeteWorkspace';
import ProtectedRoute from '@/components/ProtectedRoute';


export default function CompetePage() {
  return (
    <ProtectedRoute>
      <CompeteWorkspace />
    </ProtectedRoute>
  );
}
