import type { HomePillarVisual } from "./home-content";

export function HomeMiniVisual({ type }: { type: HomePillarVisual }) {
  if (type === "bars") {
    return (
      <div className="space-y-3 pt-2">
        {[100, 78, 88, 56, 70].map((width, index) => (
          <div
            key={index}
            className="h-px bg-ivory/30"
            style={{ width: `${width}%` }}
          />
        ))}
      </div>
    );
  }

  if (type === "grid") {
    return (
      <div className="grid grid-cols-5 gap-2 pt-2">
        {Array.from({ length: 10 }).map((_, index) => (
          <div
            key={index}
            className={`aspect-square border ${
              index === 2 || index === 6
                ? "border-ivory bg-ivory"
                : "border-ivory/30"
            }`}
          />
        ))}
      </div>
    );
  }

  return (
    <svg
      viewBox="0 0 260 120"
      className="mt-2 h-28 w-full"
      role="img"
      aria-label="Threat trend"
    >
      <line x1="10" y1="102" x2="250" y2="102" stroke="rgba(255,255,255,.2)" />
      <polyline
        points="10,88 68,45 118,72 168,30 220,58 250,18"
        fill="none"
        stroke="var(--color-ivory)"
        strokeWidth="2"
      />
      {["10,88", "68,45", "118,72", "168,30", "220,58", "250,18"].map(
        (point) => {
          const [cx, cy] = point.split(",");
          return <circle key={point} cx={cx} cy={cy} r="3" fill="var(--color-ivory)" />;
        },
      )}
    </svg>
  );
}
