"use client";

import type { ChatBaselineRelationship } from "@/lib/api";
import {
  GRAPH_NODE_HEIGHT,
  GRAPH_NODE_WIDTH,
  type GraphNodePosition,
  clampGraphLabel,
  connectorDashArray,
  rectangleBoundaryScale,
} from "./relationship-graph-geometry";

export function GraphEdge({
  relationship,
  source,
  target,
  markerId,
  selected,
  indexInPair,
  totalInPair,
  onSelect,
}: {
  relationship: ChatBaselineRelationship;
  source: GraphNodePosition;
  target: GraphNodePosition;
  markerId: string;
  selected: boolean;
  indexInPair: number;
  totalInPair: number;
  onSelect: () => void;
}) {
  const isSelf =
    relationship.subject_entity_id === relationship.object_entity_id;
  const strokeWidth = selected ? 3 : 1.5;
  const opacity = selected ? 1 : 0.65;

  let pathD = "";
  let labelX = 0;
  let labelY = 0;
  let midX = 0;
  let midY = 0;

  if (isSelf) {
    const rightEdge = source.left + GRAPH_NODE_WIDTH;
    const startY = source.top + 20;
    const endY = source.top + GRAPH_NODE_HEIGHT - 20;
    const controlX = rightEdge + 50;
    const controlY = source.y;

    pathD = `M ${rightEdge} ${startY} Q ${controlX} ${controlY} ${rightEdge} ${endY}`;
    labelX = rightEdge + 35;
    labelY = source.y;
    midX = labelX;
    midY = labelY;
  } else {
    const dx = target.x - source.x;
    const dy = target.y - source.y;
    const dist = Math.hypot(dx, dy) || 1;
    const ux = dx / dist;
    const uy = dy / dist;
    const nx = -uy;
    const ny = ux;

    let offset = (indexInPair - (totalInPair - 1) / 2) * 36;
    if (totalInPair === 1) {
      if (Math.abs(dy) < 30) {
        offset = Math.abs(dx) > 300 ? -65 : -24;
      } else if (Math.abs(dx) > 10 && Math.abs(dy) > 10) {
        const sign =
          source.left < target.left && source.top < target.top ? 1 : -1;
        offset = sign * 24;
      }
    }

    const rawMidX = (source.x + target.x) / 2;
    const rawMidY = (source.y + target.y) / 2;
    const controlX = rawMidX + nx * offset;
    const controlY = rawMidY + ny * offset;

    const startScale = rectangleBoundaryScale(
      controlX - source.x,
      controlY - source.y,
    );
    const startX = source.x + (controlX - source.x) * startScale;
    const startY = source.y + (controlY - source.y) * startScale;

    const endScale = rectangleBoundaryScale(
      controlX - target.x,
      controlY - target.y,
    );
    const endX = target.x + (controlX - target.x) * endScale;
    const endY = target.y + (controlY - target.y) * endScale;

    pathD = `M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`;
    labelX = 0.25 * startX + 0.5 * controlX + 0.25 * endX;
    labelY = 0.25 * startY + 0.5 * controlY + 0.25 * endY;
    midX = labelX;
    midY = labelY;
  }

  const labelText = clampGraphLabel(relationship.predicate, 28);
  const badgeWidth = Math.max(54, labelText.length * 6.2 + 14);
  const badgeHeight = 18;

  return (
    <g
      data-graph-edge-id={relationship.relationship_id}
      data-selected={selected}
      opacity={opacity}
      className="pointer-events-auto cursor-pointer"
      onClick={onSelect}
    >
      <path
        d={pathD}
        fill="none"
        stroke="var(--color-primary)"
        strokeWidth={strokeWidth}
        strokeDasharray={connectorDashArray(relationship.status)}
        markerEnd={`url(#${markerId})`}
      />
      {relationship.status === "contradicted" && (
        <g stroke="var(--color-primary)" strokeWidth={selected ? 3 : 2}>
          <line
            x1={midX - badgeWidth / 2 - 10}
            y1={midY - 5}
            x2={midX - badgeWidth / 2 - 2}
            y2={midY + 5}
          />
          <line
            x1={midX - badgeWidth / 2 - 2}
            y1={midY - 5}
            x2={midX - badgeWidth / 2 - 10}
            y2={midY + 5}
          />
        </g>
      )}
      <g transform={`translate(${labelX}, ${labelY})`}>
        <rect
          x={-badgeWidth / 2}
          y={-badgeHeight / 2}
          width={badgeWidth}
          height={badgeHeight}
          rx="9"
          fill="var(--color-ivory)"
          stroke={selected ? "var(--color-primary)" : "var(--color-line-strong)"}
          strokeWidth={selected ? 2 : 1}
        />
        <text
          data-graph-edge-label={relationship.relationship_id}
          x={0}
          y={3.5}
          textAnchor="middle"
          fill="var(--color-primary)"
          fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
          fontSize={selected ? 10 : 9}
          fontWeight={selected ? 800 : 600}
        >
          {labelText}
        </text>
      </g>
    </g>
  );
}
