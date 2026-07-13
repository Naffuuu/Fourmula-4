import { MessageSquareWarning, Armchair, BookOpenCheck, Wallet, Siren, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import PageWrapper from "../components/layout/PageWrapper";
import Card from "../components/ui/Card";
import StrikeMeter from "../components/ui/StrikeMeter";
import ProgressBar from "../components/ui/ProgressBar";
import MissionTile from "../features/dashboard/MissionTile";
import { useDashboardSummary } from "../features/dashboard/useDashboardSummary";
import { useAuth } from "../hooks/useAuth";

const STUDENT_MISSIONS = [
  { to: "/missions/whistleblower", icon: MessageSquareWarning, title: "Whistleblower", description: "File an anonymous complaint. Your identity is cryptographically protected.", accent: "coral" },
  { to: "/missions/sos", icon: Siren, title: "SOS Flare", description: "Send a real-time alert to on-duty captains.", accent: "coral" },
  { to: "/missions/factchecker", icon: ShieldCheck, title: "Fact-Checker", description: "Check a claimed rule against the seeded rulebook.", accent: "primary" },
  { to: "/missions/ledger", icon: Wallet, title: "Tiffin Ledger", description: "See the running total of the corrupt economy.", accent: "warning" },
  { to: "/missions/syllabus", icon: BookOpenCheck, title: "Syllabus Negotiator", description: "AI-filter the bloated syllabus into what's actually examinable.", accent: "primary" },
];

const CAPTAIN_MISSIONS = [
  { to: "/missions/seating", icon: Armchair, title: "Seat Planner", description: "Generate a line-of-sight-optimized seating chart.", accent: "primary" },
  { to: "/missions/sos", icon: Siren, title: "SOS Console", description: "Live feed of incoming SOS flares from students.", accent: "coral" },
  { to: "/missions/whistleblower", icon: MessageSquareWarning, title: "Strike Review", description: "Review anonymous complaints and issue warnings.", accent: "coral" },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const { summary, loading } = useDashboardSummary();
  const isCaptain = user.role === "second_captain" || user.role === "third_captain";
  const missions = isCaptain ? CAPTAIN_MISSIONS : STUDENT_MISSIONS;

  return (
    <PageWrapper>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold">
            {greeting()}, {user.name.split(" ")[0]}
          </h1>
          <p className="text-ink-soft mt-1">
            {isCaptain
              ? "Here's what's happening across the student body right now."
              : "Here's your Protocol status at a glance."}
          </p>
        </div>
      </div>

      {!loading && summary && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
          <Card as={Link} to="/missions/whistleblower" interactive className="lg:col-span-1 flex flex-col items-center justify-center">
            <StrikeMeter value={summary.strike_count} max={summary.strike_max} />
          </Card>

          <Card as={Link} to="/missions/sos" interactive className="lg:col-span-2">
            <h3 className="font-display font-semibold mb-4">Live status</h3>
            <div className="grid grid-cols-2 gap-6">
              <Stat label="Open SOS alerts" value={summary.open_sos_alerts} tone="coral" />
              <Stat
                label="Next test"
                value={
                  summary.next_test_date
                    ? summary.next_test_date
                    : summary.days_until_test === null
                    ? "—"
                    : `${summary.days_until_test} days`
                }
                tone="primary"
              />
              <div className="col-span-2">
                <ProgressBar
                  value={summary.recent_complaints_count}
                  max={summary.recent_complaints_capacity || 10}
                  tone="warning"
                  label="Recent complaints this week"
                />
              </div>
            </div>
            {summary.recent_complaint_categories?.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-4">
                {summary.recent_complaint_categories.map((cat) => (
                  <span
                    key={cat}
                    className="text-xs font-medium bg-primary-50 text-primary-700 rounded-full px-2.5 py-1"
                  >
                    {cat}
                  </span>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}

      <h2 className="font-display font-semibold text-lg mb-4">Missions</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {missions.map((m) => (
          <MissionTile key={m.to} {...m} />
        ))}
      </div>
    </PageWrapper>
  );
}

function Stat({ label, value, tone }) {
  const TONE_TEXT = { coral: "text-coral-600", primary: "text-primary-600" };
  return (
    <div>
      <p className={`font-display text-3xl font-extrabold ${TONE_TEXT[tone]}`}>{value}</p>
      <p className="text-xs text-ink-faint font-medium uppercase tracking-wide mt-1">{label}</p>
    </div>
  );
}

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}
