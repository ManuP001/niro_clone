"use client";
import { useEffect, useState } from "react";
import { Mic, MicOff, Video, VideoOff, PhoneOff } from "lucide-react";
import { clsx } from "clsx";

export default function SimulatedVideo({ clientName, onEnd }: { clientName: string; onEnd: () => void }) {
  const [waiting, setWaiting] = useState(true);
  const [muted, setMuted] = useState(false);
  const [cameraOff, setCameraOff] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setWaiting(false), 3000);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="relative bg-gray-900 rounded-xl overflow-hidden aspect-video w-full">
      {/* Main video — client */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center">
        {!waiting && (
          <div
            className="w-20 h-20 rounded-full bg-gray-600 flex items-center justify-center text-gray-400 text-2xl font-bold"
            style={{ animation: "pulse 3s ease-in-out infinite" }}
          >
            {clientName[0]}
          </div>
        )}
        {waiting && (
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-white/30 border-t-white/80 rounded-full animate-spin mx-auto mb-2" />
            <p className="text-white/60 text-sm">Waiting for {clientName} to join...</p>
          </div>
        )}
      </div>
      {/* Client label */}
      {!waiting && (
        <div className="absolute bottom-3 left-3 bg-black/40 backdrop-blur-sm text-white text-xs px-2 py-1 rounded-md font-medium">
          {clientName}
        </div>
      )}
      {/* Picture-in-picture — self */}
      <div className={clsx("absolute bottom-3 right-3 w-24 h-16 rounded-lg overflow-hidden bg-gradient-to-br from-gray-700 to-gray-800 border border-white/10 flex items-center justify-center", cameraOff && "opacity-50")}>
        {cameraOff ? <VideoOff className="w-4 h-4 text-gray-400" /> : <div className="text-gray-500 text-xs">You</div>}
        <div className="absolute bottom-1 left-1 bg-black/40 text-white text-xs px-1 rounded">You</div>
      </div>
      {/* Controls */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex items-center gap-3">
        <button
          onClick={() => setMuted(m => !m)}
          className={clsx("w-9 h-9 rounded-full flex items-center justify-center transition-colors", muted ? "bg-red-500 text-white" : "bg-white/20 text-white hover:bg-white/30")}
        >
          {muted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </button>
        <button
          onClick={() => setCameraOff(c => !c)}
          className={clsx("w-9 h-9 rounded-full flex items-center justify-center transition-colors", cameraOff ? "bg-red-500 text-white" : "bg-white/20 text-white hover:bg-white/30")}
        >
          {cameraOff ? <VideoOff className="w-4 h-4" /> : <Video className="w-4 h-4" />}
        </button>
        <button
          onClick={onEnd}
          className="w-9 h-9 rounded-full bg-red-600 text-white flex items-center justify-center hover:bg-red-700 transition-colors"
        >
          <PhoneOff className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
