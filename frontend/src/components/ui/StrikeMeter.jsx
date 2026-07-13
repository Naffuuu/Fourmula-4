import clsx from "clsx";

/**
 * The Strike Meter — the app's signature element.
 *
 * Styled like a torn scrap of "wanted poster" paper with a hand-drawn arc dial
 * burned into it. Used on the dashboard, the whistleblower mission, and the
 * ledger — anywhere a strike/warning count needs to feel consequential rather
 * than like a generic progress bar. `max` is normally 3 (three strikes).
 */
export default function StrikeMeter({ value, max = 3, size = 180, caption = "Warnings" }) {
  const radius = 70;
  const circumference = Math.PI * radius; // half circle
  const pct = Math.max(0, Math.min(1, value / max));
  const offset = circumference * (1 - pct);

  const tone =
    value >= max ? "text-danger-500 stroke-danger-500" : value === max - 1 ? "text-warning-500 stroke-warning-500" : "text-primary-500 stroke-primary-500";

  return (
    <div
      className="relative torn-edge bg-[#F5EFDD] rounded-lg px-6 pt-5 pb-3 shadow-poster rotate-[-1deg]"
      style={{ width: size + 40 }}
    >
      <div className="absolute inset-0 torn-edge bg-[radial-gradient(ellipse_at_top,rgba(0,0,0,0.03),transparent_70%)] pointer-events-none" />
      <p className="text-center text-[10px] tracking-[0.2em] uppercase font-display font-bold text-ink-soft mb-1">
        Wanted: Compliance
      </p>
      <svg viewBox={`0 0 ${size} ${size / 2 + 20}`} className="w-full">
        <path
          d={`M 20 ${size / 2 + 10} A ${radius} ${radius} 0 0 1 ${size - 20} ${size / 2 + 10}`}
          fill="none"
          stroke="#E7DCC0"
          strokeWidth="14"
          strokeLinecap="round"
        />
        <path
          d={`M 20 ${size / 2 + 10} A ${radius} ${radius} 0 0 1 ${size - 20} ${size / 2 + 10}`}
          fill="none"
          strokeWidth="14"
          strokeLinecap="round"
          className={clsx(tone, "animate-meter-fill")}
          stroke="currentColor"
          strokeDasharray={circumference}
          style={{ "--meter-start": circumference, "--meter-end": offset }}
        />
      </svg>
      <div className="text-center -mt-6">
        <span className={clsx("font-display text-3xl font-extrabold", tone)}>{value}</span>
        <span className="font-display text-lg font-semibold text-ink-faint">/{max}</span>
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mt-0.5">{caption}</p>
      </div>
    </div>
  );
}
