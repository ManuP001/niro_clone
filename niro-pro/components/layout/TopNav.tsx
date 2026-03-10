"use client";
import { Bell, X, Copy, Check } from "lucide-react";
import { useState } from "react";
import { MOCK_NOTIFICATIONS } from "@/lib/mock-data";
import { Notification } from "@/lib/types";

export default function TopNav() {
  const [notifications, setNotifications] = useState<Notification[]>(MOCK_NOTIFICATIONS);
  const [panelOpen, setPanelOpen] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  function copyTemplate(notif: Notification) {
    navigator.clipboard.writeText(notif.whatsapp_template);
    setCopiedId(notif.id);
    setTimeout(() => setCopiedId(null), 2000);
  }

  function dismiss(id: string) {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }

  return (
    <div className="relative">
      <button
        onClick={() => setPanelOpen(!panelOpen)}
        className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <Bell className="w-5 h-5" />
        {notifications.length > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
            {notifications.length}
          </span>
        )}
      </button>

      {panelOpen && (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setPanelOpen(false)} />
          <div className="absolute right-0 top-12 w-80 bg-white rounded-xl shadow-lg border border-gray-100 z-40">
            <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
              <span className="font-semibold text-gray-900 text-sm">Notifications</span>
              <button onClick={() => setPanelOpen(false)}><X className="w-4 h-4 text-gray-400" /></button>
            </div>
            {notifications.length === 0 ? (
              <p className="px-4 py-6 text-sm text-gray-400 text-center">All caught up ✓</p>
            ) : (
              notifications.map(n => (
                <div key={n.id} className="px-4 py-3 border-b border-gray-50 last:border-0">
                  <p className="text-sm text-gray-700 mb-2">{n.message}</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => copyTemplate(n)}
                      className="flex items-center gap-1.5 text-xs font-medium text-violet-600 hover:text-violet-700 bg-violet-50 hover:bg-violet-100 px-2 py-1 rounded-md transition-colors"
                    >
                      {copiedId === n.id ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                      {copiedId === n.id ? "Copied ✓" : "Copy WhatsApp"}
                    </button>
                    <button
                      onClick={() => dismiss(n.id)}
                      className="text-xs text-gray-400 hover:text-gray-600 px-2 py-1 rounded-md hover:bg-gray-50 transition-colors"
                    >
                      Mark done
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
}
