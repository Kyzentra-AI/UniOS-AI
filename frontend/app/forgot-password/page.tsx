
import Forgot from '@/pages/Forgot';
import ProtectedRoute from "@/components/ProtectedRoute";

export default function ForgotPasswordPage() {
  return (
    <ProtectedRoute>
      <Forgot />
    </ProtectedRoute>
  );
}
