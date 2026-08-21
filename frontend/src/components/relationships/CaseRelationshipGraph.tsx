"use client";

import { useId, useState } from "react";
import type {
  ChatBaselineEntity,
  ChatBaselineRelationship,
} from "@/lib/api";
import {
  RelationshipHeader,
  RelationshipTrustNotice,
  STATUS_LABELS,
  StatusConnector,
} from "./relationship-graph-visuals";
import { RelationshipCanvas } from "./relationship-graph-canvas";

interface CaseRelationshipGraphProps {
  entities: ChatBaselineEntity[];
  relationships: ChatBaselineRelationship[];
}

export function CaseRelationshipGraph({
  entities,
  relationships,
}: CaseRelationshipGraphProps) {
  const detailId = useId();
  const [selectedRelationshipId, setSelectedRelationshipId] = useState(
    relationships[0]?.relationship_id ?? "",
  );
  const selectedRelationship =
    relationships.find(
      (relationship) =>
        relationship.relationship_id === selectedRelationshipId,
    ) ?? relationships[0];
  const entitiesById = new Map(
    entities.map((entity) => [entity.entity_id, entity]),
  );

  if (!selectedRelationship) {
    return (
      <section
        aria-label="Candidate entity relationships"
        className="mb-4 min-w-0 max-w-full rounded-xl border border-dashed border-line-strong bg-surface-nested p-4"
      >
        <RelationshipHeader count={0} />
        <RelationshipTrustNotice />
        <p className="mt-3 text-xs leading-5 text-ink-secondary">
          No explicit entity-to-entity relationship was extracted.
        </p>
      </section>
    );
  }

  const selectedSubject = entitiesById.get(
    selectedRelationship.subject_entity_id,
  );
  const selectedObject = entitiesById.get(selectedRelationship.object_entity_id);

  return (
    <section
      aria-label="Candidate entity relationships"
      className="mb-4 min-w-0 max-w-full rounded-xl border border-line bg-surface-nested p-3 sm:p-4"
    >
      <RelationshipHeader count={relationships.length} />
      <RelationshipTrustNotice />

      <div className="mt-5">
        <RelationshipCanvas
          entities={entities}
          relationships={relationships}
          selectedRelationshipId={selectedRelationship.relationship_id}
          onSelectRelationship={setSelectedRelationshipId}
        />
      </div>

      <div className="mt-5 grid min-w-0 max-w-full gap-4 lg:grid-cols-12">
        <div className="min-w-0 lg:col-span-5">
          <p className="text-[10px] font-extrabold uppercase tracking-[0.14em] text-ink-secondary">
            Relationship list
          </p>
          <div className="mt-2 space-y-2">
            {relationships.map((relationship) => {
              const subject = entitiesById.get(relationship.subject_entity_id);
              const object = entitiesById.get(relationship.object_entity_id);
              const selected =
                relationship.relationship_id ===
                selectedRelationship.relationship_id;
              return (
                <button
                  key={relationship.relationship_id}
                  type="button"
                  aria-pressed={selected}
                  aria-controls={detailId}
                  onClick={() =>
                    setSelectedRelationshipId(relationship.relationship_id)
                  }
                  className={`w-full rounded-xl border p-3 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-surface-nested ${selected
                      ? "border-primary bg-surface shadow-[0_2px_8px_rgba(39,39,39,0.07)]"
                      : "border-line bg-surface hover:border-line-strong hover:bg-surface-hover"
                    }`}
                >
                  <span className="flex items-start justify-between gap-3">
                    <span className="min-w-0 text-sm font-bold leading-5 text-ink [overflow-wrap:anywhere]">
                      {subject?.name ?? relationship.subject_entity_id}
                      <span aria-hidden="true"> → </span>
                      {object?.name ?? relationship.object_entity_id}
                    </span>
                    <span className="shrink-0 text-[9px] font-extrabold uppercase tracking-[0.1em] text-ink-secondary">
                      {relationship.relationship_id}
                    </span>
                  </span>
                  <span className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-[11px] text-ink-secondary">
                    <span className="font-mono [overflow-wrap:anywhere]">
                      {relationship.predicate}
                    </span>
                    <span className="inline-flex items-center gap-1.5 font-bold">
                      <StatusConnector status={relationship.status} />
                      {STATUS_LABELS[relationship.status]}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="min-w-0 max-w-full lg:col-span-7">
          <div
            id={detailId}
            aria-live="polite"
            className="rounded-xl border border-line bg-surface p-4"
          >
            <p className="text-[10px] font-extrabold uppercase tracking-[0.14em] text-ink-secondary">
              Selected relationship detail
            </p>
            <p className="mt-2 text-sm font-bold leading-6 text-ink [overflow-wrap:anywhere]">
              {selectedRelationship.statement}
            </p>
            <dl className="mt-3 grid gap-3 text-xs sm:grid-cols-2">
              <div className="sm:col-span-2">
                <dt className="font-extrabold uppercase tracking-[0.1em] text-ink-secondary">
                  Source → target
                </dt>
                <dd className="mt-1 leading-5 text-ink [overflow-wrap:anywhere]">
                  {selectedSubject?.name ??
                    selectedRelationship.subject_entity_id}
                  <span aria-hidden="true"> → </span>
                  {selectedObject?.name ?? selectedRelationship.object_entity_id}
                </dd>
              </div>
              <div>
                <dt className="font-extrabold uppercase tracking-[0.1em] text-ink-secondary">
                  Status
                </dt>
                <dd className="mt-1 inline-flex items-center gap-1.5 font-bold text-ink">
                  <StatusConnector status={selectedRelationship.status} />
                  {STATUS_LABELS[selectedRelationship.status]}
                </dd>
              </div>
              <div>
                <dt className="font-extrabold uppercase tracking-[0.1em] text-ink-secondary">
                  Confidence
                </dt>
                <dd className="mt-1 capitalize text-ink">
                  {selectedRelationship.confidence}
                </dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="font-extrabold uppercase tracking-[0.1em] text-ink-secondary">
                  Predicate
                </dt>
                <dd className="mt-1 font-mono text-ink [overflow-wrap:anywhere]">
                  {selectedRelationship.predicate}
                </dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="font-extrabold uppercase tracking-[0.1em] text-ink-secondary">
                  Source message IDs
                </dt>
                <dd className="mt-1 flex flex-wrap gap-1.5">
                  {selectedRelationship.source_message_ids.map((messageId) => (
                    <span
                      key={messageId}
                      className="max-w-full rounded border border-line bg-surface-nested px-1.5 py-1 font-mono text-[10px] leading-4 text-ink-secondary [overflow-wrap:anywhere]"
                    >
                      {messageId}
                    </span>
                  ))}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </section>
  );
}
