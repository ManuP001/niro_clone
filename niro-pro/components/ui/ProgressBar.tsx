interface ProgressBarProps {
  percent: number;
  step: number;
  totalSteps: number;
}

export default function ProgressBar({ percent, step, totalSteps }: ProgressBarProps) {
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>Step {step} of {totalSteps}</span>
        <span>{percent}%</span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-violet-600 rounded-full transition-all duration-500"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
