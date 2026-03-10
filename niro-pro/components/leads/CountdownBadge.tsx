"use client";
import { useEffect, useState } from "react";
import { formatSeconds } from "@/lib/utils";
import { clsx } from "clsx";

export default function CountdownBadge({ initialSeconds, onExpire }: { initialSeconds: number; onExpire?: () => void }) {
  const [seconds, setSeconds] = useState(initialSeconds);

  useEffect(() => {
    if (seconds <= 0) { onExpire?.(); return; }
    const t = setInterval(() => setSeconds(s => { if (s <= 1) { clearInterval(t); onExpire?.(); return 0; } return s - 1; }), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <span className={clsx("text-xs font-mono font-bold px-2 py-1 rounded-full",
      seconds > 300 ? "bg-emerald-100 text-emerald-700" :
      seconds > 60  ? "bg-amber-100 text-amber-700 animate-pulse" :
                      "bg-red-100 text-red-700 animate-pulse"
    )}>
      {formatSeconds(seconds)}
    </span>
  );
}
