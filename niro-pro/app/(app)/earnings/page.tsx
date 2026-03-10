"use client";
import { MOCK_EARNINGS } from "@/lib/mock-data";
import { formatCurrency, downloadCSV } from "@/lib/utils";
import Button from "@/components/ui/Button";
import { Download } from "lucide-react";

export default function EarningsPage() {
  const totalGross = MOCK_EARNINGS.reduce((s, r) => s + r.gross_inr, 0);
  const totalFees = MOCK_EARNINGS.reduce((s, r) => s + r.fee_inr, 0);
  const totalNet = MOCK_EARNINGS.reduce((s, r) => s + r.net_inr, 0);

  function handleDownload() {
    downloadCSV(
      MOCK_EARNINGS.map(r => ({ Date: r.date, Client: r.client, Package: r.package, Gross: r.gross_inr, Fee: r.fee_inr, Net: r.net_inr })),
      "niro-earnings-march-2026.csv"
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Earnings</h1>
          <p className="text-sm text-gray-400 mt-0.5">March 2026</p>
        </div>
        <Button variant="secondary" size="sm" onClick={handleDownload}>
          <Download className="w-4 h-4" /> Download Statement
        </Button>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: "Total revenue", value: formatCurrency(totalGross) },
          { label: "Platform fees", value: formatCurrency(totalFees) },
          { label: "Net earnings", value: formatCurrency(totalNet) },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <p className="text-xs text-gray-400 mb-1">{k.label}</p>
            <p className="text-xl font-bold text-gray-900">{k.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              {["Date", "Client", "Package", "Gross", "Fee", "Net"].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {MOCK_EARNINGS.map((row, i) => (
              <tr key={i} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 text-gray-500">{row.date}</td>
                <td className="px-4 py-3 font-medium text-gray-900">{row.client}</td>
                <td className="px-4 py-3 text-gray-600">{row.package}</td>
                <td className="px-4 py-3 text-gray-900">{formatCurrency(row.gross_inr)}</td>
                <td className="px-4 py-3 text-gray-400">{formatCurrency(row.fee_inr)}</td>
                <td className="px-4 py-3 font-semibold text-emerald-600">{formatCurrency(row.net_inr)}</td>
              </tr>
            ))}
            <tr className="bg-gray-50 font-semibold">
              <td className="px-4 py-3 text-gray-900" colSpan={3}>Total</td>
              <td className="px-4 py-3 text-gray-900">{formatCurrency(totalGross)}</td>
              <td className="px-4 py-3 text-gray-400">{formatCurrency(totalFees)}</td>
              <td className="px-4 py-3 text-emerald-600">{formatCurrency(totalNet)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p className="text-xs text-gray-400 mt-4">
        Each accepted lead carries a ₹99 flat platform fee. You keep 100% of all consultation revenue.
      </p>
    </div>
  );
}
