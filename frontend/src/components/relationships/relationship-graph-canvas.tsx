"use client";

import { useEffect, useId, useMemo } from "react";
import {
  Background,
  BackgroundVariant,
  Controls,
  Node,
  ReactFlow,
  ViewportPortal,
  useNodesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type {
  ChatBaselineEntity,
  ChatBaselineRelationship,
} from "@/lib/api";
import {
  GRAPH_NODE_HEIGHT,
  GRAPH_NODE_WIDTH,
  computeLayeredNodePositions,
  graphNodePosition,
} from "./relationship-graph-geometry";
import { GraphEdge } from "./relationship-graph-edge";
import { GraphLegend, relationshipNodeTypes } from "./relationship-graph-visuals";

export function RelationshipCanvas({
  entities,
  relationships,
  selectedRelationshipId,
  onSelectRelationship,
}: {
  entities: ChatBaselineEntity[];
  relationships: ChatBaselineRelationship[];
  selectedRelationshipId: string;
  onSelectRelationship: (id: string) => void;
}) {
  const markerId = `relationship-arrow-${useId().replace(/:/g, "")}`;
  const entitiesById = useMemo(
    () => new Map(entities.map((entity) => [entity.entity_id, entity])),
    [entities],
  );

  const connectedEntityIds = useMemo(
    () =>
      Array.from(
        new Set(
          relationships.flatMap((relationship) => [
            relationship.subject_entity_id,
            relationship.object_entity_id,
          ]),
        ),
      ).sort(),
    [relationships],
  );

  const positionsById = useMemo(
    () => computeLayeredNodePositions(entities, relationships),
    [entities, relationships],
  );

  const graphEntities = useMemo(
    () =>
      connectedEntityIds.map((entityId, index) => ({
        entityId,
        entity: entitiesById.get(entityId),
        position:
          positionsById.get(entityId) || graphNodePosition(index),
      })),
    [connectedEntityIds, entitiesById, positionsById],
  );

  const selectedRelationship = useMemo(
    () =>
      relationships.find(
        (rel) => rel.relationship_id === selectedRelationshipId,
      ),
    [relationships, selectedRelationshipId],
  );

  const selectedEndpointIds = useMemo(
    () =>
      new Set(
        selectedRelationship
          ? [
            selectedRelationship.subject_entity_id,
            selectedRelationship.object_entity_id,
          ]
          : [],
      ),
    [selectedRelationship],
  );

  const pairGroups = useMemo(() => {
    const map = new Map<string, ChatBaselineRelationship[]>();
    for (const rel of relationships) {
      const pairKey = [rel.subject_entity_id, rel.object_entity_id]
        .sort()
        .join("::");
      const group = map.get(pairKey) || [];
      group.push(rel);
      map.set(pairKey, group);
    }
    return map;
  }, [relationships]);

  const sortedRelationships = useMemo(() => {
    return [...relationships].sort((a, b) => {
      if (a.relationship_id === selectedRelationshipId) return 1;
      if (b.relationship_id === selectedRelationshipId) return -1;
      return 0;
    });
  }, [relationships, selectedRelationshipId]);

  const initialNodes: Node[] = useMemo(() => {
    return graphEntities.map(({ entityId, entity, position }) => ({
      id: entityId,
      type: "customNode",
      position: { x: position.left, y: position.top },
      data: {
        entityId,
        label: entity?.name ?? entityId,
        selected: false,
      },
    }));
  }, [graphEntities]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);

  useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes, setNodes]);

  useEffect(() => {
    setNodes((prevNodes) =>
      prevNodes.map((node) => {
        const isSelected = selectedEndpointIds.has(node.id);
        if (node.data.selected === isSelected) return node;
        return {
          ...node,
          data: {
            ...node.data,
            selected: isSelected,
          },
        };
      })
    );
  }, [selectedEndpointIds, setNodes]);

  return (
    <div className="min-w-0 max-w-full rounded-xl border border-line bg-surface p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-[10px] font-extrabold uppercase tracking-[0.14em] text-ink-secondary">
          Relationship canvas
        </p>
        <p className="text-[10px] text-ink-secondary">
          Drag nodes to reposition · Zoom & Pan enabled
        </p>
      </div>
      <div
        data-relationship-graph-scroller="true"
        className="mt-2 h-[420px] min-w-0 max-w-full overflow-x-auto rounded-lg border border-line bg-surface overflow-hidden"
      >
        <ReactFlow
          nodes={nodes}
          onNodesChange={onNodesChange}
          nodeTypes={relationshipNodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.4}
          maxZoom={2}
          proOptions={{ hideAttribution: true }}
        >
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="var(--color-line)" />
          <Controls className="!rounded-lg !border-line !bg-surface !shadow-sm" />

          <ViewportPortal>
            <svg
              aria-hidden="true"
              data-relationship-graph="true"
              className="react-flow__edges h-[420px] min-w-[960px]"
              style={{ overflow: "visible", pointerEvents: "none" }}
            >
              <defs>
                <marker
                  id={markerId}
                  markerWidth="8"
                  markerHeight="8"
                  refX="7"
                  refY="4"
                  orient="auto"
                  markerUnits="strokeWidth"
                >
                  <path d="M0,0 L8,4 L0,8 Z" fill="var(--color-primary)" />
                </marker>
              </defs>

              {sortedRelationships.map((relationship) => {
                const sourceNode = nodes.find(
                  (n) => n.id === relationship.subject_entity_id,
                );
                const targetNode = nodes.find(
                  (n) => n.id === relationship.object_entity_id,
                );
                const sourcePos = sourceNode
                  ? {
                    left: sourceNode.position.x,
                    top: sourceNode.position.y,
                    x: sourceNode.position.x + GRAPH_NODE_WIDTH / 2,
                    y: sourceNode.position.y + GRAPH_NODE_HEIGHT / 2,
                  }
                  : positionsById.get(relationship.subject_entity_id);
                const targetPos = targetNode
                  ? {
                    left: targetNode.position.x,
                    top: targetNode.position.y,
                    x: targetNode.position.x + GRAPH_NODE_WIDTH / 2,
                    y: targetNode.position.y + GRAPH_NODE_HEIGHT / 2,
                  }
                  : positionsById.get(relationship.object_entity_id);

                if (!sourcePos || !targetPos) return null;

                const pairKey = [
                  relationship.subject_entity_id,
                  relationship.object_entity_id,
                ]
                  .sort()
                  .join("::");
                const group = pairGroups.get(pairKey) || [relationship];
                const indexInPair = group.findIndex(
                  (r) => r.relationship_id === relationship.relationship_id,
                );

                return (
                  <GraphEdge
                    key={relationship.relationship_id}
                    relationship={relationship}
                    source={sourcePos}
                    target={targetPos}
                    markerId={markerId}
                    selected={
                      relationship.relationship_id === selectedRelationshipId
                    }
                    indexInPair={indexInPair}
                    totalInPair={group.length}
                    onSelect={() => onSelectRelationship(relationship.relationship_id)}
                  />
                );
              })}
            </svg>
          </ViewportPortal>
        </ReactFlow>
      </div>

      <GraphLegend />
    </div>
  );
}
