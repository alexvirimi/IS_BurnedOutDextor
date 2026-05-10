"use client";

import { useRouter } from "next/navigation";
import { BudLogo } from "@/components/icons";
import { useAuth } from "@/lib/auth/context";
import { authApi } from "@/lib/auth/api";

interface BurnoutRiskCardProps {
  label?: string;
  percentage?: number;
}

export function BurnoutRiskCard({
  label = "Poco Probable",
  percentage = 15,
}: BurnoutRiskCardProps) {
  return (
    <div className="bg-muted rounded-lg p-4">
      <h3 className="font-heading font-bold text-foreground text-sm">
        Riesgo de Burn Out
      </h3>
      <div className="flex justify-between items-center mt-1">
        <span className="text-primary text-sm font-sans">{label}</span>
        <span className="text-foreground text-sm font-sans">{percentage}%</span>
      </div>
    </div>
  );
}

interface SidebarShellProps {
  userName: string;
  children: React.ReactNode;
}

export function SidebarShell({ userName, children }: SidebarShellProps) {
  const { session, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await authApi.logout(); // no argument needed
    } catch {
      // always clear client state regardless
    } finally {
      logout();
      router.push("/login");
    }
  };

  return (
    <aside className="w-72 h-screen bg-background flex flex-col border-r border-border fixed left-0 top-0 overflow-y-auto">
      {/* User Profile */}
      <div className="flex flex-col items-center pt-8 px-6">
        <h2 className="font-heading font-bold text-foreground text-center text-sm">
          {userName}
        </h2>
      </div>

      {/* Navigation slot */}
      <nav className="flex flex-col gap-2 mt-8 px-6">{children}</nav>

      <div className="flex-1" />

      {/* Burnout risk card */}
      <div className="px-6 mb-4">
        <BurnoutRiskCard />
      </div>

      {/* Log Out button */}
      <div className="px-6 mb-4">
        <button
          onClick={handleLogout}
          className="w-full text-left px-4 py-3 rounded-lg font-sans text-sm transition-colors bg-transparent border border-border text-foreground hover:bg-destructive/10 hover:text-destructive hover:border-destructive/30"
        >
          Cerrar sesión
        </button>
      </div>

      {/* Logo */}
      <div className="flex justify-center pb-8">
        <BudLogo className="w-24 h-auto" />
      </div>
    </aside>
  );
}

/** Reusable nav button for sidebar items */
interface SidebarNavButtonProps {
  label: string;
  isActive: boolean;
  onClick: () => void;
  children?: React.ReactNode;
}

export function SidebarNavButton({
  label,
  isActive,
  onClick,
  children,
}: SidebarNavButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-4 py-3 rounded-lg font-sans text-sm transition-colors ${
        isActive
          ? "bg-primary text-primary-foreground font-medium"
          : "bg-transparent border border-border text-foreground hover:bg-muted"
      }`}
    >
      {children ?? label}
    </button>
  );
}

/** Collapsible sub-menu section */
interface SidebarExpandableProps {
  label: string;
  isExpanded: boolean;
  isActive: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

export function SidebarExpandable({
  label,
  isExpanded,
  isActive,
  onToggle,
  children,
}: SidebarExpandableProps) {
  return (
    <div>
      <button
        onClick={onToggle}
        className={`w-full text-left px-4 py-3 rounded-lg font-sans text-sm transition-colors flex items-center justify-between ${
          isActive
            ? "bg-primary text-primary-foreground font-medium"
            : "bg-transparent border border-border text-foreground hover:bg-muted"
        }`}
      >
        <span>{label}</span>
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`transition-transform ${isExpanded ? "rotate-180" : ""}`}
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>
      {isExpanded && (
        <div className="mt-1 border border-border border-foreground/30 rounded-lg overflow-hidden">
          {children}
        </div>
      )}
    </div>
  );
}

/** Sub-item inside an expandable section */
interface SidebarSubItemProps {
  label: string;
  isActive: boolean;
  onClick: () => void;
}

export function SidebarSubItem({
  label,
  isActive,
  onClick,
}: SidebarSubItemProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-6 py-2 font-sans text-sm transition-colors ${
        isActive
          ? "bg-secondary/80 font-bold text-foreground"
          : "text-foreground hover:bg-secondary/60"
      }`}
    >
      {label}
    </button>
  );
}
