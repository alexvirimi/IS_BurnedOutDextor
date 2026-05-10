"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/context";

interface DashboardAuthGuardProps {
  children: ReactNode;
}

/**
 * Client-side route guard.
 * Redirects to /login if no session is present.
 * Renders nothing while session is being rehydrated from localStorage.
 */
export function DashboardAuthGuard({ children }: DashboardAuthGuardProps) {
  const { isAuthenticated, session } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // session starts as null during SSR/hydration; only redirect once we
    // know hydration is done (we can tell because useEffect runs client-side).
    if (!isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, router]);

  // Don't flash dashboard content before redirect fires
  if (!session) return null;

  return <>{children}</>;
}
