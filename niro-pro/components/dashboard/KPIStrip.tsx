import { formatCurrency } from "@/lib/utils";
import { MOCK_PRACTITIONER } from "@/lib/mock-data";

export default function KPIStrip() {
  const kpis = [
    { label: "Conversion rate", value: `${MOCK_PRACTITIONER.conversion_rate}%`, sub: "5-min conversion — March", border: "border-l-violet-500" },
    { label: "Revenue this month", value: formatCurrency(MOCK_PRACTITIONER.total_revenue_inr), sub: "from 5 clients this month", border: "border-l-emerald-500" },
    { label: "Rating", value: `${MOCK_PRACTITIONER.average_rating} ⭐`, sub: `from ${MOCK_PRACTITIONER.total_sessions} sessions`, border: "border-l-amber-500" },
  ];
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      {kpis.map(k => (
        <div key={k.label} className={`bg-white rounded-xl shadow-sm border border-gray-100 border-l-4 ${k.border} p-5`}>
          <p className="text-xs text-gray-400 font-medium uppercase tracking-wide mb-1">{k.label}</p>
          <p className="text-2xl font-bold text-gray-900">{k.value}</p>
          <p className="text-xs text-gray-400 mt-1">{k.sub}</p>
        </div>
      ))}
    </div>
  );
}
