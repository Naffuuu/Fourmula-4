import clsx from "clsx";

/**
 * Scores a password 0-4 using simple heuristics (length + character variety).
 * This is a UX nudge, not a security boundary — the backend independently
 * enforces a minimum policy regardless of what this shows.
 */
export function scorePassword(password) {
  if (!password) return 0;
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  return Math.min(score, 4);
}

const LABELS = ["Too short", "Weak", "Okay", "Strong", "Very strong"];
const COLORS = ["bg-danger-500", "bg-danger-500", "bg-warning-500", "bg-primary-500", "bg-success-500"];

export default function PasswordStrengthMeter({ password }) {
  const score = scorePassword(password);
  if (!password) return null;

  return (
    <div className="flex flex-col gap-1 mt-1">
      <div className="flex gap-1">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className={clsx(
              "h-1.5 flex-1 rounded-full transition-colors duration-200",
              i < score ? COLORS[score] : "bg-primary-100"
            )}
          />
        ))}
      </div>
      <span className="text-xs text-ink-faint">{LABELS[score]}</span>
    </div>
  );
}
