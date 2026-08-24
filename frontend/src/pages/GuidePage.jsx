import { useLanguage } from "../context/LanguageContext";

export default function GuidePage() {
  const { t } = useLanguage();

  return (
    <div className="content-area">
      <div className="container analytics-container" style={{ width: "100%", maxWidth: "800px" }}>
        <header>
          <h1><i className="fas fa-circle-info"></i> {t("guide_title")}</h1>
        </header>

        <div className="upload-card" style={{ marginBottom: "20px" }}>
          <h3 style={{ color: "var(--primary-color)", marginBottom: "10px" }}>
            <i className="fas fa-keyboard"></i> {t("guide_text_search_title")}
          </h3>
          <ol style={{ paddingLeft: "20px", lineHeight: "1.8" }}>
            <li>{t("guide_text_search_1")}</li>
            <li>{t("guide_text_search_2")}</li>
            <li>{t("guide_text_search_3")}</li>
          </ol>
        </div>

        <div className="upload-card" style={{ marginBottom: "20px" }}>
          <h3 style={{ color: "var(--primary-color)", marginBottom: "10px" }}>
            <i className="fas fa-camera"></i> {t("guide_image_search_title")}
          </h3>
          <ol style={{ paddingLeft: "20px", lineHeight: "1.8" }}>
            <li>{t("guide_image_search_1")}</li>
            <li>{t("guide_image_search_2")}</li>
            <li>{t("guide_image_search_3")}</li>
            <li>{t("guide_image_search_4")}</li>
          </ol>
        </div>

        <div className="upload-card" style={{ marginBottom: "20px" }}>
          <h3 style={{ color: "var(--primary-color)", marginBottom: "10px" }}>
            <i className="fas fa-clipboard-list"></i> {t("guide_results_history_title")}
          </h3>
          <ul style={{ paddingLeft: "20px", lineHeight: "1.8" }}>
            <li>{t("guide_results_1")}</li>
            <li>{t("guide_history_1")}</li>
          </ul>

          <h3 style={{ color: "var(--primary-color)", margin: "20px 0 10px" }}>
            <i className="fas fa-language"></i> {t("guide_language_title")}
          </h3>
          <p style={{ lineHeight: "1.8" }}>{t("guide_language_1")}</p>
        </div>

        <div className="upload-card" style={{ borderColor: "#f59e0b" }}>
          <h3 style={{ color: "#f59e0b", marginBottom: "10px" }}>
            <i className="fas fa-triangle-exclamation"></i> {t("guide_limitations_title")}
          </h3>
          <ul style={{ paddingLeft: "20px", lineHeight: "1.8" }}>
            <li>{t("guide_limit_dataset")}</li>
            <li>{t("guide_limit_visual")}</li>
            <li>{t("guide_limit_ocr")}</li>
            <li>{t("guide_limit_history")}</li>
            <li>{t("guide_limit_coldstart")}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
