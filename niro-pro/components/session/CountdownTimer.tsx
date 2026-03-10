"use client";
import { useEffect, useState } from "react";
import { formatSeconds } from "@/lib/utils";
import { clsx } from "clsx";

interface CountdownTimerProps {
  totalSeconds?: number;
  onMilestone?: (secondsLeft: number) => void;
}

export default function CountdownTimer({ totalSeconds = 300, onMilestone }: CountdownTimerProps) {
  const [seconds, setSeconds] = useState(totalSeconds);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (seconds <= 0) { setDone(true); return; }
    const t = setInterval(() => {
      setSeconds(s => {
        const next = s - 1;
        onMilestone?.(next);
        if (next <= 0) { clearInterval(t); setDone(true); return 0; }
        return next;
      });
    }, 1000);
    return () => clearInterval(t);
  }, []);

  const color = seconds > 90 ? "text-emerald-600" : seconds > 30 ? "text-amber-600" : "text-red-600";

  return (
    <div className="text-center">
      <span className={clsx("text-3xl font-mono font-bold tabular-nums", color, seconds < 30 && "animate-pulse")}>
        {formatSeconds(seconds)}
      </span>
      {done && <p className="text-xs text-red-500 font-medium mt-1">Time&apos;s up — send your offer</p>}
    </div>
  );
}
