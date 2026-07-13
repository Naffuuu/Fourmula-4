import { Link, useNavigate } from "react-router-dom";
import { LogOut, ShieldAlert, Menu } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import Button from "../ui/Button";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-40 bg-paper-card/90 backdrop-blur border-b border-primary-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <Link to="/dashboard" className="flex items-center gap-2 font-display font-extrabold text-lg text-primary-700">
          <ShieldAlert className="w-6 h-6 text-coral-500" />
          Anti-Kuddus Protocol
        </Link>

        {user && (
          <div className="hidden sm:flex items-center gap-4">
            <div className="flex items-center gap-2">
              <img
                src={user.avatar_url || `https://api.dicebear.com/9.x/thumbs/svg?seed=${user.id}`}
                alt=""
                className="w-8 h-8 rounded-full border-2 border-primary-200"
              />
              <div className="text-sm leading-tight">
                <p className="font-semibold text-ink">{user.name}</p>
                <p className="text-ink-faint capitalize text-xs">{user.role.replace("_", " ")}</p>
              </div>
            </div>
            <Button variant="ghost" size="sm" icon={LogOut} onClick={handleLogout}>
              Log out
            </Button>
          </div>
        )}

        <button
          className="sm:hidden text-ink-soft"
          onClick={() => setMobileOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          <Menu className="w-6 h-6" />
        </button>
      </div>

      {mobileOpen && user && (
        <div className="sm:hidden border-t border-primary-100 px-4 py-3 flex items-center justify-between">
          <span className="text-sm font-semibold text-ink">{user.name}</span>
          <Button variant="ghost" size="sm" icon={LogOut} onClick={handleLogout}>
            Log out
          </Button>
        </div>
      )}
    </header>
  );
}
