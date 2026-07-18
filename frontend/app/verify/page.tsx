"use client";

import { useVerifyQuery } from "@/hooks/use-queries";

export default function VerifyPage() {
  const { data: cases = [], isLoading, isSuccess } = useVerifyQuery();

  if (isLoading) {
    return (
      <div className="monitor-page">
        <div style={{ padding: "100px", textAlign: "center" }}>Đang tải dữ liệu kiểm chứng...</div>
      </div>
    );
  }

  return (
    <div className="monitor-page">
      <div className="queue-heading">
        <div>
          <span className="eyebrow">ĐỐI CHIẾU THỰC TẾ</span>
          <h1>Tầng kiểm chứng</h1>
          <p>So sánh kết quả hệ thống với các quyết định xử phạt đã được công bố.</p>
        </div>
        <div className={`verify-state ${isSuccess ? "connected" : ""}`}>
          <i />
          {isSuccess ? `${cases.length} study case từ API` : "Đang chờ Backend API"}
        </div>
      </div>
      {!cases.length ? (
        <section className="queue-card verify-empty">
          <strong>Chưa tải được study case</strong>
          <p>Khởi động backend tại cổng 8000 để xem dữ liệu kiểm chứng thật.</p>
        </section>
      ) : (
        <div className="verify-list">
          {cases.map((item) => (
            <article className="verify-card" key={item.id}>
              <header>
                <div>
                  <small>
                    {item.id} · {item.ngay_quyet_dinh}
                  </small>
                  <h2>{item.ten_vu}</h2>
                  <p>{item.nguon_cong_bo}</p>
                </div>
                <span>KHỚP CASE THẬT</span>
              </header>
              <div className="verify-columns">
                <div>
                  <small>HÀNH VI THỰC TẾ</small>
                  <p>{item.hanh_vi}</p>
                  <dl>
                    <div>
                      <dt>Chủ thể</dt>
                      <dd>{item.chu_the}</dd>
                    </div>
                    <div>
                      <dt>Mức phạt thực tế</dt>
                      <dd>{item.muc_phat.toLocaleString("vi-VN")} đồng</dd>
                    </div>
                    <div>
                      <dt>Điều khoản viện dẫn</dt>
                      <dd>{item.dieu_khoan_vien_dan}</dd>
                    </div>
                  </dl>
                </div>
                <div>
                  <small>KỲ VỌNG HỆ THỐNG</small>
                  <p className="expected-label">✓ {item.expected_he_thong.nhan}</p>
                  <strong>{item.expected_he_thong.dieu_khoan_moi}</strong>
                  <p>{item.expected_he_thong.ghi_chu}</p>
                </div>
              </div>
              <footer>
                <span>Biện pháp: {item.bien_phap_khac_phuc}</span>
                <a href={item.nguon_url} target="_blank" rel="noreferrer">
                  Mở nguồn công bố ↗
                </a>
              </footer>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
