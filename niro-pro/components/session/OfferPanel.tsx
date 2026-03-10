"use client";
import { useState } from "react";
import { MOCK_PACKAGES } from "@/lib/mock-data";
import { simulateOfferSend } from "@/lib/simulate";
import { formatCurrency } from "@/lib/utils";
import Button from "@/components/ui/Button";
import { Copy, Check } from "lucide-react";

export default function OfferPanel({ clientName, onOfferSent }: { clientName: string; onOfferSent: () => void }) {
  const [selectedPkg, setSelectedPkg] = useState(MOCK_PACKAGES[0].id);
  const [customOffer, setCustomOffer] = useState(false);
  const [customTitle, setCustomTitle] = useState("");
  const [customPrice, setCustomPrice] = useState("");
  const [expiryHours, setExpiryHours] = useState(24);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [template, setTemplate] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const sortedPackages = [...MOCK_PACKAGES].sort((a, b) => a.price_inr - b.price_inr);

  async function handleSend() {
    setSending(true);
    let packageName: string;
    let price: number;
    if (customOffer) {
      packageName = customTitle;
      price = Number(customPrice);
    } else {
      const found = sortedPackages.find(p => p.id === selectedPkg)!;
      packageName = found.name;
      price = found.price_inr;
    }
    const result = await simulateOfferSend({
      clientName,
      packageName,
      price,
      expiryHours,
    });
    setSending(false);
    setTemplate(result.whatsapp_template);
    onOfferSent();
  }

  function copy() {
    if (template) navigator.clipboard.writeText(template);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100";

  return (
    <div className="bg-white rounded-xl border border-violet-200 shadow-md p-5">
      <h3 className="font-semibold text-gray-900 mb-4">Send {clientName} an offer</h3>

      {!template ? (
        <>
          <div className="space-y-2 mb-4">
            {sortedPackages.map((pkg, i) => (
              <label key={pkg.id} className={`flex items-center gap-3 rounded-lg px-3 py-2.5 cursor-pointer border transition-colors ${!customOffer && selectedPkg === pkg.id ? "border-violet-300 bg-violet-50" : "border-gray-100 bg-gray-50 hover:bg-gray-100"}`}>
                <input type="radio" name="pkg" value={pkg.id} checked={!customOffer && selectedPkg === pkg.id} onChange={() => { setSelectedPkg(pkg.id); setCustomOffer(false); }} className="text-violet-600" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{pkg.name}</p>
                  {i === 0 && <p className="text-xs text-violet-600">★ Recommended for first-time clients</p>}
                </div>
                <span className="text-sm font-bold text-gray-900 shrink-0">{formatCurrency(pkg.price_inr)}</span>
              </label>
            ))}
            <label className={`flex items-center gap-3 rounded-lg px-3 py-2.5 cursor-pointer border transition-colors ${customOffer ? "border-violet-300 bg-violet-50" : "border-gray-100 bg-gray-50 hover:bg-gray-100"}`}>
              <input type="radio" name="pkg" checked={customOffer} onChange={() => setCustomOffer(true)} className="text-violet-600" />
              <p className="text-sm font-medium text-gray-700">Custom offer</p>
            </label>
          </div>

          {customOffer && (
            <div className="grid grid-cols-2 gap-2 mb-4">
              <div className="col-span-2"><input className={inputCls} placeholder="Offer title" value={customTitle} onChange={e => setCustomTitle(e.target.value)} /></div>
              <input className={inputCls} placeholder="₹ Price" type="number" value={customPrice} onChange={e => setCustomPrice(e.target.value)} />
              <select className={inputCls} value={expiryHours} onChange={e => setExpiryHours(Number(e.target.value))}>
                <option value={24}>Expires 24h</option>
                <option value={48}>Expires 48h</option>
                <option value={72}>Expires 72h</option>
              </select>
            </div>
          )}

          <div className="mb-4">
            <textarea
              className={`${inputCls} resize-none`}
              rows={2}
              placeholder="Personal message (optional)"
              value={message}
              onChange={e => setMessage(e.target.value)}
              maxLength={200}
            />
          </div>

          <Button className="w-full" loading={sending} onClick={handleSend}>Send Offer</Button>
        </>
      ) : (
        <div>
          <p className="text-sm font-medium text-emerald-600 mb-3">✓ Offer sent! Complete your debrief below.</p>
          <div className="bg-gray-50 rounded-lg p-3 mb-3">
            <p className="text-xs text-gray-400 font-medium mb-2">WhatsApp template</p>
            <pre className="text-xs text-gray-700 whitespace-pre-wrap font-sans">{template}</pre>
          </div>
          <button
            onClick={copy}
            className="flex items-center gap-2 text-sm font-medium text-violet-600 hover:text-violet-700"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            {copied ? "Copied ✓" : "Copy to WhatsApp"}
          </button>
        </div>
      )}
    </div>
  );
}
