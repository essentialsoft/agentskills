import { useState } from "react";

type CopyCommandProps = {
  command: string;
};

export function CopyCommand({ command }: CopyCommandProps) {
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(command);
      setStatus("success");
    } catch {
      setStatus("error");
    }
  };

  return (
    <section className="copy-command">
      <p>Install command</p>
      <pre>{command}</pre>
      <button type="button" onClick={handleCopy}>
        Copy command
      </button>
      {status === "success" ? (
        <small role="status">Copied.</small>
      ) : null}
      {status === "error" ? (
        <small role="status">Copy failed. Copy manually from the command text.</small>
      ) : null}
    </section>
  );
}
