"use client";
import LeadCard from "@/components/leads/LeadCard";
import { MOCK_LEADS } from "@/lib/mock-data";

export default function LeadsPage() {
  const pending = MOCK_LEADS.filter(l => l.status === "pending");
  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
        {pending.length > 0 && (
          <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">{pending.length}</span>
        )}
      </div>
      {pending.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-12 text-center">
          <p className="text-gray-400">No pending leads right now — we&apos;re finding the right clients for you 🔍</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {pending.map(lead => <LeadCard key={lead.id} lead={lead} />)}
        </div>
      )}
    </div>
  );
}
