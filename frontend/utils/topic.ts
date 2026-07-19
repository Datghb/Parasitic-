import { Case } from "../types";

export function legalTopicName(document: string): string {
  const value = document.toLocaleLowerCase("vi");
  if (/tín dụng|ngân hàng|bank/.test(value)) return "Tổ chức tín dụng";
  if (/căn cước|cư trú/.test(value)) return "Cư trú";
  if (/bảo hiểm|bhyt|y tế/.test(value)) return "BHYT";
  if (/lao động|việc làm/.test(value)) return "Lao động";
  if (/giao thông|đường bộ|phương tiện/.test(value)) return "Giao thông";
  return document.replace(/\s*\(.+?\)\s*/g, " ").trim().slice(0, 34) || "Khác";
}

export function discussionTopicName(item: Case): string {
  const value = `${item.claim} ${(item.keywords || []).join(" ")} ${item.document}`.toLocaleLowerCase("vi");
  if (/vắc.?xin|vaccine|dịch bệnh|y tế|bảo hiểm y tế|bhyt/.test(value)) return "Y tế & vaccine";
  if (/ngân hàng|tín dụng|lãi suất|tiền gửi/.test(value)) return "Ngân hàng & tín dụng";
  if (/sáp nhập|đơn vị hành chính|tỉnh thành/.test(value)) return "Sáp nhập hành chính";
  if (/tin giả|sai sự thật|mạng xã hội|mxh|tin đồn/.test(value)) return "Tin giả trên mạng xã hội";
  if (/xử phạt|mức phạt|phạt hành chính/.test(value)) return "Xử phạt hành chính";
  return item.keywords?.find((keyword) => keyword.trim().length > 3)?.trim() || legalTopicName(item.document);
}
