import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Loader from "../components/Loader";
import { useLanguage } from "../context/LanguageContext";

export default function ScanPage({ totalPantun, dbStatus }) {
  const { t } = useLanguage();
  const [tab, setTab] = useState("image");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [textVal, setTextVal] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFiles = (files) => {
    const f = files[0];
    if (f && f.type.startsWith("image/")) {
      setFile(f);
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(f);
    } else {
      alert(t("alert_image_only"));
    }
  };

  const resetImage = () => {
    setFile(null);
    setPreview("");
  };

  const analyzeData = async (type) => {
    let payload = {};
    if (type === "image") {
      if (!file || !preview) {
        alert(t("alert_select_image"));
        return;
      }
      payload = { type: "image", image: preview, filename: file.name };
    } else {
      if (!textVal.trim()) {
        alert(t("alert_enter_text"));
        return;
      }
      payload = { type: "text", text: textVal };
    }

    setLoading(true);
    try {
      const res = await axios.post("/api/analyze", payload);
      if (res.data.success) {
        // Save to localStorage history
        try {
          const history = JSON.parse(localStorage.getItem('simpantun_history') || '[]');
          const newEntry = {
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            data: res.data
          };
          history.unshift(newEntry);
          if (history.length > 50) history.pop(); // Keep last 50
          localStorage.setItem('simpantun_history', JSON.stringify(history));
        } catch (e) {
          console.error("Error saving history", e);
        }

        navigate("/result", { state: res.data });
      } else {
        alert(t("alert_error_prefix") + (res.data.error || t("alert_unknown_error")));
      }
    } catch (err) {
      console.error(err);
      alert(t("alert_server_fail"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="content-area">
      <div className="container">
        <header>
          <h1><i className="fas fa-book-open"></i> SIMPANTUN</h1>
          <p>{t("scan_subtitle")}</p>
        </header>

        <div className="upload-card">
          <div className="tabs">
            <button className={`tab-btn ${tab === 'image' ? 'active' : ''}`} onClick={() => setTab("image")}>
              <i className="fas fa-camera"></i> {t("tab_image")}
            </button>
            <button className={`tab-btn ${tab === 'text' ? 'active' : ''}`} onClick={() => setTab("text")}>
              <i className="fas fa-keyboard"></i> {t("tab_text")}
            </button>
          </div>

          {tab === "image" && (
            <div className="input-section active">
              {!preview ? (
                <div
                  className="upload-area"
                  onClick={() => document.getElementById("file-input").click()}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <i className="fas fa-cloud-upload-alt upload-icon"></i>
                  <div className="upload-text">
                    <h3>{t("upload_click")}</h3>
                    <p>{t("upload_format")}</p>
                  </div>
                  <input type="file" id="file-input" accept="image/*" hidden onChange={(e) => handleFiles(e.target.files)} />
                </div>
              ) : (
                <div id="preview-container">
                  <button className="remove-img-btn" onClick={resetImage} title={t("remove_image")}>
                    <i className="fas fa-times"></i>
                  </button>
                  <img id="image-preview" src={preview} alt="Preview" />
                </div>
              )}

              <button className="btn-analyze" onClick={() => analyzeData("image")}>
                <i className="fas fa-search"></i> {t("btn_analyze_image")}
              </button>
            </div>
          )}

          {tab === "text" && (
            <div className="input-section active">
              <textarea
                value={textVal}
                onChange={(e) => setTextVal(e.target.value)}
                placeholder={t("text_placeholder")}
              />
              <button className="btn-analyze" onClick={() => analyzeData("text")}>
                <i className="fas fa-search"></i> {t("btn_search_pantun")}
              </button>
            </div>
          )}
        </div>

        <footer>
          <p>
            {t("db_status")}
            <span className="stats-badge" style={{ margin: "0 10px" }}><i className="fas fa-database"></i> {totalPantun} Pantun</span>
            <span>{dbStatus === "Ready" ? t("status_ready") : dbStatus === "Loading..." ? t("status_loading") : dbStatus}</span>
          </p>
        </footer>
      </div>

      {loading && (
        <div id="loading-overlay">
          <Loader />
        </div>
      )}
    </div>
  );
}
