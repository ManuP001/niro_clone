import { clsx } from "clsx";
import { TOPIC_BADGE_COLOURS } from "@/lib/mock-data";

interface BadgeProps {
  topic: string;
  size?: "sm" | "md";
  className?: string;
}

export default function Badge({ topic, size = "md", className }: BadgeProps) {
  const colours = TOPIC_BADGE_COLOURS[topic] ?? { bg: "bg-gray-100", text: "text-gray-700" };
  const label = topic.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
  return (
    <span
      className={clsx(
        "inline-flex items-center font-medium rounded-full",
        colours.bg,
        colours.text,
        { "px-2 py-0.5 text-xs": size === "sm", "px-3 py-1 text-sm": size === "md" },
        className
      )}
    >
      {label}
    </span>
  );
}
