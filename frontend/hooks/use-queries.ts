import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Case, ApiQueueItem, StudyCase, Status } from "../types";
import { API_URL, mapApiCase } from "../utils/api";

export function useQueueQuery() {
  return useQuery<Case[]>({
    queryKey: ["queue"],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/api/queue?_=${Date.now()}`, {
        cache: "no-store",
        headers: { "Cache-Control": "no-cache" },
      });
      if (!response.ok) throw new Error("Queue API unavailable");
      const queue = (await response.json()) as ApiQueueItem[];
      return queue.map(mapApiCase);
    },
    refetchInterval: 30000, // automatic polling every 30 seconds
  });
}

export function useVerifyQuery() {
  return useQuery<StudyCase[]>({
    queryKey: ["verify"],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/api/verify`, { cache: "no-store" });
      if (!response.ok) throw new Error("Verify API unavailable");
      const data = (await response.json()) as { cases: StudyCase[] };
      return data.cases || [];
    },
  });
}

export function useUpdateStatusMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, status }: { id: string; status: Status }) => {
      const statusMap: Record<Status, string> = {
        Mới: "new",
        "Đang xử lý": "reviewing",
        "Đã xử lý": "resolved",
      };
      const response = await fetch(`${API_URL}/api/cases/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: statusMap[status] }),
      });
      if (!response.ok) throw new Error("Failed to update status");
      return response.json();
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["queue"] });
    },
  });
}

export function useClearQueueMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_URL}/api/queue`, { method: "DELETE" });
      if (!response.ok) throw new Error("Failed to clear queue");
      return response.json() as Promise<{ deleted: number; message: string }>;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["queue"] });
    },
  });
}
