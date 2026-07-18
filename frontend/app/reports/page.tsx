"use client";

import { useQueueQuery } from "@/hooks/use-queries";

export default function ReportsPage() {
  const { data: allItems = [], isLoading } = useQueueQuery();

  if (isLoading) {
    return (
      <div className="monitor-page">
        <div style={{ padding: "100px", textAlign: "center" }}>Đang tải báo cáo...</div>
      </div>
    );
  }

  const total = allItems.length;
  const dung = allItems.filter((i) => i.verdict === "Đúng").length;
  const hieuLam = allItems.filter((i) => i.verdict === "Hiểu lầm").length;
  const canKC = allItems.filter((i) => i.verdict === "Cần kiểm chứng").length;
  const open = allItems.filter((i) => i.status !== "Đã xử lý").length;

  const hieuLamItems = allItems.filter((i) => i.verdict === "Hiểu lầm");
  const reasonTexts = hieuLamItems.map((i) => i.reason.toLowerCase());
  const countPattern = (patterns: RegExp[]) =>
    reasonTexts.filter((r) => patterns.some((p) => p.test(r))).length;
  const nhầmChủThể = countPattern([
    /chủ thể.*tổ chức.*cá nhân|tổ chức.*cá nhân.*chủ thể|gán.*tổ chức.*cá nhân|cá nhân.*tổ chức/i,
  ]);
  const nhầmNĐ15 = countPattern([/nđ15|nđ 15|15\/2020|hết hiệu lực|quy định cũ/i]);
  const nhầmKhoản = countPattern([
    /khoản 1.*khoản 2|khoản 2.*khoản 1|k1.*k2|k2.*k1|nhầm khoản/i,
  ]);
  const otherHieuLam = Math.max(0, hieuLam - nhầmChủThể - nhầmNĐ15 - nhầmKhoản);

  const platforms = ["Facebook", "TikTok", "YouTube", "X", "Forum"] as const;
  const platformCounts = platforms.map((p) => ({
    platform: p,
    count: allItems.filter((i) => i.platform === p).length,
  }));

  return (
    <div className="monitor-page">
      <div className="queue-heading">
        <div>
          <span className="eyebrow">BÁO CÁO</span>
          <h1>Báo cáo tổng hợp</h1>
          <p>Tổng hợp kết quả phân tích AI trên tất cả hồ sơ giám sát.</p>
        </div>
      </div>

      <section className="queue-card" style={{ marginBottom: 24 }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, padding: 24 }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 32, fontWeight: 700 }}>{total}</div>
            <small>Tổng hồ sơ</small>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#22c55e" }}>{dung}</div>
            <small>Đúng</small>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#f97316" }}>{hieuLam}</div>
            <small>Hiểu lầm</small>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#eab308" }}>{canKC}</div>
            <small>Cần kiểm chứng</small>
          </div>
        </div>
      </section>

      <section className="queue-card" style={{ marginBottom: 24 }}>
        <div style={{ padding: 24 }}>
          <h3 style={{ marginBottom: 12 }}>Top hiểu lầm lặp lại</h3>
          <table className="queue-table">
            <thead>
              <tr>
                <th>STT</th>
                <th>NHÓM HIỂU LẦM</th>
                <th>SỐ LẦN</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1</td>
                <td>Nhầm chủ thể tổ chức ↔ cá nhân</td>
                <td>{nhầmChủThể}</td>
              </tr>
              <tr>
                <td>2</td>
                <td>Nhầm quy định cũ NĐ15/2020</td>
                <td>{nhầmNĐ15}</td>
              </tr>
              <tr>
                <td>3</td>
                <td>Nhầm khoản k1 ↔ k2 Điều 95</td>
                <td>{nhầmKhoản}</td>
              </tr>
              {otherHieuLam > 0 && (
                <tr>
                  <td>4</td>
                  <td>Hiểu lầm khác</td>
                  <td>{otherHieuLam}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="queue-card" style={{ marginBottom: 24 }}>
        <div style={{ padding: 24 }}>
          <h3 style={{ marginBottom: 12 }}>Phân bổ theo nền tảng</h3>
          <table className="queue-table">
            <thead>
              <tr>
                <th>NỀN TẢNG</th>
                <th>SỐ LƯỢNG</th>
                <th>TỈ LỆ</th>
              </tr>
            </thead>
            <tbody>
              {platformCounts
                .filter((p) => p.count > 0)
                .sort((a, b) => b.count - a.count)
                .map((p) => (
                  <tr key={p.platform}>
                    <td>{p.platform}</td>
                    <td>{p.count}</td>
                    <td>{total ? Math.round((p.count / total) * 100) : 0}%</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="queue-card">
        <div style={{ padding: 24 }}>
          <h3 style={{ marginBottom: 4 }}>Hồ sơ đang mở: {open}</h3>
          <p style={{ color: "#94a3b8", fontSize: 14 }}>
            Báo cáo được tính trực tiếp từ dữ liệu hàng đợi hiện đang hiển thị.
          </p>
        </div>
      </section>
    </div>
  );
}
