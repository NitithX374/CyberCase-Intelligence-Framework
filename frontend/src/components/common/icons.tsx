import type { HTMLAttributes } from "react";

export type KnownIconName =
  | "overview"
  | "sources"
  | "technical"
  | "issues"
  | "chat"
  | "plus"
  | "report"
  | "send"
  | "trash"
  | "close"
  | "chevron"
  | "external"
  | "error"
  | "alert"
  | "expand"
  | "collapse"
  | "account"
  | "search"
  | "list"
  | "edit"
  | "lock"
  | "mail"
  | "eye"
  | "eye-off"
  | "shield"
  | "check"
  | "log-out"
  | "folder"
  | "narrative"
  | "upload"
  | "download"
  | "refresh"
  | "info"
  | "chevron-right"
  | "legal"
  | "spinner";

export type IconName = KnownIconName | (string & {});

const nameToBoxicon: Record<string, string> = {
  overview: "bx-grid-alt",
  sources: "bx-file",
  technical: "bx-shield-quarter",
  issues: "bx-error-circle",
  chat: "bx-message-square-dots",
  plus: "bx-plus",
  report: "bx-file-blank",
  send: "bx-send",
  trash: "bx-trash",
  close: "bx-x",
  chevron: "bx-chevron-down",
  external: "bx-link-external",
  error: "bx-error-circle",
  alert: "bx-error",
  expand: "bx-expand-alt",
  collapse: "bx-collapse-alt",
  account: "bx-user",
  search: "bx-search",
  list: "bx-list-ul",
  edit: "bx-edit-alt",
  lock: "bx-lock-alt",
  mail: "bx-envelope",
  eye: "bx-show",
  "eye-off": "bx-hide",
  shield: "bx-shield",
  check: "bx-check",
  "log-out": "bx-log-out",
  folder: "bx-folder",
  narrative: "bx-detail",
  upload: "bx-upload",
  download: "bx-download",
  refresh: "bx-refresh",
  info: "bx-info-circle",
  "chevron-right": "bx-chevron-right",
  legal: "bx-book-bookmark",
  spinner: "bx-loader-alt bx-spin",
};

export interface IconProps extends HTMLAttributes<HTMLElement> {
  name: IconName;
}

export function Icon({ name, className = "", ...props }: IconProps) {
  const iconClass = nameToBoxicon[name] ?? (name.startsWith("bx") ? name : `bx-${name}`);
  return (
    <i
      aria-hidden="true"
      className={`bx ${iconClass} inline-flex items-center justify-center leading-none ${className}`}
      {...props}
    />
  );
}
