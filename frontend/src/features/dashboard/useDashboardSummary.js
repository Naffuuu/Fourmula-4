import { useEffect, useState } from "react";
import api from "../../lib/apiClient";

/**
 * Pulls the aggregated /dashboard/summary endpoint — real numbers computed
 * server-side (strike count, open SOS alerts, recent complaint categories,
 * next test countdown), never hardcoded in the frontend.
 */
export function useDashboardSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { data } = await api.get("/dashboard/summary");
        if (!cancelled) setSummary(data);
      } catch (err) {
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return { summary, loading, error };
}
