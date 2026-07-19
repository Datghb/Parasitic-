"use client";

import { useQueueQuery } from "@/hooks/use-queries";
import { MarketOverview } from "@/components/dashboard/market-overview";

export default function Home() {
  const { data: allItems = [] } = useQueueQuery();
  return <MarketOverview allItems={allItems} />;
}
