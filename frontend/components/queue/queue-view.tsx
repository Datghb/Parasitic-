"use client";

import { useState, useMemo, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  useQueueQuery,
  useClearQueueMutation,
} from "../../hooks/use-queries";
import { VerdictBadge, StatusBadge } from "../common/badge";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { ManualInputDrawer } from "./manual-input-drawer";
import { Case, Verdict, Status, Priority } from "../../types";

const verdicts: Array<"Tất cả" | Verdict> = ["Tất cả", "Đúng", "Hiểu lầm", "Cần kiểm chứng"];
const statuses: Array<"Tất cả" | Status> = ["Tất cả", "Mới", "Đang xử lý", "Đã xử lý"];
const priorityRank: Record<Priority, number> = { "Khẩn cấp": 4, Cao: 3, "Trung bình": 2, Thấp: 1 };

function platformIcon(platform: Case["platform"]) {
  const paths: Record<Case["platform"], string> = {
    Facebook:
      "M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z",
    TikTok:
      "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z",
    YouTube:
      "M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z",
    X: "M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z",
    Forum:
      "M12.103 0C18.666 0 24 5.485 24 11.997c0 6.51-5.33 11.99-11.9 11.99L0 24V11.79C0 5.28 5.532 0 12.103 0zm.116 4.563c-2.593-.003-4.996 1.352-6.337 3.57-1.33 2.208-1.387 4.957-.148 7.22L4.4 19.61l4.794-1.074c2.745 1.225 5.965.676 8.136-1.39 2.17-2.054 2.86-5.228 1.737-7.997-1.135-2.778-3.84-4.59-6.84-4.585h-.008z",
  };
  return (
    <svg
      className={`platform-svg platform-${platform.toLowerCase()}`}
      viewBox="0 0 24 24"
      role="img"
      aria-label={`${platform} logo`}
      style={{ width: 14, height: 14 }}
    >
      <path d={paths[platform]} />
    </svg>
  );
}

export function QueueView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const searchQuery = searchParams.get("q") || "";

  const { data: fetchedItems = [], isLoading } = useQueueQuery();
  const clearQueueMutation = useClearQueueMutation();

  const [localCases, setLocalCases] = useState<Case[]>([]);

  // Load local cases from sessionStorage on mount
  useEffect(() => {
    const saved = sessionStorage.getItem("local_cases");
    if (saved) {
      try {
        setLocalCases(JSON.parse(saved) as Case[]);
      } catch {
        // ignore
      }
    }
  }, []);

  const saveLocalCases = (cases: Case[]) => {
    setLocalCases(cases);
    sessionStorage.setItem("local_cases", JSON.stringify(cases));
  };

  const [verdictFilter, setVerdictFilter] = useState<(typeof verdicts)[number]>("Tất cả");
  const [statusFilter, setStatusFilter] = useState<(typeof statuses)[number]>("Tất cả");
  const [sortDesc, setSortDesc] = useState(true);
  const [quickTab, setQuickTab] = useState<"all" | "urgent" | "verify" | "processing">("all");
  const [showInput, setShowInput] = useState(false);

  const allItems = useMemo(() => {
    // Deduplicate: if a local case exists in backend (by ID), prefer the backend one.
    const fetchedIds = new Set(fetchedItems.map((item) => item.id));
    const filteredLocal = localCases.filter((item) => !fetchedIds.has(item.id));
    return [...filteredLocal, ...fetchedItems];
  }, [localCases, fetchedItems]);

  const openCount = allItems.filter((item) => item.status !== "Đã xử lý").length;
  const urgentCount = allItems.filter((item) => item.priority === "Khẩn cấp").length;
  const verifyCount = allItems.filter((item) => item.verdict === "Cần kiểm chứng").length;
  const processingCount = allItems.filter((item) => item.status === "Đang xử lý").length;

  const rows = useMemo(() => {
    return allItems
      .filter((item) => verdictFilter === "Tất cả" || item.verdict === verdictFilter)
      .filter((item) => statusFilter === "Tất cả" || item.status === statusFilter)
      .filter(
        (item) =>
          !searchQuery ||
          `${item.claim} ${item.platform} ${item.id}`.toLowerCase().includes(searchQuery.toLowerCase())
      )
      .sort((a, b) => (priorityRank[b.priority] - priorityRank[a.priority]) * (sortDesc ? 1 : -1));
  }, [allItems, verdictFilter, statusFilter, searchQuery, sortDesc]);

  const visibleRows = useMemo(() => {
    return rows.filter(
      (item) =>
        quickTab === "all" ||
        (quickTab === "urgent" && item.priority === "Khẩn cấp") ||
        (quickTab === "verify" && item.verdict === "Cần kiểm chứng") ||
        (quickTab === "processing" && item.status === "Đang xử lý")
    );
  }, [rows, quickTab]);

  const handleOpenCase = (id: string) => {
    // If the case is a local case, we need to save it temporarily so the CaseDetail page can load it!
    // Since CaseDetail page will load from backend API, it will fail for local cases.
    // So we can save the local cases to sessionStorage under 'local_cases' which CaseDetail can read from!
    router.push(`/cases/${id}`);
  };

  const handleClearQueue = () => {
    if (confirm("Bạn có chắc chắn muốn xóa toàn bộ hàng đợi?")) {
      clearQueueMutation.mutate();
      saveLocalCases([]);
    }
  };

  if (isLoading) {
    return (
      <div className="monitor-page">
        <div style={{ padding: "100px", textAlign: "center" }}>Đang tải hàng đợi giám sát...</div>
      </div>
    );
  }

  return (
    <div className="monitor-page">
      <div className="queue-heading">
        <div>
          <span className="eyebrow">ĐIỀU PHỐI NỘI DUNG</span>
          <h1>Hàng đợi giám sát</h1>
          <p>Nhập thủ công nội dung cần theo dõi, sau đó rà soát kết quả phân tích của AI.</p>
        </div>
        <div className="trend-card">
          <div>
            <small>Xu hướng rủi ro 7 ngày</small>
            <strong>
              {allItems.length > 0 ? `↑ ${Math.min(99, allItems.length * 3)}%` : "Chưa có dữ liệu"}
            </strong>
          </div>
          <svg viewBox="0 0 250 55" aria-hidden="true">
            <path d="M3 48 L25 23 L47 30 L69 17 L91 19 L113 8 L135 12 L157 4 L179 33 L201 42 L224 18 L247 25" />
          </svg>
        </div>
      </div>

      <section className="queue-metrics">
        <article>
          <div>
            <small>Hồ sơ mới</small>
            <strong>{allItems.filter((item) => item.status === "Mới").length}</strong>
          </div>
          <i className="metric-icon purple">▣</i>
        </article>
        <article>
          <div>
            <small>Khẩn cấp</small>
            <strong>{urgentCount}</strong>
            {urgentCount > 0 && (
              <span className="hot">
                <em>{allItems.length ? Math.round((urgentCount / allItems.length) * 100) : 0}% tổng hồ sơ</em>
              </span>
            )}
          </div>
          <i className="metric-icon pink">ϟ</i>
        </article>
        <article>
          <div>
            <small>Cần kiểm chứng</small>
            <strong>{verifyCount}</strong>
            {verifyCount > 0 && (
              <span className="up">
                <em>{allItems.length ? Math.round((verifyCount / allItems.length) * 100) : 0}% tổng hồ sơ</em>
              </span>
            )}
          </div>
          <i className="metric-icon amber">◇</i>
        </article>
        <article>
          <div>
            <small>Đang xử lý</small>
            <strong>{processingCount || openCount}</strong>
          </div>
          <i className="metric-icon rose">◷</i>
        </article>
      </section>

      <section className="queue-card">
        <div className="queue-tabs">
          <button className={quickTab === "all" ? "active" : ""} onClick={() => setQuickTab("all")}>
            Tất cả
          </button>
          <button className={quickTab === "urgent" ? "active" : ""} onClick={() => setQuickTab("urgent")}>
            Khẩn cấp <b>{urgentCount}</b>
          </button>
          <button className={quickTab === "verify" ? "active" : ""} onClick={() => setQuickTab("verify")}>
            Cần kiểm chứng <b>{verifyCount}</b>
          </button>
          <button
            className={quickTab === "processing" ? "active" : ""}
            onClick={() => setQuickTab("processing")}
          >
            Đang xử lý <b>{processingCount}</b>
          </button>
        </div>
        <div className="queue-toolbar">
          <div className="filter-group">
            <label>
              Kết quả AI
              <select
                value={verdictFilter}
                onChange={(event) => setVerdictFilter(event.target.value as (typeof verdicts)[number])}
              >
                {verdicts.map((value) => (
                  <option key={value}>{value}</option>
                ))}
              </select>
            </label>
            <label>
              Trạng thái
              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value as (typeof statuses)[number])}
              >
                {statuses.map((value) => (
                  <option key={value}>{value}</option>
                ))}
              </select>
            </label>
          </div>
          <div className="queue-actions">
            <button className="sort-button" onClick={() => setSortDesc((v) => !v)}>
              ↕ Mức ưu tiên: {sortDesc ? "cao trước" : "thấp trước"}
            </button>
            <button className="create-button" onClick={() => setShowInput(true)}>
              ＋ Nhập nội dung mới
            </button>
            <button
              className="clear-button"
              onClick={handleClearQueue}
              disabled={clearQueueMutation.isPending}
            >
              ✕ Xóa hàng đợi
            </button>
          </div>
        </div>
        <div className="queue-table-wrap">
          <table className="queue-table">
            <thead>
              <tr>
                <th>
                  <span className="fake-checkbox" />
                </th>
                <th>CLAIM / NỘI DUNG</th>
                <th>NỀN TẢNG</th>
                <th>MỨC RỦI RO</th>
                <th>ĐÁNH GIÁ AI</th>
                <th>ĐỘ TIN CẬY</th>
                <th>CHỦ ĐỀ PHÁP LÝ</th>
                <th>TRẠNG THÁI</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {visibleRows.map((item) => (
                <tr
                  key={item.id}
                  onClick={() => handleOpenCase(item.id)}
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") handleOpenCase(item.id);
                  }}
                >
                  <td>
                    <span className="fake-checkbox" />
                  </td>
                  <td>
                    <strong>{item.claim}</strong>
                    <small>
                      {item.id} · {item.publishedAt}
                      {item.sourceUrl && item.sourceUrl !== "#" ? (
                        <a
                          href={item.sourceUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="source-link"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {" "}
                          ↗
                        </a>
                      ) : null}
                    </small>
                  </td>
                  <td>
                    <span className={`platform-logo ${item.platform.toLowerCase()}`}>
                      {platformIcon(item.platform)}
                    </span>
                    {item.platform}
                  </td>
                  <td>
                    <span
                      className={`priority-badge ${item.priority
                        .normalize("NFD")
                        .replace(/[\u0300-\u036f]/g, "")
                        .toLowerCase()
                        .replace(/\s+/g, "-")}`}
                    >
                      <i />
                      {item.priority}
                    </span>
                  </td>
                  <td>
                    <VerdictBadge value={item.verdict} />
                    <small className="score-copy">AI score {item.score}/100</small>
                  </td>
                  <td>
                    <span
                      className={`confidence-ring ${
                        item.confidence >= 85 ? "strong" : item.confidence >= 65 ? "medium" : ""
                      }`}
                    >
                      {item.confidence}%
                    </span>
                  </td>
                  <td>
                    <strong className="legal-topic">{item.document}</strong>
                    <small>{item.provision}</small>
                  </td>
                  <td>
                    <StatusBadge value={item.status} />
                  </td>
                  <td>
                    <button className="row-arrow" aria-label={`Mở hồ sơ ${item.id}`}>
                      →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {visibleRows.length === 0 && (
            <div className="queue-empty">
              <strong>Chưa có hồ sơ trong hàng đợi</strong>
              <span>Bấm &ldquo;Quét MXH&rdquo; để thu thập dữ liệu từ mạng xã hội.</span>
            </div>
          )}
        </div>
        <footer className="queue-footer">
          Hiển thị <strong>{visibleRows.length}</strong> / {allItems.length} hồ sơ
        </footer>
      </section>

      {showInput && (
        <ManualInputDrawer
          onClose={() => setShowInput(false)}
          onSave={(items: Case[]) => {
            const updated = [...items, ...localCases];
            saveLocalCases(updated);
            setShowInput(false);
            if (items.length === 1) {
              router.push(`/cases/${items[0].id}`);
            }
          }}
        />
      )}
    </div>
  );
}
