import { Verdict, Status } from "@/types";

export function slug(value: string) {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/\s+/g, "-");
}

export function VerdictBadge({ value, large = false }: { value: Verdict; large?: boolean }) {
  return (
    <span className={`verdict-new ${slug(value)} ${large ? "large" : ""}`}>
      <i />
      {value}
    </span>
  );
}

export function StatusBadge({ value }: { value: Status }) {
  return (
    <span className={`status-new ${slug(value)}`}>
      <i />
      {value}
    </span>
  );
}
