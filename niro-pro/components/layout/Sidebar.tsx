"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, Package, DollarSign, Settings, Menu, X } from "lucide-react";
import { clsx } from "clsx";
import { useState } from "react";
import { MOCK_PRACTITIONER, MOCK_LEADS, MOCK_NOTIFICATIONS } from "@/lib/mock-data";
import { getInitials } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/leads", label: "Leads", icon: Users },
  { href: "/packages", label: "Packages", icon: Package },
  { href: "/earnings", label: "Earnings", icon: DollarSign },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const pendingCount = MOCK_LEADS.filter(l => l.status === "pending").length;

  const NavContent = () => (
    <div className="flex flex-col h-full">
      <div className="px-6 py-5 border-b border-white/10">
        <span className="text-white font-bold text-xl tracking-wide">NIRO ✦</span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              onClick={() => setOpen(false)}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                active
                  ? "bg-violet-600 text-white"
                  : "text-white/70 hover:text-white hover:bg-white/10"
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {label}
              {label === "Leads" && pendingCount > 0 && (
                <span className="ml-auto bg-red-500 text-white text-xs font-bold px-1.5 py-0.5 rounded-full">
                  {pendingCount}
                </span>
              )}
            </Link>
          );
        })}
      </nav>
      <div className="px-4 py-4 border-t border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-violet-400 flex items-center justify-center text-white text-xs font-bold shrink-0">
            {getInitials(MOCK_PRACTITIONER.full_name)}
          </div>
          <div className="min-w-0">
            <p className="text-white text-sm font-medium truncate">{MOCK_PRACTITIONER.full_name}</p>
            <p className="text-white/50 text-xs truncate">{MOCK_PRACTITIONER.primary_tradition}</p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile toggle */}
      <button
        className="fixed top-4 left-4 z-50 lg:hidden bg-[#1E1B4B] text-white p-2 rounded-lg"
        onClick={() => setOpen(!open)}
      >
        {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Mobile drawer */}
      <div className={clsx(
        "fixed inset-y-0 left-0 w-64 bg-[#1E1B4B] z-40 lg:hidden transition-transform",
        open ? "translate-x-0" : "-translate-x-full"
      )}>
        <NavContent />
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0 bg-[#1E1B4B]">
        <NavContent />
      </div>
    </>
  );
}
