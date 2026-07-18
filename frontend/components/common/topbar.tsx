"use client";

import { useState, useTransition } from "react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useQueueQuery, API_URL } from "@/hooks/use-queries";

export function Topbar() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  const { data: caseItems = [], isError } = useQueueQuery();
  const [crawlState, setCrawlState] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [crawlMessage, setCrawlMessage] = useState("");
  const [, startTransition] = useTransition();

  const searchQuery = searchParams.get("q") || "";

  const handleSearchChange = (val: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (val) params.set("q", val);
    else params.delete("q");
    startTransition(() => {
      router.replace(`${pathname}?${params.toString()}`);
    });
  };

  async function runCrawl() {
    setCrawlState("loading");
    setCrawlMessage("Đang kết nối quét MXH...");
    try {
      const response = await fetch(`${API_URL}/api/crawl`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keywords: [], max_posts_per_platform: 2 }),
      });
      if (!response.ok) throw new Error("Crawl API unavailable");
      const reader = response.body?.getReader();
      if (!reader) throw new Error("No stream");
      const decoder = new TextDecoder();
      let buffer = "";
      let itemCount = 0;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const msg = JSON.parse(line);
            if (msg.type === "start") {
              setCrawlMessage(`${msg.message} — đang phân tích...`);
            } else if (msg.type === "item") {
              itemCount = msg.count;
              setCrawlMessage(`Đã phân tích ${itemCount} nội dung: ${msg.claim}...`);
              void queryClient.invalidateQueries({ queryKey: ["queue"] });
            } else if (msg.type === "done") {
              setCrawlMessage(`Hoàn tất! ${itemCount} nội dung đã được thêm vào hàng đợi.`);
            }
          } catch { /* skip non-JSON */ }
        }
      }
      void queryClient.invalidateQueries({ queryKey: ["queue"] });
      setCrawlState("success");
    } catch {
      setCrawlMessage("Không thể quét nguồn lúc này. Kiểm tra Backend và API key crawler.");
      setCrawlState("error");
    }
  }

  const urgentCount = caseItems.filter((x) => x.priority === "Khẩn cấp").length;

  return (
    <>
      <header className="monitor-topbar">
        <div className="monitor-search">
          <span>⌕</span>
          <input
            value={searchQuery}
            onChange={(event) => handleSearchChange(event.target.value)}
            placeholder="Tìm claim hoặc mã hồ sơ…"
            aria-label="Tìm kiếm hồ sơ"
          />
        </div>
        <button
          className={`crawl-button ${crawlState}`}
          onClick={runCrawl}
          disabled={crawlState === "loading"}
        >
          {crawlState === "loading" ? <><i /> Đang quét MXH…</> : "⌁ Quét MXH"}
        </button>
        <div className={`monitor-live ${isError || caseItems.length === 0 ? "fallback" : "api"}`}>
          <i /> {isError || caseItems.length === 0 ? "Dữ liệu mẫu dự phòng" : "Dữ liệu API trực tiếp"}
        </div>
        <button className="notification-button" aria-label="Thông báo">
          ♢<b>{urgentCount || ""}</b>
        </button>
        <button className="monitor-avatar" aria-label="Tài khoản Minh Anh">
          MA
        </button>
        <span className="avatar-chevron">⌄</span>
      </header>

      {crawlMessage && (
        <div className={`crawl-toast ${crawlState}`} role="status">
          <span>{crawlState === "success" ? "✓" : "!"}</span>
          <p>{crawlMessage}</p>
          <button onClick={() => setCrawlMessage("")}>×</button>
        </div>
      )}
    </>
  );
}
