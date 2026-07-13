import clsx from "clsx";

/**
 * Base surface for the app. `interactive` adds hover lift for clickable cards
 * (e.g. mission tiles on the dashboard).
 */
export default function Card({
  as: Component = "div",
  interactive = false,
  padding = "p-6",
  className,
  children,
  ...props
}) {
  return (
    <Component
      className={clsx(
        "bg-paper-card rounded-2xl border border-primary-100 shadow-soft",
        padding,
        interactive &&
          "transition-all duration-200 hover:shadow-soft-lg hover:-translate-y-0.5 hover:border-primary-200 cursor-pointer",
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

export function CardHeader({ title, subtitle, action, className }) {
  return (
    <div className={clsx("flex items-start justify-between gap-4 mb-4", className)}>
      <div>
        <h3 className="font-display text-lg font-semibold text-ink">{title}</h3>
        {subtitle && <p className="text-sm text-ink-soft mt-0.5">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}
