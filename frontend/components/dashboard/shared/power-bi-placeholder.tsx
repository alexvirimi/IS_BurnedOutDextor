import { MicrosoftIcon } from "@/components/icons";

interface PowerBIPlaceholderProps {
  label?: string;
}

export function PowerBIPlaceholder({
  label = "Power BI",
}: PowerBIPlaceholderProps) {
  return (
    <div className="mt-6 bg-muted rounded-lg aspect-video flex items-center justify-center">
      <div className="flex items-center gap-2 text-muted-foreground">
        <MicrosoftIcon className="w-5 h-5" />
        <span className="font-sans font-medium">{label}</span>
      </div>
    </div>
  );
}
