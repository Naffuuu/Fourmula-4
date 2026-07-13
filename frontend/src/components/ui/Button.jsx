import { forwardRef } from "react";
import clsx from "clsx";
import { Loader2 } from "lucide-react";

const VARIANTS = {
  primary:
    "bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700 shadow-soft",
  coral:
    "bg-coral-500 text-white hover:bg-coral-600 active:bg-coral-700 shadow-soft",
  outline:
    "bg-transparent border-2 border-primary-500 text-primary-700 hover:bg-primary-50",
  ghost: "bg-transparent text-ink-soft hover:bg-primary-50 hover:text-primary-700",
  danger: "bg-danger-500 text-white hover:bg-danger-700 shadow-soft",
};

const SIZES = {
  sm: "text-sm px-3 py-1.5 gap-1.5",
  md: "text-sm px-4 py-2.5 gap-2",
  lg: "text-base px-6 py-3 gap-2",
};

/**
 * Base button for the whole app. Every interactive action funnels through this
 * (or IconButton below) so hover/focus/disabled/loading states stay consistent.
 */
const Button = forwardRef(function Button(
  {
    as: Component = "button",
    variant = "primary",
    size = "md",
    loading = false,
    disabled = false,
    icon: Icon,
    iconPosition = "left",
    className,
    children,
    ...props
  },
  ref
) {
  const isDisabled = disabled || loading;

  return (
    <Component
      ref={ref}
      disabled={isDisabled}
      aria-disabled={isDisabled}
      aria-busy={loading || undefined}
      className={clsx(
        "inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-150",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none",
        "active:scale-[0.98]",
        VARIANTS[variant],
        SIZES[size],
        className
      )}
      {...props}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />}
      {!loading && Icon && iconPosition === "left" && (
        <Icon className="w-4 h-4" aria-hidden="true" />
      )}
      {children}
      {!loading && Icon && iconPosition === "right" && (
        <Icon className="w-4 h-4" aria-hidden="true" />
      )}
    </Component>
  );
});

export default Button;
