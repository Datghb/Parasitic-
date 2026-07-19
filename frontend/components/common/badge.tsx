import { Verdict, Status } from "@/types";

export function slug(value: string) {
  return value.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/\s+/g, "-");
}

const badgeBase =
  "inline-flex items-center gap-1.5 rounded-[9px] px-2 py-[5px] text-[8px] font-[750] whitespace-nowrap";

const verdictColors: Record<string, string> = {
  dung: "bg-[#e9f8f2] text-[#25856b]",
  "hieu-lam": "bg-[#fff0f4] text-[#bd315b]",
  "can-kiem-chung": "bg-[#fff7e5] text-[#a16b15]",
};

const statusColors: Record<string, string> = {
  moi: "bg-[#fff0f4] text-[#bd315b]",
  "dang-xu-ly": "bg-[#fff7e5] text-[#a16b15]",
  "da-xu-ly": "bg-[#e9f8f2] text-[#25856b]",
};

function Dot() {
  return <i className="h-[5px] w-[5px] rounded-full bg-current" />;
}

export function VerdictBadge({ value, large = false }: { value: Verdict; large?: boolean }) {
  return (
    <span
      className={`${badgeBase} ${verdictColors[slug(value)] ?? ""} ${
        large ? "mt-[13px] mb-[17px] px-[11px] py-2 text-[14px]" : ""
      }`}
    >
      <Dot />
      {value}
    </span>
  );
}

export function StatusBadge({ value }: { value: Status }) {
  return (
    <span className={`${badgeBase} ${statusColors[slug(value)] ?? ""}`}>
      <Dot />
      {value}
    </span>
  );
}
