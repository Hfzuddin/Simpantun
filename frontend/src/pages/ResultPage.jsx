import { useLocation, Link } from "react-router-dom";
import { useState } from "react";

export default function ResultPage() {
  const location = useLocation();
  const state = location.state || {};
  const { results = [], search_mode = "", input_keywords = [], image_url, extracted_text } = state;

  const [page, setPage] = useState(1);
  const itemsPerPage = 10;
  const isVisualMode = search_mode.includes("Visual");

  const highlightText = (text, keywords) => {
    if (!keywords || keywords.length === 0) return text;
    const sortedKeywords = [...keywords].sort((a, b) => b.length - a.length);
    const escapedKeywords = sortedKeywords.map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const pattern = new RegExp(`(${escapedKeywords.join('|')})`, 'gi');
    const parts = text.split(pattern);

    return parts.map((part, i) => {
      const isMatch = keywords.some(k => k.toLowerCase() === part.toLowerCase());
      if (isMatch) {
        return <mark key={i} className="highlight-word">{part}</mark>;
      }
      return part;
    });
  };

  const start = (page - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const currentItems = results.slice(start, end);
  const totalPages = Math.ceil(results.length / itemsPerPage);

  if (!state.success) {
    return (
      <div className="content-area result-content-area" style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ textAlign: "center" }}>
          <h2 style={{ marginBottom: "15px" }}>No Analysis Data Found</h2>
          <Link to="/" className="btn-back">Go to Upload Scan</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="content-area result-content-area">
      <div className="result-panel">
        <Link to="/" className="btn-back"><i className="fas fa-arrow-left"></i> New Search</Link>

        {image_url && <img src={image_url} className="img-preview" alt="Uploaded Preview" />}

        <div className="box">
          <h3><i className="fa-solid fa-code"></i> Analysis Findings</h3>
          <div style={{ marginBottom: "10px", fontSize: "0.9em", color: "var(--text-muted)" }}>
            <strong>Mode:</strong>
            <span style={isVisualMode ? { color: "#22c55e", fontWeight: "bold", marginLeft: "5px" } : { marginLeft: "5px" }}>
              {search_mode}
            </span>
          </div>

          <div style={{ marginTop: "30  px" }}>
            <strong>
              {isVisualMode ? <i className="fas fa-camera"></i> : <i className="fas fa-tags"></i>}
              {isVisualMode ? " Detected Visual Objects:" : " Text Keywords:"}
            </strong><br />
            <div style={{ marginTop: "5px" }}>
              {input_keywords.length > 0 ? (
                input_keywords.map((k, i) => (
                  <span key={i} className={`tag ${isVisualMode ? 'tag-visual' : 'tag-text'}`}>{k}</span>
                ))
              ) : (
                <span style={{ color: "var(--text-muted)", fontStyle: "italic", fontSize: "0.85em" }}>
                  No objects or keywords detected.
                </span>
              )}
            </div>
          </div>

          {extracted_text && extracted_text.length > 5 && search_mode.includes("OCR") && (
            <>
              <hr style={{ margin: "15px 0", borderTop: "1px dashed var(--border-color)" }} />
              <p>
                <strong><i className="fas fa-file-alt"></i> OCR Text:</strong><br />
                <em style={{ color: "var(--text-muted)", fontSize: "0.9em" }}>"{extracted_text}"</em>
              </p>
            </>
          )}
        </div>
      </div>

      <div className="results-main">
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px", borderBottom: "2px solid var(--border-color)", paddingBottom: "10px" }}>
          <h2>Pantun Search Results</h2>
          <small style={{ alignSelf: "flex-end", color: "var(--text-muted)" }}>Sorted by similarity level</small>
        </div>

        <div className="results-grid">
          {results.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px", gridColumn: "1 / -1", color: "var(--text-muted)" }}>
              No matching pantun found.
            </div>
          ) : (
            currentItems.map((item, i) => {
              const globalIdx = start + i + 1;
              const pantunLower = item.highlighted_content.toLowerCase();
              const matched = input_keywords.filter(kw => pantunLower.includes(kw.toLowerCase()));

              return (
                <div className="pantun-card" key={i}>
                  <div className="card-header">
                    <span className="theme-badge">{item.title}</span>
                    <div className="score-badge">
                      <span className="score-value">{item.score.toFixed(1)}%</span>
                      <div className="score-bar-bg">
                        <div className="score-bar-fill" style={{ width: `${item.score}%` }}></div>
                      </div>
                    </div>
                  </div>

                  <div className="card-body">
                    <div className="pantun-text">
                      {highlightText(item.highlighted_content, input_keywords)}
                    </div>
                  </div>

                  <div className="card-footer">
                    <div style={{ fontSize: "0.8em", color: "var(--text-muted)", marginBottom: "5px" }}>
                      <strong>#{globalIdx}</strong> &bull; Source: {item.author}
                    </div>
                    {matched.length > 0 ? (
                      <div className="match-reason">
                        <strong><i className={isVisualMode ? "fas fa-camera" : "fas fa-tag"}></i> Match:</strong> {matched.join(', ')}
                      </div>
                    ) : (
                      <div className="match-reason semantic">
                        <strong><i className="fas fa-brain"></i> Semantic:</strong> {item.score > 85 ? "Highly relevant theme." : "Visual concept/meaning match."}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {totalPages > 1 && (
          <div className="pagination">
            <button className="page-btn" disabled={page === 1} onClick={() => setPage(page - 1)}>
              <i className="fas fa-chevron-left"></i>
            </button>
            <span style={{ alignSelf: "center", fontSize: "0.9em", margin: "0 10px" }}>{page} / {totalPages}</span>
            <button className="page-btn" disabled={page === totalPages} onClick={() => setPage(page + 1)}>
              <i className="fas fa-chevron-right"></i>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
