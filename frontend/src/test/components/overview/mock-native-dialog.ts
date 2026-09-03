import { afterAll, beforeAll } from "vitest";

export function mockNativeDialog() {
  const prototype = HTMLDialogElement.prototype;
  const originalShow = Object.getOwnPropertyDescriptor(prototype, "showModal");
  const originalClose = Object.getOwnPropertyDescriptor(prototype, "close");
  beforeAll(() => {
    Object.defineProperty(prototype, "showModal", { configurable: true, value(this: HTMLDialogElement) {
      this.setAttribute("open", "");
      this.querySelector<HTMLButtonElement>("button")?.focus();
    } });
    Object.defineProperty(prototype, "close", { configurable: true, value(this: HTMLDialogElement) {
      this.removeAttribute("open");
    } });
  });
  afterAll(() => {
    if (originalShow) Object.defineProperty(prototype, "showModal", originalShow);
    else Reflect.deleteProperty(prototype, "showModal");
    if (originalClose) Object.defineProperty(prototype, "close", originalClose);
    else Reflect.deleteProperty(prototype, "close");
  });
}
