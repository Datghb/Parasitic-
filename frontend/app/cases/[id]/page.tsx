"use client";

import { use, useState, useEffect } from "react";
import { useQueueQuery } from "@/hooks/use-queries";
import { CaseDetail } from "@/components/cases/case-detail";
import { Case } from "@/types";

export default function CasePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: fetchedItems = [], isLoading } = useQueueQuery();
  const [localCases, setLocalCases] = useState<Case[]>([]);

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

  if (isLoading) {
    return (
      <div className="monitor-page">
        <div style={{ padding: "100px", textAlign: "center" }}>Đang tải chi tiết hồ sơ...</div>
      </div>
    );
  }

  // Merge server and local cases to find this specific case
  const allItems = [...localCases, ...fetchedItems];
  const item = allItems.find((x) => x.id === id);

  if (!item) {
    return (
      <div className="monitor-page">
        <div style={{ padding: "100px", textAlign: "center" }}>
          Hồ sơ <strong>{id}</strong> không tồn tại hoặc đã bị xóa.
        </div>
      </div>
    );
  }

  return <CaseDetail item={item} />;
}
