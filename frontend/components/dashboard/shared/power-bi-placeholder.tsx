import { MicrosoftIcon } from "@/components/icons";

interface PowerBIPlaceholderProps {
  label?: string;
  powerBiTitle?: string;
}

export function PowerBIPlaceholder({
  label = "Power BI",
  powerBiTitle,
}: PowerBIPlaceholderProps) {
  return (
    <div className="mt-6 bg-muted rounded-lg aspect-video flex items-center justify-center">
      <div className="flex flex-col items-center justify-center mb-8">
        <div className="flex items-center gap-2 text-muted-foreground">
          <MicrosoftIcon className="w-5 h-5" />
          <span className="font-sans font-medium">{label}</span>
        </div>
        <span className="text-foreground/70 text-sm mt-2">{powerBiTitle}</span>
      </div>
    </div>
  );
}
