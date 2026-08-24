import { NavLink } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";

export default function Sidebar({ collapsed, open, isDark, toggleSidebar, toggleTheme }) {
  const { t } = useLanguage();
  let className = "sidebar";
  if (collapsed) className += " collapsed";
  if (open) className += " open"; // mobile menu

  return (
    <aside id="sidebar" className={className}>
      <div className="sidebar-header">
        <span className="logo-text">Simpantun</span>
        <button className="toggle-btn" onClick={toggleSidebar}>
          <i className="fas fa-bars"></i>
        </button>
      </div>
      <nav className="sidebar-nav">
        <NavLink
          to="/"
          className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}
          end
        >
          <i className="fas fa-camera"></i>
          <span className="nav-label">{t("nav_scan")}</span>
        </NavLink>
        <NavLink
          to="/result"
          className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}
        >
          <i className="fas fa-clipboard-list"></i>
          <span className="nav-label">{t("nav_results")}</span>
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}
        >
          <i className="fa-solid fa-clock-rotate-left"></i>
          <span className="nav-label">{t("nav_history")}</span>
        </NavLink>

        <NavLink
          to="/guide"
          className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}
        >
          <i className="fas fa-circle-info"></i>
          <span className="nav-label">{t("nav_guide")}</span>
        </NavLink>
      </nav>
      <div className="sidebar-footer">
        <button className="theme-btn" onClick={toggleTheme}>
          <i id="theme-icon" className={isDark ? "fas fa-sun text-yellow-400" : "fas fa-moon"} style={{ color: isDark ? "#facc15" : "" }}></i>
          <span className="nav-label" id="theme-text">{isDark ? t("theme_light") : t("theme_dark")}</span>
        </button>
      </div>
    </aside>
  );
}
