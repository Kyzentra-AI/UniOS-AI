'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  clearSession,
  getInactivityTimeout,
  getSession,
  isSessionInactive,
  updateLastActivity,
} from '@/lib/auth';

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

    // Check immediately in case the user was inactive
    // while the protected page was not mounted.
    if (isSessionInactive()) {
      clearSession();
      router.replace('/login');
      return;
    }

    setIsChecking(false);

    let lastActivityUpdate = 0;

    const handleActivity = () => {
      const now = Date.now();

      // Avoid writing to storage on every mouse/scroll event.
      if (now - lastActivityUpdate < 1000) {
        return;
      }

      lastActivityUpdate = now;
      updateLastActivity();
    };

    const activityEvents = [
      'mousedown',
      'keydown',
      'scroll',
      'touchstart',
      'click',
    ];

    activityEvents.forEach((event) => {
      window.addEventListener(event, handleActivity);
    });

    // Periodically check whether the session has crossed
    // the 15-minute inactivity threshold.
const inactivityCheck = window.setInterval(() => {
  const inactive = isSessionInactive();


  if (inactive) {
    clearSession();
    router.replace('/login');
  }
}, 1000);


    return () => {
      activityEvents.forEach((event) => {
        window.removeEventListener(event, handleActivity);
      });

      window.clearInterval(inactivityCheck);
    };
  }, [router]);

  if (isChecking) {
    return null;
  }

  return <>{children}</>;
}