const MILESTONES = [
  { label: "Profile complete", done: true },
  { label: "First package created", done: true },
  { label: "First lead received", done: true },
  { label: "First session completed", done: false, hint: "Join your first session to unlock earnings" },
  { label: "First paid client", done: false, hint: "" },
];

export default function MilestoneTracker() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Your journey</h3>
      <div className="space-y-3">
        {MILESTONES.map((m, i) => (
          <div key={i} className="flex items-start gap-3">
            <div className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${m.done ? "bg-emerald-100 text-emerald-600" : "bg-gray-100 text-gray-400"}`}>
              {m.done ? "✓" : ""}
            </div>
            <div>
              <p className={`text-sm ${m.done ? "text-gray-400 line-through" : "text-gray-700 font-medium"}`}>{m.label}</p>
              {!m.done && m.hint && <p className="text-xs text-gray-400 mt-0.5">{m.hint}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
