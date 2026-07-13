import { useEffect, useState } from "react";
import { Siren, Wifi, WifiOff } from "lucide-react";
import PageWrapper from "../../components/layout/PageWrapper";
import Card, { CardHeader } from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import api from "../../lib/apiClient";
import { useAuth } from "../../hooks/useAuth";
import { useWebSocket } from "../../hooks/useWebSocket";
import { useToast } from "../../context/ToastContext";

const LOCATIONS = [
  "Classroom 301",
  "2nd Floor Corridor, Block B",
  "Cafeteria",
  "Sports Ground",
  "Library",
  "Main Gate",
];

export default function SosPage() {
  const { user } = useAuth();
  const isCaptain = user.role === "second_captain" || user.role === "third_captain";
  return isCaptain ? <CaptainSosConsole /> : <StudentSosButton />;
}

function StudentSosButton() {
  const { push } = useToast();
  const [location, setLocation] = useState(LOCATIONS[0]);
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const send = async () => {
    setSending(true);
    try {
      await api.post("/sos", { location });
      setSent(true);
      push({ type: "success", message: "SOS sent to on-duty captains." });
    } catch {
      push({ type: "error", message: "Could not send SOS. Try again — this matters." });
    } finally {
      setSending(false);
    }
  };

  return (
    <PageWrapper maxWidth="max-w-md">
      <div className="text-center">
        <h1 className="font-display text-2xl font-extrabold mb-1">SOS Rescue Flare</h1>
        <p className="text-ink-soft mb-8">Send a real-time alert to on-duty captains.</p>

        <Card className="flex flex-col items-center gap-6 py-10">
          <label className="w-full text-left">
            <span className="text-sm font-medium text-ink-soft">Where are you?</span>
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full mt-1.5 rounded-xl border-2 border-primary-100 px-4 py-2.5 text-sm focus:border-primary-500 focus:outline-none"
            >
              {LOCATIONS.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </label>

          <button
            onClick={send}
            disabled={sending}
            className="w-36 h-36 rounded-full bg-coral-500 hover:bg-coral-600 active:scale-95 transition-all shadow-soft-lg flex flex-col items-center justify-center text-white disabled:opacity-60"
          >
            <Siren className="w-10 h-10 mb-1" />
            <span className="font-display font-bold">SOS</span>
          </button>

          {sent && <Badge tone="success">Sent — captains have been notified</Badge>}
        </Card>
      </div>
    </PageWrapper>
  );
}

function CaptainSosConsole() {
  const [alerts, setAlerts] = useState([]);
  const { status, send } = useWebSocket("/api/v1/sos/ws", {
    onMessage: (msg) => {
      if (msg.event === "sos_triggered") {
        setAlerts((a) => [msg.alert, ...a]);
      }
    },
  });
  // eslint-disable-next-line no-unused-vars
  void send;

  useEffect(() => {
    (async () => {
      const { data } = await api.get("/sos");
      setAlerts(data);
    })();
  }, []);

  return (
    <PageWrapper maxWidth="max-w-2xl">
      <div className="flex items-center justify-between mb-1">
        <h1 className="font-display text-2xl font-extrabold">SOS Console</h1>
        <Badge tone={status === "open" ? "success" : "warning"} icon={status === "open" ? Wifi : WifiOff}>
          {status === "open" ? "Live" : "Reconnecting..."}
        </Badge>
      </div>
      <p className="text-ink-soft mb-6">Live feed of incoming SOS flares from students.</p>

      <Card>
        <CardHeader title="Recent alerts" />
        {alerts.length === 0 ? (
          <p className="text-sm text-ink-faint py-6 text-center">No alerts yet. This feed updates in real time.</p>
        ) : (
          <div className="divide-y divide-primary-50">
            {alerts.map((a) => (
              <div key={a.id} className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Siren className="w-4 h-4 text-coral-500" />
                  <div>
                    <p className="font-semibold text-sm">{a.location}</p>
                    <p className="text-xs text-ink-faint">{new Date(a.triggered_at).toLocaleString()}</p>
                  </div>
                </div>
                <Badge tone={a.status === "active" ? "danger" : "neutral"}>{a.status}</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>
    </PageWrapper>
  );
}
