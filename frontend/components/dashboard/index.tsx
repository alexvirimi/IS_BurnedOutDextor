"use client";

import { useAuth } from "@/lib/auth/context";
import { HRDashboard } from "./hr";
import { PMDashboard } from "./pm";
import { WKRDashboard } from "./wkr";

/**
 * Role is now read from the auth context instead of a hardcoded prop.
 * No changes needed to HRDashboard, PMDashboard, or WKRDashboard.
 */
export function Dashboard() {
  const { role } = useAuth();

  switch (role) {
    case "hr":
      return <HRDashboard />;
    case "pm":
      return <PMDashboard />;
    case "worker":
    default:
      return <WKRDashboard />;
  }
}
