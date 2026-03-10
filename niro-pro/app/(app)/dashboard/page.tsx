"use client";
import KPIStrip from "@/components/dashboard/KPIStrip";
import MilestoneTracker from "@/components/dashboard/MilestoneTracker";
import LeadCard from "@/components/leads/LeadCard";
import { MOCK_LEADS, MOCK_PRACTITIONER } from "@/lib/mock-data";
import { getTimeGreeting } from "@/lib/utils";

export default function DashboardPage() {
  const pendingLeads = MOCK_LEADS.filter(l => l.status === "pending");
  const greeting = getTimeGreeting();

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{greeting}, {MOCK_PRACTITIONER.full_name.split(" ")[0]} 🌟</h1>
        <p className="text-gray-400 text-sm mt-1">Here&apos;s what&apos;s happening today.</p>
      </div>

      <KPIStrip />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-gray-900">
              Leads waiting for you
              {pendingLeads.length > 0 && (
                <span className="ml-2 bg-red-500 text-white text-xs font-bold px-1.5 py-0.5 rounded-full">{pendingLeads.length}</span>
              )}
            </h2>
          </div>
          {pendingLeads.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 text-center">
              <p className="text-gray-400 text-sm">No leads right now — we&apos;re finding the right clients for you 🔍</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {pendingLeads.map(lead => <LeadCard key={lead.id} lead={lead} />)}
            </div>
          )}
        </div>
        <div>
          <h2 className="text-base font-semibold text-gray-900 mb-4">Your journey</h2>
          <MilestoneTracker />
        </div>
      </div>
    </div>
  );
}
