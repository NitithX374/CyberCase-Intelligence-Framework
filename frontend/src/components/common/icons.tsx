import type { SVGProps } from "react";

export type IconName =
  | "chat"
  | "plus"
  | "report"
  | "send"
  | "trash"
  | "close"
  | "chevron";

const paths: Record<IconName, React.ReactNode> = {
  chat: <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z" />,
  plus: <path d="M12 5v14M5 12h14" />,
  report: (
    <>
      <path d="M6 3h9l3 3v15H6z" />
      <path d="M15 3v4h4M9 12h6M9 16h6" />
    </>
  ),
  send: <path d="m22 2-7 20-4-9-9-4Zm0 0L11 13" />,
  trash: (
    <>
      <path d="M3 6h18M8 6V4h8v2M19 6l-1 15H6L5 6" />
      <path d="M10 11v5M14 11v5" />
    </>
  ),
  close: <path d="M18 6 6 18M6 6l12 12" />,
  chevron: <polyline points="6 9 12 15 18 9" />,
};

interface IconProps extends SVGProps<SVGSVGElement> {
  name: IconName;
}

export function Icon({ name, ...props }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      {paths[name]}
    </svg>
  );
}
