export default function SourcesPage() {
  const sources = [
    {
      tier: 0,
      name: "Ngân hàng Nhà nước (SBV)",
      domain: "sbv.gov.vn",
      desc: "Cơ quan quản lý ngân hàng — thẩm quyền xác nhận/bác bỏ tin đồn tài chính",
    },
    {
      tier: 0,
      name: "Bộ Y tế",
      domain: "moh.gov.vn",
      desc: "Cơ quan phát ngôn về dịch bệnh, y tế công cộng",
    },
    {
      tier: 0,
      name: "Bộ Công an",
      domain: "bocongan.gov.vn",
      desc: "Cơ quan phát ngôn về an ninh, trật tự",
    },
    {
      tier: 0,
      name: "Cổng TTĐT Chính phủ",
      domain: "chinhphu.vn",
      desc: "Công bộ chính sách, quyết định chính thức",
    },
    {
      tier: 1,
      name: "TTXVN",
      domain: "baotintuc.vn",
      desc: "Thông tấn xã — nguồn tin chính thống quốc gia",
    },
    { tier: 1, name: "VTV", domain: "vtv.vn", desc: "Đài Truyền hình Việt Nam" },
    { tier: 1, name: "Nhân Dân", domain: "nhandan.vn", desc: "Cơ quan ngôn luận của Đảng" },
    {
      tier: 2,
      name: "VnExpress",
      domain: "vnexpress.net",
      desc: "Báo lớn — corroboration, không đơn phương quyết định",
    },
    { tier: 2, name: "Tuổi Trẻ", domain: "tuoitre.vn", desc: "Báo lớn — corroboration" },
    { tier: 2, name: "Thanh Niên", domain: "thanhnien.vn", desc: "Báo lớn — corroboration" },
  ];

  return (
    <div className="monitor-page">
      <div className="queue-heading">
        <div>
          <span className="eyebrow">NGUỒN TIN</span>
          <h1>Nguồn chính thức</h1>
          <p>
            Danh sách whitelist nguồn tin theo tầng thẩm quyền — hệ thống chỉ dùng các nguồn này để xác minh nội
            dung.
          </p>
        </div>
      </div>

      {[0, 1, 2].map((tier) => (
        <section key={tier} className="queue-card" style={{ marginBottom: 24 }}>
          <div style={{ padding: 24 }}>
            <h3 style={{ marginBottom: 4 }}>
              Tier {tier}:{" "}
              {tier === 0
                ? "Cơ quan chính phủ (1 mình đủ)"
                : tier === 1
                ? "Báo chí chính thống (cần ≥2 độc lập)"
                : "Báo lớn (chỉ corroboration)"}
            </h3>
            <p style={{ color: "#94a3b8", fontSize: 13, marginBottom: 16 }}>
              {tier === 0
                ? "Một mình Tier 0 xác nhận/bác bỏ là đủ — không cần nguồn khác."
                : tier === 1
                ? "Cần ≥2 nguồn Tier 1/2 độc lập xác nhận. Bác bỏ hợp lệ khi dẫn lời Tier 0."
                : "Chỉ dùng để bổ sung — không đơn phương quyết định."}
            </p>
            <table className="queue-table">
              <thead>
                <tr>
                  <th>TÊN</th>
                  <th>DOMAIN</th>
                  <th>MÔ TẢ</th>
                </tr>
              </thead>
              <tbody>
                {sources
                  .filter((s) => s.tier === tier)
                  .map((s) => (
                    <tr key={s.domain}>
                      <td>
                        <strong>{s.name}</strong>
                      </td>
                      <td>
                        <code>{s.domain}</code>
                      </td>
                      <td>{s.desc}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}
    </div>
  );
}
