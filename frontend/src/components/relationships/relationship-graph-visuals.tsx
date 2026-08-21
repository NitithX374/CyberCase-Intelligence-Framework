"use client";

import { Handle, Position } from "@xyflow/react";
import type { ChatRelationshipStatus } from "@/lib/api";
import {
  clampGraphLabel,
  connectorDashArray,
  graphLabelLines,
} from "./relationship-graph-geometry";

export const STATUS_LABELS: Record<ChatRelationshipStatus, string> = {
  reported: "Reported",
  suspected: "Suspected",
  contradicted: "Contradicted",
  not_established: "Not established",
};

export function RelationshipHeader({ count }: { count: number }) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <p className="text-[10px] font-extrabold uppercase tracking-[0.14em] text-ink-secondary">
          Dedicated relationship inspector
        </p>
        <h4 className="mt-1 text-sm font-extrabold text-ink">
          Candidate entity relationships
        </h4>
      </div>
      <span className="text-xs font-bold text-ink-secondary">{count}</span>
    </div>
  );
}
function CustomGraphNode({
  data,
}: {
  data: { entityId: string; label: string; selected: boolean };
}) {
  const lines = graphLabelLines(data.label);
  return (
    <div
      data-graph-node-id={data.entityId}
      data-selected={data.selected}
      className={`relative min-w-[172px] max-w-[200px] rounded-xl border p-3 text-center transition-all ${data.selected
          ? "border-primary bg-surface-nested ring-2 ring-primary shadow-md"
          : "border-line-strong bg-surface hover:border-primary hover:bg-surface-hover"
        }`}
    >
      <Handle type="target" position={Position.Top} className="!opacity-0" />
      <Handle type="source" position={Position.Bottom} className="!opacity-0" />
      <Handle type="target" position={Position.Left} id="left" className="!opacity-0" />
      <Handle type="source" position={Position.Right} id="right" className="!opacity-0" />

      <div className="flex h-full flex-col justify-center gap-1">
        <div className="text-xs font-bold leading-snug text-ink">
          {lines.map((line, idx) => (
            <div key={`${line}-${idx}`}>{line}</div>
          ))}
        </div>
        <div className="font-mono text-[9px] font-semibold text-ink-secondary">
          {clampGraphLabel(data.entityId, 24)}
        </div>
      </div>
    </div>
  );
}

export const relationshipNodeTypes = { customNode: CustomGraphNode };

export function GraphLegend() {
  const statuses: ChatRelationshipStatus[] = [
    "reported",
    "suspected",
    "contradicted",
    "not_established",
  ];
  return (
    <div
      data-graph-legend="true"
      className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-2 px-1 text-xs text-ink-secondary"
    >
      {statuses.map((status) => (
        <div key={status} className="flex items-center gap-2">
          <StatusConnector status={status} />
          <span className="font-bold text-ink">
            {STATUS_LABELS[status]}
          </span>
        </div>
      ))}
    </div>
  );
}

export function StatusConnector({ status }: { status: ChatRelationshipStatus }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 38 14" className="h-3.5 w-9">
      {status === "not_established" ? (
        <>
          <line
            x1="1"
            y1="7"
            x2="14"
            y2="7"
            stroke="currentColor"
            strokeWidth="2"
            strokeDasharray="2 5"
          />
          <line
            x1="24"
            y1="7"
            x2="37"
            y2="7"
            stroke="currentColor"
            strokeWidth="2"
            strokeDasharray="2 5"
          />
        </>
      ) : (
        <line
          x1="1"
          y1="7"
          x2="37"
          y2="7"
          stroke="currentColor"
          strokeWidth="2"
          strokeDasharray={connectorDashArray(status)}
        />
      )}
      {status === "contradicted" && (
        <g stroke="currentColor" strokeWidth="2">
          <line x1="15" y1="2" x2="23" y2="12" />
          <line x1="23" y1="2" x2="15" y2="12" />
        </g>
      )}
    </svg>
  );
}

function RelationshipLabels() {
  return (
    <div className="mt-3 flex flex-wrap gap-1.5" aria-label="Relationship labels">
      {[
        "Candidate",
        "User-reported",
        "Unverified",
      ].map((label) => (
        <span
          key={label}
          className="rounded-full border border-line-strong bg-surface-nested px-2 py-0.5 text-[9px] font-extrabold uppercase tracking-[0.1em] text-ink-secondary"
        >
          {label}
        </span>
      ))}
    </div>
  );
}

export function RelationshipTrustNotice() {
  return (
    <>
      <RelationshipLabels />
      <p className="mt-2 text-xs leading-5 text-ink-secondary">
        These source-explicit relationships are candidate, user-reported, and
        unverified. The graph is a visual inspection aid, not forensic proof.
      </p>
    </>
  );
}
