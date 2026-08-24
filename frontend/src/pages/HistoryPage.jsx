import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { SEARCH_MODE_KEYS } from "../i18n/translations";

export default function HistoryPage() {
  const { t } = useLanguage();
  const [history, setHistory] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    try {
      const data = JSON.parse(localStorage.getItem('simpantun_history') || '[]');
      setHistory(data);
    } catch (e) {
      console.error(e);
    }
  }, []);

  const clearHistory = () => {
    if (confirm(t("confirm_clear_history"))) {
      localStorage.removeItem('simpantun_history');
      setHistory([]);
    }
  };

  const viewResult = (item) => {
    navigate("/result", { state: item.data });
  };

  const formatDate = (isoString) => {
    const d = new Date(isoString);
    return d.toLocaleDateString() + " " + d.toLocaleTimeString();
  };

  return (
    <div className="content-area">
      <div className="container analytics-container">
        <header>
          <h1><i className="fa-solid fa-clock-rotate-left"></i> {t("search_history_title")}</h1>
        </header>

        <div className="upload-card">
          {/* Header row: title + clear button */}
          <div className="history-header-row">
            <h3>{t("saved_results")} ({history.length})</h3>
            {history.length > 0 && (
              <button
                onClick={clearHistory}
                className="history-clear-btn"
              >
                <i className="fas fa-trash"></i> {t("clear_all")}
              </button>
            )}
          </div>

          {history.length === 0 ? (
            <div className="history-empty">
              <i className="fas fa-folder-open"></i>
              <p>{t("no_history")}</p>
              <Link to="/" className="history-back-link">{t("back_to_scan")}</Link>
            </div>
          ) : (
            <div className="history-list">
              {history.map((item) => {
                const mode = item.data.search_mode || "Unknown";
                const isVisual = mode.includes("Visual");
                const displayMode = t(SEARCH_MODE_KEYS[mode]) || mode;

                return (
                  <div key={item.id} className="history-item">
                    {/* Left side: icon + info */}
                    <div className="history-item-left">
                      <div
                        className="history-mode-icon"
                        style={{
                          background: isVisual ? "#dcfce7" : "#e0e7ff",
                          color: isVisual ? "#166534" : "#4f46e5",
                        }}
                      >
                        <i className={isVisual ? "fas fa-image" : "fas fa-font"}></i>
                      </div>
                      <div className="history-item-info">
                        <div className="history-item-title">
                          {displayMode} {t("scan_suffix")}
                        </div>
                        <div className="history-item-date">{formatDate(item.timestamp)}</div>
                        <div className="history-item-badge">
                          <span className="stats-badge" style={{ padding: "2px 8px", fontSize: "0.8rem" }}>
                            {item.data.results ? item.data.results.length : 0} {t("matches")}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Right side: view button */}
                    <div className="history-item-action">
                      <button
                        onClick={() => viewResult(item)}
                        className="history-view-btn"
                      >
                        {t("view")} <i className="fas fa-arrow-right" style={{ marginLeft: "5px" }}></i>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
