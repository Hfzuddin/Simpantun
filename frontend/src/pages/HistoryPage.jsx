import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function HistoryPage() {
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
    if (confirm("Are you sure you want to clear all history?")) {
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
      <div className="container analytics-container" style={{ width: "100%", maxWidth: "800px" }}>
        <header>
          <h1><i className="fa-solid fa-clock-rotate-left"></i> Search History</h1>
        </header>

        <div className="upload-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
            <h3>Saved Results ({history.length})</h3>
            {history.length > 0 && (
              <button onClick={clearHistory} style={{ background: "#ef4444", color: "white", border: "none", padding: "8px 16px", borderRadius: "8px", cursor: "pointer", fontWeight: "bold" }}>
                <i className="fas fa-trash"></i> Clear All
              </button>
            )}
          </div>

          {history.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
              <i className="fas fa-folder-open" style={{ fontSize: "3rem", marginBottom: "15px" }}></i>
              <p>No search history found.</p>
              <Link to="/" style={{ color: "var(--primary-color)", marginTop: "10px", display: "inline-block" }}>Go back to Scan</Link>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
              {history.map((item, index) => {
                const mode = item.data.search_mode || "Unknown";
                const isVisual = mode.includes("Visual");

                return (
                  <div key={item.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "15px", border: "1px solid var(--border-color)", borderRadius: "12px", background: "var(--bg-color)" }}>
                    <div style={{ display: "flex", gap: "15px", alignItems: "center" }}>
                      <div style={{ width: "40px", height: "40px", borderRadius: "8px", background: isVisual ? "#dcfce7" : "#e0e7ff", color: isVisual ? "#166534" : "#4f46e5", display: "flex", justifyContent: "center", alignItems: "center", fontSize: "1.2rem" }}>
                        <i className={isVisual ? "fas fa-image" : "fas fa-font"}></i>
                      </div>
                      <div>
                        <div style={{ fontWeight: "bold", fontSize: "1.1rem" }}>{mode} Scan</div>
                        <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>{formatDate(item.timestamp)}</div>
                        <div style={{ fontSize: "0.85rem", marginTop: "4px" }}>
                          <span className="stats-badge" style={{ padding: "2px 8px", fontSize: "0.8rem" }}>
                            {item.data.results ? item.data.results.length : 0} Matches
                          </span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <button onClick={() => viewResult(item)} style={{ background: "var(--primary-color)", color: "white", border: "none", padding: "8px 16px", borderRadius: "8px", cursor: "pointer", fontWeight: "bold" }}>
                        View <i className="fas fa-arrow-right" style={{ marginLeft: "5px" }}></i>
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
