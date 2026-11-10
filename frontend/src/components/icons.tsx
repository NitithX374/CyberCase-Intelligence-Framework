import {
  Activity,
  BookOpen,
  BriefcaseBusiness,
  Check,
  ChevronDown,
  Clock,
  Cpu,
  Download,
  ExternalLink,
  Eye,
  EyeOff,
  FileText,
  Flag,
  Folder,
  FolderOpen,
  Info,
  LayoutGrid,
  Link2,
  List,
  ListChecks,
  LoaderCircle,
  LogOut,
  MessageSquareMore,
  PenLine,
  Play,
  Plus,
  RefreshCw,
  Scale,
  Search,
  SendHorizontal,
  Trash2,
  TriangleAlert,
  Upload,
  User,
  Users,
  X,
  type LucideIcon,
} from "lucide-react";

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
  | "spinner"
  | "case"
  | "sources"
  | "report"
  | "timeline"
  | "people"
  | "impact"
  | "attention"
  | "summary"
  | "findings"
  | "references"
  | "technical"
  | "legal"
  | "play";

const icons: Record<IconName, LucideIcon> = {
  overview: LayoutGrid,
  chat: MessageSquareMore,
  plus: Plus,
  send: SendHorizontal,
  trash: Trash2,
  close: X,
  chevron: ChevronDown,
  external: ExternalLink,
  alert: TriangleAlert,
  account: User,
  search: Search,
  list: List,
  edit: PenLine,
  eye: Eye,
  "eye-off": EyeOff,
  check: Check,
  "log-out": LogOut,
  folder: Folder,
  upload: Upload,
  download: Download,
  refresh: RefreshCw,
  info: Info,
  spinner: LoaderCircle,
  case: BriefcaseBusiness,
  sources: FolderOpen,
  report: FileText,
  timeline: Clock,
  people: Users,
  impact: Activity,
  attention: Flag,
  summary: BookOpen,
  findings: ListChecks,
  references: Link2,
  technical: Cpu,
  legal: Scale,
  play: Play,
};

export function Icon({ name, className = "" }: { name: IconName; className?: string }) {
  const Glyph = icons[name];
  return (
    <Glyph
      aria-hidden="true"
      size="1em"
      strokeWidth={1.75}
      className={`inline-block shrink-0 ${name === "spinner" ? "animate-spin motion-reduce:animate-none" : ""} ${className}`}
    />
  );
}
