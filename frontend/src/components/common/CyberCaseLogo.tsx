import Image from "next/image";

export function CyberCaseLogo({ size = 32 }: { size?: number }) {
  return (
    <Image
      src="/cybercase-mark.png"
      alt=""
      width={size}
      height={size}
      className="shrink-0 rounded-md"
      priority
    />
  );
}
