import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ScanPage from "./pages/ScanPage";
import ResultPage from "./pages/ResultPage";
import HistoryPage from "./pages/HistoryPage";
import GuidePage from "./pages/GuidePage";
import { useLanguage } from "./context/LanguageContext";

function App() {
  const { lang, toggleLanguage } = useLanguage();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [totalPantun, setTotalPantun] = useState(0);
  const [dbStatus, setDbStatus] = useState("Loading...");

  useEffect(() => {
    if (isDark) {
      document.body.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
    }
  }, [isDark]);

  useEffect(() => {
    fetch("/api/status")
      .then((res) => res.json())
      .then((data) => {
        setTotalPantun(data.total_pantun);
        setDbStatus(data.status);
      })
      .catch((err) => console.error("Error fetching status:", err));
  }, []);

  const toggleSidebar = () => setSidebarCollapsed(!sidebarCollapsed);
  const toggleMobileMenu = () => setSidebarOpen(!sidebarOpen);
  const closeMobileMenu = () => setSidebarOpen(false);
  const toggleTheme = () => setIsDark(!isDark);

  return (
    <BrowserRouter>
      <div className="app-layout">
        {/* Mobile sidebar overlay — click to close */}
        <div
          className={`sidebar-overlay${sidebarOpen ? " active" : ""}`}
          onClick={closeMobileMenu}
          aria-hidden="true"
        />

        <button
          className="lang-corner-btn"
          onClick={toggleLanguage}
          title={lang === "en" ? "Bahasa Melayu" : "English"}
          aria-label="Toggle language"
        >
          <i className="fas fa-language fa-xl"></i>
        </button>

        <Sidebar
          collapsed={sidebarCollapsed}
          open={sidebarOpen}
          isDark={isDark}
          toggleSidebar={toggleSidebar}
          toggleTheme={toggleTheme}
          onNavClick={closeMobileMenu}
        />

        <main className="main-content">
          {/* Top nav bar for mobile */}
          <div className="top-nav">
            <button className="toggle-btn" onClick={toggleMobileMenu} aria-label="Toggle menu">
              <i className={`fas ${sidebarOpen ? "fa-times" : "fa-bars"}`}></i>
            </button>
            <span className="topnav-logo">Simpantun</span>
          </div>

          <Routes>
            <Route path="/" element={<ScanPage totalPantun={totalPantun} dbStatus={dbStatus} />} />
            <Route path="/result" element={<ResultPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/guide" element={<GuidePage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
