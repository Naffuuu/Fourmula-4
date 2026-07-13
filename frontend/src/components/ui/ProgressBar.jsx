import clsx from "clsx";

const TONES = {
  primary: "bg-primary-500",
  coral: "bg-coral-500",
  success: "bg-success-500",
  warning: "bg-warning-500",
  danger: "bg-danger-500",
};

export default function ProgressBar({ value, max = 100, tone = "primary", label, className }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));

  return (
    <div className={clsx("w-full", className)}>
      {label && (
        <div className="flex justify-between text-xs font-medium text-ink-soft mb-1">
          <span>{label}</span>
          <span>
            {value}/{max}
          </span>
        </div>
      )}
      <div
        className="h-2.5 w-full rounded-full bg-primary-50 overflow-hidden"
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      >
        <div
          className={clsx("h-full rounded-full transition-all duration-700 ease-out", TONES[tone])}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
