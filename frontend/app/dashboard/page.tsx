import { Dashboard } from "@/components/dashboard";
import { DashboardAuthGuard } from "@/components/dashboard/auth-guard";

export default function DashboardPage() {
  return (
    <DashboardAuthGuard>
      <Dashboard />
    </DashboardAuthGuard>
  );
}
