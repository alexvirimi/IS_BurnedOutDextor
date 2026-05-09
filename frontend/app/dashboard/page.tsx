import { Dashboard } from "@/components/dashboard";

/**
 * Replace the hardcoded role with your real auth logic, e.g.:
 *   const role = await getSessionRole()   // "hr" | "pm" | "worker"
 */
export default function DashboardPage() {
  return <Dashboard role="hr" />;
}
