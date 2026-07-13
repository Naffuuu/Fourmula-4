import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import Card from "../../components/ui/Card";
import Badge from "../../components/ui/Badge";

export default function MissionTile({ to, icon: Icon, title, description, badge, accent = "primary" }) {
  const ACCENTS = {
    primary: "bg-primary-50 text-primary-600",
    coral: "bg-coral-100 text-coral-600",
    warning: "bg-warning-50 text-warning-700",
  };

  return (
    <Card as={Link} to={to} interactive className="flex flex-col h-full">
      <div className="flex items-start justify-between">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${ACCENTS[accent]}`}>
          <Icon className="w-5 h-5" />
        </div>
        <ArrowUpRight className="w-4 h-4 text-ink-faint" />
      </div>
      <h3 className="font-display font-semibold text-ink mt-3">{title}</h3>
      <p className="text-sm text-ink-soft mt-1 flex-1">{description}</p>
      {badge && (
        <Badge tone={badge.tone} className="mt-3 self-start">
          {badge.label}
        </Badge>
      )}
    </Card>
  );
}
