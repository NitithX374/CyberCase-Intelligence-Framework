import type {
  ChatBaselineEntity,
  ChatBaselineRelationship,
  ChatRelationshipStatus,
} from "@/lib/api";

export const GRAPH_NODE_WIDTH = 172;
export const GRAPH_NODE_HEIGHT = 78;

export interface GraphPoint {
  x: number;
  y: number;
}
export interface GraphNodePosition extends GraphPoint {
  left: number;
  top: number;
}

export function computeLayeredNodePositions(
  entities: ChatBaselineEntity[],
  relationships: ChatBaselineRelationship[],
): Map<string, GraphNodePosition> {
  const connectedIds = Array.from(
    new Set(
      relationships.flatMap((r) => [r.subject_entity_id, r.object_entity_id]),
    ),
  );

  const allEntityIds = Array.from(
    new Set([
      ...connectedIds,
      ...entities.map((e) => e.entity_id),
    ]),
  );

  if (allEntityIds.length === 0) return new Map();

  const inDegree = new Map<string, number>();
  const outEdges = new Map<string, Set<string>>();
  allEntityIds.forEach((id) => {
    inDegree.set(id, 0);
    outEdges.set(id, new Set());
  });

  for (const rel of relationships) {
    if (rel.subject_entity_id !== rel.object_entity_id) {
      outEdges.get(rel.subject_entity_id)?.add(rel.object_entity_id);
      inDegree.set(
        rel.object_entity_id,
        (inDegree.get(rel.object_entity_id) || 0) + 1,
      );
    }
  }

  const layers = new Map<string, number>();
  const queue: { id: string; layer: number }[] = [];

  allEntityIds.forEach((id) => {
    if ((inDegree.get(id) || 0) === 0) {
      queue.push({ id, layer: 0 });
      layers.set(id, 0);
    }
  });

  if (queue.length === 0 && allEntityIds.length > 0) {
    queue.push({ id: allEntityIds[0], layer: 0 });
    layers.set(allEntityIds[0], 0);
  }

  const visited = new Set<string>();
  while (queue.length > 0) {
    const { id, layer } = queue.shift()!;
    if (visited.has(id)) continue;
    visited.add(id);

    const currentLayer = layers.get(id) ?? layer;
    const targets = outEdges.get(id) || new Set();
    for (const targetId of targets) {
      const nextLayer = Math.max(layers.get(targetId) ?? 0, currentLayer + 1);
      layers.set(targetId, nextLayer);
      queue.push({ id: targetId, layer: nextLayer });
    }
  }

  allEntityIds.forEach((id) => {
    if (!layers.has(id)) layers.set(id, 0);
  });

  const nodesByLayer = new Map<number, string[]>();
  allEntityIds.forEach((id) => {
    const l = layers.get(id) || 0;
    const list = nodesByLayer.get(l) || [];
    list.push(id);
    nodesByLayer.set(l, list);
  });

  const posMap = new Map<string, GraphNodePosition>();
  const sortedLayerKeys = Array.from(nodesByLayer.keys()).sort((a, b) => a - b);

  sortedLayerKeys.forEach((layerIndex, colIdx) => {
    const nodeIdsInLayer = nodesByLayer.get(layerIndex) || [];
    nodeIdsInLayer.forEach((id, rowIdx) => {
      const left = 48 + colIdx * 360;
      const stagger = colIdx % 2 === 1 ? 36 : 0;
      const top = 40 + rowIdx * 220 + stagger;
      posMap.set(id, {
        left,
        top,
        x: left + GRAPH_NODE_WIDTH / 2,
        y: top + GRAPH_NODE_HEIGHT / 2,
      });
    });
  });

  return posMap;
}

export function graphNodePosition(index: number): GraphNodePosition {
  const column = Math.floor(index / 2);
  const row = index % 2;
  const left = 48 + column * 360;
  const top = row === 0 ? 40 : 250;
  return {
    left,
    top,
    x: left + GRAPH_NODE_WIDTH / 2,
    y: top + GRAPH_NODE_HEIGHT / 2,
  };
}

export function rectangleBoundaryScale(deltaX: number, deltaY: number): number {
  if (deltaX === 0 && deltaY === 0) return 0;
  const horizontalScale =
    deltaX === 0 ? Number.POSITIVE_INFINITY : GRAPH_NODE_WIDTH / 2 / Math.abs(deltaX);
  const verticalScale =
    deltaY === 0 ? Number.POSITIVE_INFINITY : GRAPH_NODE_HEIGHT / 2 / Math.abs(deltaY);
  const scale = Math.min(horizontalScale, verticalScale);
  return Number.isFinite(scale) ? scale : 0;
}

export function connectorDashArray(status: ChatRelationshipStatus) {
  if (status === "suspected") return "10 7";
  if (status === "not_established") return "2 8";
  return undefined;
}

export function graphLabelLines(value: string): string[] {
  const normalized = value.trim();
  if (normalized.length <= 25) return [normalized];
  const firstBreak = normalized.lastIndexOf(" ", 25);
  const splitAt = firstBreak > 10 ? firstBreak : 25;
  return [
    normalized.slice(0, splitAt).trim(),
    clampGraphLabel(normalized.slice(splitAt).trim(), 25),
  ];
}

export function clampGraphLabel(value: string, maxLength: number): string {
  return value.length <= maxLength
    ? value
    : `${value.slice(0, Math.max(1, maxLength - 1))}…`;
}
