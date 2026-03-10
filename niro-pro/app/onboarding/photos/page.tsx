"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import OnboardingLayout from "@/components/onboarding/OnboardingLayout";
import { X, Star } from "lucide-react";

export default function PhotosPage() {
  const router = useRouter();
  const [photos, setPhotos] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem("niro_onboarding_photos");
    if (saved) setPhotos(JSON.parse(saved));
  }, []);

  function handleFiles(files: FileList | null) {
    if (!files) return;
    setError(null);
    Array.from(files).forEach(file => {
      if (file.size > 3 * 1024 * 1024) { setError("File too large — max 3MB"); return; }
      if (photos.length >= 3) return;
      const reader = new FileReader();
      reader.onload = e => {
        const b64 = e.target?.result as string;
        setPhotos(prev => {
          const next = [...prev, b64].slice(0, 3);
          localStorage.setItem("niro_onboarding_photos", JSON.stringify(next));
          return next;
        });
      };
      reader.readAsDataURL(file);
    });
  }

  function remove(idx: number) {
    setPhotos(prev => {
      const next = prev.filter((_, i) => i !== idx);
      localStorage.setItem("niro_onboarding_photos", JSON.stringify(next));
      return next;
    });
  }

  function save() {
    localStorage.setItem("niro_onboarding_photos", JSON.stringify(photos));
    router.push("/onboarding/preview");
  }

  return (
    <OnboardingLayout step={5} totalSteps={6} percent={83} backHref="/onboarding/packages" onContinue={save}>
      <h2 className="text-2xl font-bold text-gray-900 mb-1">Profile photos</h2>
      <p className="text-gray-400 text-sm mb-6">Add up to 3 photos. Your first photo is your primary profile picture.</p>

      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={e => e.preventDefault()}
        onDrop={e => { e.preventDefault(); handleFiles(e.dataTransfer.files); }}
        className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center cursor-pointer hover:border-violet-300 hover:bg-violet-50/30 transition-colors mb-4"
      >
        <p className="text-gray-400 text-sm">Click or drag photos here</p>
        <p className="text-gray-300 text-xs mt-1">Max 3MB per photo · Max 3 photos</p>
        <input ref={inputRef} type="file" accept="image/*" multiple className="hidden" onChange={e => handleFiles(e.target.files)} />
      </div>

      {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

      <div className="flex gap-4 flex-wrap">
        {photos.map((src, i) => (
          <div key={i} className="relative">
            <img src={src} alt="" className="w-24 h-24 rounded-full object-cover border-2 border-gray-100" />
            {i === 0 && <span className="absolute -top-1 -right-1 bg-amber-400 text-white rounded-full w-5 h-5 flex items-center justify-center"><Star className="w-3 h-3" /></span>}
            <button onClick={() => remove(i)} className="absolute -bottom-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center hover:bg-red-600">
              <X className="w-3 h-3" />
            </button>
          </div>
        ))}
        {photos.length === 0 && (
          <div className="w-24 h-24 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 text-xl font-bold">KS</div>
        )}
      </div>
    </OnboardingLayout>
  );
}
