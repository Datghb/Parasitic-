import { notFound } from "next/navigation";
import { CaseDetail } from "@/components/cases/case-detail";
import { fetchQueue } from "@/utils/api";

export default async function CasePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const items = await fetchQueue();
  const item = items.find((x) => x.id === id);

  if (!item) notFound();

  return <CaseDetail item={item} />;
}
