"use client";

import { HRDashboard } from "./hr";
import { PMDashboard } from "./pm";
import { WKRDashboard } from "./wkr";

export type UserRole = "hr" | "pm" | "worker";

interface DashboardProps {
  role?: UserRole;
}

export function Dashboard({ role = "worker" }: DashboardProps) {
  switch (role) {
    case "hr":
      return <HRDashboard />;
    case "pm":
      return <PMDashboard />;
    case "worker":
      return <WKRDashboard />;
  }
}
