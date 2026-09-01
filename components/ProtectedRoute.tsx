'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getSession } from '@/lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({
  children,
}: ProtectedRouteProps) {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const session = getSession();

    if (!session?.access_token) {
      router.replace('/login');
      return;
    }

    setIsChecking(false);
  }, [router]);

  if (isChecking) {
    return null;
  }

  return <>{children}</>;
}