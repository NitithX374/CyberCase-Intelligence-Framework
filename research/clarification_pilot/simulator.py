"""The stand-in for the user, and the only holder of the hidden context.

An arm is handed this object's ``answer`` method, not the object -- and never
the ``HiddenContext`` itself. So the arm can ask a question and read a reply,
and has no way to read the rubric, the full task or the gold answer. The
boundary is enforced by what is passed, not by a convention.

The simulator answers from the reference and says so when the reference does not
cover what was asked, which is what makes ``unknown_information`` a real stop
condition rather than an invented fact that looks like progress.
"""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import CallRecord, HiddenContext, SimulatorReply
from .prompts import SIMULATOR_V1, simulator_messages
from .provider import Provider

# What the simulator says when the model call itself failed. Treated as "did
# not know" so the loop stops rather than spending its budget on silence.
NO_REPLY = SimulatorReply(answer="I am not sure about that.", knew=False)


@dataclass
class UserSimulator:
    """Answers the candidate's questions from information the candidate cannot see."""

    provider: Provider
    hidden: HiddenContext

    async def answer(self, question: str, sink: list[CallRecord]) -> SimulatorReply:
        reply = await self.provider.structured(
            messages=simulator_messages(self.hidden, question),
            schema=SimulatorReply,
            stage="simulator",
            role="simulator",
            prompt_version=SIMULATOR_V1,
            sink=sink,
        )
        return reply if reply is not None else NO_REPLY


class SilentSimulator:
    """A simulator that is never asked anything.

    Arms A, B and C are non-interactive, and passing them this makes that a
    property of the run rather than a promise: if one of them ever asks, the
    call raises instead of quietly succeeding.
    """

    async def answer(self, question: str, sink: list[CallRecord]) -> SimulatorReply:
        raise AssertionError("A non-interactive arm tried to ask the user a question")


__all__ = ["NO_REPLY", "SilentSimulator", "UserSimulator"]
