import Syllabus from '@/pages/Syllabus';
import ProtectedRoute from "@/components/ProtectedRoute";

export default function SyllabusPage() {

  return (
      <ProtectedRoute>
        <Syllabus />
      </ProtectedRoute>
    );
  }