

import ProtectedRoute from '@/components/ProtectedRoute';
import MFASetup from '@/pages/MFASetup';

export default function MFSetupPage() {
  return (
  <ProtectedRoute>
    <MFASetup/>
  </ProtectedRoute>
  );
}
       