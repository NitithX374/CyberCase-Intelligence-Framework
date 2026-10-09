import type { HTMLAttributes } from "react";

export type IconName =
  | "overview"
  | "chat"
  | "plus"
  | "send"
  | "trash"
  | "close"
  | "chevron"
  | "external"
  | "alert"
  | "account"
  | "search"
  | "list"
  | "edit"
  | "eye"
  | "eye-off"
  | "check"
  | "log-out"
  | "folder"
  | "upload"
  | "download"
  | "refresh"
  | "info"
  | "spinner";

const nameToBoxicon: Record<IconName, string> = {
  overview: "bx-grid-alt",
  chat: "bx-message-square-dots",
  plus: "bx-plus",
  send: "bx-send",
  trash: "bx-trash",
  close: "bx-x",
  chevron: "bx-chevron-down",
  external: "bx-link-external",
  alert: "bx-error",
  account: "bx-user",
  search: "bx-search",
  list: "bx-list-ul",
  edit: "bx-edit-alt",
  eye: "bx-show",
  "eye-off": "bx-hide",
  check: "bx-check",
  "log-out": "bx-log-out",
  folder: "bx-folder",
  upload: "bx-upload",
  download: "bx-download",
  refresh: "bx-refresh",
  info: "bx-info-circle",
  spinner: "bx-loader-alt bx-spin",
};

export interface IconProps extends HTMLAttributes<HTMLElement> {
  name: IconName;
}

export function Icon({ name, className = "", ...props }: IconProps) {
  return (
    <i
      aria-hidden="true"
      className={`bx ${nameToBoxicon[name]} inline-flex items-center justify-center leading-none ${className}`}
      {...props}
    />
  );
}
