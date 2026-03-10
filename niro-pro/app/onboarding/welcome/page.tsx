"use client";
import { useRouter } from "next/navigation";
import Button from "@/components/ui/Button";

export default function WelcomePage() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="text-center max-w-lg">
        <p className="text-[#1E1B4B] font-bold text-2xl mb-2">NIRO ✦</p>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">Welcome, Kavita</h1>
        <p className="text-gray-500 text-lg mb-10">You are 6 steps away from your Niro practitioner profile.</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
          {[
            { icon: "💰", title: "You keep 100%", desc: "Of all consultation revenue" },
            { icon: "🎯", title: "Right clients only", desc: "Pre-qualified by Niro AI" },
            { icon: "🏛", title: "Your practice", desc: "Your rules, your packages" },
          ].map(card => (
            <div key={card.title} className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm text-center">
              <div className="text-2xl mb-2">{card.icon}</div>
              <p className="font-semibold text-gray-900 text-sm">{card.title}</p>
              <p className="text-gray-400 text-xs mt-1">{card.desc}</p>
            </div>
          ))}
        </div>
        <Button size="lg" onClick={() => router.push("/onboarding/identity")}>Start My Profile →</Button>
      </div>
    </div>
  );
}
