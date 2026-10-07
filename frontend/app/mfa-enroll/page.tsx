
import ProtectedRoute from '@/components/ProtectedRoute';
import MFAEnroll from '@/pages/MFAEnroll';

export default function MFAEnrollPage() {
  return (
  <ProtectedRoute>
    <MFAEnroll/>
  </ProtectedRoute>
  );
}
       