export function getInstallCommand(skillName: string): string {
  return `npx skills add essentialsoft/agentskills@${skillName}`;
}
