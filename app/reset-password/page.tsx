import { redirect } from 'next/navigation';
import ResetPassword from '@/pages/ResetPassword';

interface ResetPasswordPageProps {
  searchParams: Promise<{
    token?: string;
  }>;
}

export default async function ResetPasswordPage({
  searchParams,
}: ResetPasswordPageProps) {
  const params = await searchParams;

  if (!params.token) {
    redirect('/forgot-password');
  }

  return <ResetPassword />;
}