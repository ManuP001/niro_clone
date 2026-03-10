"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import OnboardingLayout from "@/components/onboarding/OnboardingLayout";
import { MOCK_PRACTITIONER, MOCK_PACKAGES } from "@/lib/mock-data";
import { simulateTextCleanup } from "@/lib/simulate";
import { formatCurrency, getInitials } from "@/lib/utils";
import { IdentityForm, StoryForm, Package } from "@/lib/types";
import Button from "@/components/ui/Button";

export default function PreviewPage() {
  const router = useRouter();
  const [identity, setIdentity] = useState<IdentityForm | null>(null);
  const [story, setStory] = useState<StoryForm | null>(null);
  const [packages, setPackages] = useState<Package[]>(MOCK_PACKAGES);
  const [photos, setPhotos] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [diffResult, setDiffResult] = useState<{ corrected: string; changes: string[] } | null>(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const id = localStorage.getItem("niro_onboarding_identity");
    const st = localStorage.getItem("niro_onboarding_story");
    const pk = localStorage.getItem("niro_onboarding_packages");
    const ph = localStorage.getItem("niro_onboarding_photos");
    if (id) setIdentity(JSON.parse(id));
    if (st) setStory(JSON.parse(st));
    if (pk) setPackages(JSON.parse(pk));
    if (ph) setPhotos(JSON.parse(ph));
  }, []);

  const data = {
    name: identity?.full_name ?? MOCK_PRACTITIONER.full_name,
    tradition: identity?.primary_tradition ?? MOCK_PRACTITIONER.primary_tradition,
    city: identity?.city ?? MOCK_PRACTITIONER.city,
    years: identity?.years_of_practice ?? MOCK_PRACTITIONER.years_of_practice,
    languages: identity?.languages ?? MOCK_PRACTITIONER.languages,
    philosophy: story?.philosophy ?? MOCK_PRACTITIONER.philosophy,
  };

  async function handleSubmit() {
    setSubmitting(true);
    const result = await simulateTextCleanup(data.philosophy);
    setSubmitting(false);
    if (result.changes_made) {
      setDiffResult({ corrected: result.corrected, changes: result.changes });
    } else {
      doSubmit();
    }
  }

  function doSubmit() {
    setDiffResult(null);
    ["niro_onboarding_identity","niro_onboarding_story","niro_onboarding_specializations","niro_onboarding_packages","niro_onboarding_photos"].forEach(k => localStorage.removeItem(k));
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="text-5xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Profile submitted!</h2>
          <p className="text-gray-500 mb-8">Manu will review within 48 hours. You&apos;ll receive a WhatsApp message when approved.</p>
          <Button size="lg" onClick={() => router.push("/dashboard")}>Go to Dashboard →</Button>
        </div>
      </div>
    );
  }

  return (
    <OnboardingLayout step={6} totalSteps={6} percent={100} backHref="/onboarding/photos" onContinue={handleSubmit} continueLabel="Submit My Profile →" continueLoading={submitting}>
      <h2 className="text-2xl font-bold text-gray-900 mb-1">Preview your profile</h2>
      <p className="text-gray-400 text-sm mb-6">This is what clients will see.</p>

      {diffResult && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6">
          <p className="text-sm font-semibold text-yellow-800 mb-2">Suggested improvement:</p>
          <p className="text-sm text-gray-700 bg-yellow-100 rounded p-2 mb-3">{diffResult.corrected}</p>
          <p className="text-xs text-gray-500 mb-3">Change: {diffResult.changes.join(", ")}</p>
          <div className="flex gap-3">
            <Button size="sm" onClick={doSubmit}>Accept</Button>
            <Button size="sm" variant="secondary" onClick={doSubmit}>Keep Original</Button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center gap-4 mb-4">
          {photos[0] ? (
            <img src={photos[0]} alt="" className="w-16 h-16 rounded-full object-cover" />
          ) : (
            <div className="w-16 h-16 rounded-full bg-violet-100 flex items-center justify-center text-violet-600 font-bold text-lg">
              {getInitials(data.name)}
            </div>
          )}
          <div>
            <h3 className="text-lg font-bold text-gray-900">{data.name}</h3>
            <p className="text-sm text-gray-500">{data.tradition} · {data.city} · {data.years} years</p>
            <div className="flex gap-1 mt-1 flex-wrap">
              {data.languages.map((l: string) => <span key={l} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{l}</span>)}
            </div>
          </div>
        </div>
        <p className="text-sm text-gray-600 mb-4 line-clamp-3">{data.philosophy}</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {packages.map(pkg => (
            <div key={pkg.id} className="border border-gray-100 rounded-lg p-3">
              <p className="text-sm font-semibold text-gray-900">{pkg.name}</p>
              <p className="text-xs text-gray-400 mt-0.5">{pkg.sessions_included} session · {pkg.duration_days} days</p>
              <p className="text-sm font-bold text-violet-600 mt-1">{formatCurrency(pkg.price_inr)}</p>
            </div>
          ))}
        </div>
      </div>
    </OnboardingLayout>
  );
}
