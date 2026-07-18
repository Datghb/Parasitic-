"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQueueQuery } from "@/hooks/use-queries";

export function Sidebar() {
  const pathname = usePathname();
  const { data: caseItems = [] } = useQueueQuery();

  const activeCount = caseItems.filter((x) => x.status !== "Đã xử lý").length;

  return (
    <aside className="monitor-sidebar" style={{ position: "fixed", top: 0, bottom: 0, left: 0, width: "248px" }}>
      <div className="monitor-brand">
        <span className="monitor-brand-mark">L</span>
        <div>
          <strong>Legal Radar</strong>
          <small>TRUNG TÂM GIÁM SÁT</small>
        </div>
      </div>
      <nav aria-label="Điều hướng chính">
        <Link href="/" className={`monitor-nav-link ${pathname === "/" ? "active" : ""}`} style={{ display: "flex", textDecoration: "none" }}>
          <span>⌁</span> Tổng quan thị trường
        </Link>
        <Link href="/queue" className={`monitor-nav-link ${pathname.startsWith("/queue") ? "active" : ""}`} style={{ display: "flex", textDecoration: "none" }}>
          <span>▦</span> Hàng đợi giám sát <b>{activeCount}</b>
        </Link>
        <Link href="/reports" className={`monitor-nav-link ${pathname.startsWith("/reports") ? "active" : ""}`} style={{ display: "flex", textDecoration: "none" }}>
          <span>◎</span> Báo cáo tổng hợp
        </Link>
        <Link href="/sources" className={`monitor-nav-link ${pathname.startsWith("/sources") ? "active" : ""}`} style={{ display: "flex", textDecoration: "none" }}>
          <span>⌘</span> Nguồn chính thức
        </Link>
        <Link href="/verify" className={`monitor-nav-link ${pathname.startsWith("/verify") ? "active" : ""}`} style={{ display: "flex", textDecoration: "none" }}>
          <span>✓</span> Tầng kiểm chứng
        </Link>
        <Link href="/graph" className={`monitor-nav-link ${pathname.startsWith("/graph") ? "active" : ""}`} style={{ display: "flex", textDecoration: "none" }}>
          <span>⌬</span> Knowledge Graph
        </Link>
      </nav>
      <div className="sidebar-insights">
        <div className="sidebar-mini-report">
          <small>BÁO CÁO NHANH HÔM NAY</small>
          <span>Claims mới</span>{" "}
          <strong>
            {caseItems.length}{" "}
            {caseItems.length > 0 ? <em>↗ {Math.min(99, caseItems.length * 3)}%</em> : null}
          </strong>
          <svg viewBox="0 0 200 48" aria-hidden="true">
            <path d="M2 42 L18 26 L32 31 L48 17 L64 23 L81 12 L97 28 L113 19 L130 25 L148 9 L164 27 L181 18 L198 4" />
          </svg>
        </div>
        <div className="sidebar-support">
          <span>◉</span>
          <div>
            <strong>Trung tâm hỗ trợ</strong>
            <small>Hướng dẫn & chính sách</small>
          </div>
        </div>
        <div className="monitor-system">
          <i /> Legal Radar v2.4.1<small>Hệ thống hoạt động ổn định</small>
        </div>
      </div>
    </aside>
  );
}
