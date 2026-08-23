import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MitreCandidatePanel } from "@/components/conversation/MitreCandidatePanel";

describe("MitreCandidatePanel", () => {
  it("renders candidate-only external context without confidence language", () => {
    render(
      <MitreCandidatePanel
        candidates={[
          {
            associationId: "MA-01",
            techniqueId: "T1078",
            techniqueName: "Valid Accounts",
            claims: [
              {
                claimId: "A-01",
                text: "Administrative credentials were reported compromised.",
                claimType: "reported",
                epistemicStatus: "reported",
              },
            ],
            reason: "The behavior concerns use of a valid administrative credential.",
          },
        ]}
      />,
    );

    const candidate = screen.getByRole("article", {
      name: "T1078 MITRE candidate",
    });
    expect(within(candidate).getByText("T1078")).toBeInTheDocument();
    expect(within(candidate).getByText("Valid Accounts")).toBeInTheDocument();
    expect(within(candidate).getByText("A-01")).toBeInTheDocument();
    expect(within(candidate).getByText("Candidate only")).toBeInTheDocument();
    expect(
      within(candidate).getByText("External technical context"),
    ).toBeInTheDocument();
    expect(within(candidate).getByText("Not incident evidence")).toBeInTheDocument();
    expect(within(candidate).queryByText(/confidence/i)).not.toBeInTheDocument();
    expect(within(candidate).queryByText(/probability/i)).not.toBeInTheDocument();
    expect(within(candidate).queryByText(/score/i)).not.toBeInTheDocument();
  });

  it("renders nothing when there are no admitted candidates", () => {
    const { container } = render(<MitreCandidatePanel candidates={[]} />);
    expect(container).toBeEmptyDOMElement();
  });
});
