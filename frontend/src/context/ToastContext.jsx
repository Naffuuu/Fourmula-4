import { createContext, useCallback, useContext, useState } from "react";
import { createPortal } from "react-dom";
import clsx from "clsx";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";

const ToastContext = createContext(null);

const ICONS = { success: CheckCircle2, error: AlertCircle, info: Info };
const TONES = {
  success: "bg-success-50 text-success-700 border-success-500",
  error: "bg-danger-50 text-danger-700 border-danger-500",
  info: "bg-primary-50 text-primary-700 border-primary-500",
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismiss = useCallback((id) => {
    setToasts((t) => t.filter((toast) => toast.id !== id));
  }, []);

  const push = useCallback(
    ({ message, type = "info", duration = 4000 }) => {
      const id = crypto.randomUUID();
      setToasts((t) => [...t, { id, message, type }]);
      if (duration) setTimeout(() => dismiss(id), duration);
      return id;
    },
    [dismiss]
  );

  return (
    <ToastContext.Provider value={{ push, dismiss }}>
      {children}
      {createPortal(
        <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 w-full max-w-sm">
          {toasts.map((toast) => {
            const Icon = ICONS[toast.type];
            return (
              <div
                key={toast.id}
                role="status"
                className={clsx(
                  "flex items-start gap-2 rounded-xl border-l-4 shadow-soft-lg px-4 py-3 animate-pop-in bg-paper-card",
                  TONES[toast.type]
                )}
              >
                <Icon className="w-4 h-4 mt-0.5 shrink-0" />
                <p className="text-sm font-medium flex-1">{toast.message}</p>
                <button
                  onClick={() => dismiss(toast.id)}
                  aria-label="Dismiss notification"
                  className="text-ink-faint hover:text-ink"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })}
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within a ToastProvider");
  return ctx;
}
