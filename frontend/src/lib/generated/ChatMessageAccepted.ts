import type { ChatMessageRead } from "./ChatMessageRead";
import type { ChatRunRead } from "./ChatRunRead";

export type ChatMessageAccepted = {
    message: ChatMessageRead;
    run: ChatRunRead;
};
