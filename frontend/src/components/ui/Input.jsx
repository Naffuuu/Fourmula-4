import { forwardRef, useState } from "react";
import clsx from "clsx";
import { Eye, EyeOff, AlertCircle, CheckCircle2 } from "lucide-react";

/**
 * Text input with a floating label, inline error/success state, and optional
 * password visibility toggle. Used across signup/login and every mission form.
 */
const Input = forwardRef(function Input(
  { label, error, success, type = "text", hint, className, id, ...props },
  ref
) {
  const [showPassword, setShowPassword] = useState(false);
  const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");
  const isPassword = type === "password";
  const resolvedType = isPassword && showPassword ? "text" : type;

  return (
    <div className={clsx("flex flex-col gap-1.5", className)}>
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-ink-soft">
          {label}
        </label>
      )}
      <div className="relative">
        <input
          ref={ref}
          id={inputId}
          type={resolvedType}
          aria-invalid={!!error}
          aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
          className={clsx(
            "w-full rounded-xl border-2 bg-paper-soft px-4 py-2.5 text-sm text-ink placeholder:text-ink-faint transition-colors",
            "focus:bg-paper-card focus:outline-none",
            error
              ? "border-danger-500 focus:border-danger-500"
              : success
              ? "border-success-500 focus:border-success-500"
              : "border-primary-100 focus:border-primary-500",
            isPassword && "pr-10"
          )}
          {...props}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword((s) => !s)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-faint hover:text-ink-soft"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}
      </div>
      {error && (
        <p id={`${inputId}-error`} className="flex items-center gap-1 text-xs font-medium text-danger-700">
          <AlertCircle className="w-3.5 h-3.5" /> {error}
        </p>
      )}
      {!error && success && (
        <p className="flex items-center gap-1 text-xs font-medium text-success-700">
          <CheckCircle2 className="w-3.5 h-3.5" /> {success}
        </p>
      )}
      {!error && !success && hint && (
        <p id={`${inputId}-hint`} className="text-xs text-ink-faint">
          {hint}
        </p>
      )}
    </div>
  );
});

export default Input;
