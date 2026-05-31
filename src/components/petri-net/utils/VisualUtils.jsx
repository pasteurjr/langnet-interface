/**
 * Wraps text to fit within a maximum width
 */
export const wrapText = (text, maxWidth) => {
    // Certifique-se de que text seja uma string e não seja undefined/null
    const safeText = String(text || "").trim();
  
    if (!safeText || safeText.length <= maxWidth) return safeText;
  
    const words = safeText.split(" ");
    const lines = [];
    let currentLine = words[0] || "";
  
    for (let i = 1; i < words.length; i++) {
      if (currentLine.length + words[i].length + 1 <= maxWidth) {
        currentLine += " " + words[i]; // Garante espaço entre palavras
      } else {
        lines.push(currentLine);
        currentLine = words[i] || "";
      }
    }
  
    if (currentLine) {
      lines.push(currentLine);
    }
  
    // Usar um separador visível que será interpretado corretamente pelo SVG
    return lines.join("\n");
  };
  
  /**
   * Formats tokens for display in place nodes
   */
  export const formatTokens = (tokens) => {
    if (!tokens && tokens !== 0) return "";
    if (tokens >= 10) return tokens.toString();
  
    return Array(Math.ceil(tokens / 3))
      .fill(0)
      .map((_, rowIndex) => {
        const start = rowIndex * 3;
        const count = Math.min(3, tokens - start);
        return Array(count).fill("●").join("");
      })
      .join("\n");
  };