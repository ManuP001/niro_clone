"use client";
import { useRouter } from "next/navigation";
import { Lead } from "@/lib/types";
import Badge from "@/components/ui/Badge";
import CountdownBadge from "./CountdownBadge";
import Button from "@/components/ui/Button";

export default function LeadCard({ lead }: { lead: Lead }) {
  const router = useRouter();
  const preview = lead.question.split(" ").slice(0, 12).join(" ") + "...";
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-center justify-between mb-3">
        <Badge topic={lead.life_area} />
        <CountdownBadge initialSeconds={lead.expires_in_seconds} />
      </div>
      <p className="text-sm text-gray-700 mb-4 leading-relaxed">{preview}</p>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400">Platform fee: ₹{lead.flat_fee_inr}</span>
        <Button size="sm" onClick={() => router.push(`/leads/${lead.id}`)}>Review Lead →</Button>
      </div>
    </div>
  );
}
