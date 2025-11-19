import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

/**
 * Exporta conteúdo markdown para PDF
 * Renderiza o markdown em HTML temporário e converte para PDF
 */
export const exportMarkdownToPDF = async (
  markdownContent: string,
  filename: string = 'requisitos.pdf'
): Promise<void> => {
  try {
    // Criar elemento temporário para renderização
    const tempDiv = document.createElement('div');
    tempDiv.style.position = 'absolute';
    tempDiv.style.left = '-9999px';
    tempDiv.style.width = '800px';
    tempDiv.style.padding = '40px';
    tempDiv.style.backgroundColor = 'white';
    tempDiv.style.fontFamily = 'Arial, sans-serif';
    tempDiv.style.fontSize = '14px';
    tempDiv.style.lineHeight = '1.6';
    tempDiv.style.color = '#333';

    // Renderizar markdown como HTML
    tempDiv.innerHTML = convertMarkdownToHTML(markdownContent);

    document.body.appendChild(tempDiv);

    // Aplicar estilos ao conteúdo renderizado
    applyPDFStyles(tempDiv);

    // Capturar como imagem
    const canvas = await html2canvas(tempDiv, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    });

    // Remover elemento temporário
    document.body.removeChild(tempDiv);

    // Criar PDF
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });

    const imgWidth = 210; // A4 width in mm
    const pageHeight = 297; // A4 height in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;
    let position = 0;

    // Adicionar primeira página
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    // Adicionar páginas adicionais se necessário
    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    // Salvar PDF
    pdf.save(filename);
  } catch (error) {
    console.error('Erro ao exportar PDF:', error);
    throw new Error('Falha ao exportar documento para PDF');
  }
};

/**
 * Converte markdown básico para HTML
 * Implementação simplificada para suporte básico de markdown
 */
const convertMarkdownToHTML = (markdown: string): string => {
  let html = markdown;

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/_(.*?)_/g, '<em>$1</em>');

  // Code inline
  html = html.replace(/`(.*?)`/g, '<code>$1</code>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

  // Listas não ordenadas
  html = html.replace(/^\* (.+)$/gim, '<li>$1</li>');
  html = html.replace(/^- (.+)$/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

  // Listas ordenadas
  html = html.replace(/^\d+\. (.+)$/gim, '<li>$1</li>');

  // Parágrafos
  html = html.split('\n\n').map(para => {
    if (
      para.trim().startsWith('<h') ||
      para.trim().startsWith('<ul') ||
      para.trim().startsWith('<ol') ||
      para.trim().startsWith('<li')
    ) {
      return para;
    }
    return `<p>${para.trim()}</p>`;
  }).join('\n');

  // Line breaks
  html = html.replace(/\n/g, '<br>');

  return html;
};

/**
 * Aplica estilos CSS ao conteúdo para melhor renderização em PDF
 */
const applyPDFStyles = (container: HTMLElement): void => {
  // Headers
  const h1Elements = container.querySelectorAll('h1');
  h1Elements.forEach(el => {
    (el as HTMLElement).style.fontSize = '28px';
    (el as HTMLElement).style.fontWeight = 'bold';
    (el as HTMLElement).style.color = '#2c3e50';
    (el as HTMLElement).style.borderBottom = '3px solid #667eea';
    (el as HTMLElement).style.paddingBottom = '12px';
    (el as HTMLElement).style.marginTop = '0';
    (el as HTMLElement).style.marginBottom = '20px';
  });

  const h2Elements = container.querySelectorAll('h2');
  h2Elements.forEach(el => {
    (el as HTMLElement).style.fontSize = '22px';
    (el as HTMLElement).style.fontWeight = 'bold';
    (el as HTMLElement).style.color = '#34495e';
    (el as HTMLElement).style.marginTop = '32px';
    (el as HTMLElement).style.marginBottom = '16px';
  });

  const h3Elements = container.querySelectorAll('h3');
  h3Elements.forEach(el => {
    (el as HTMLElement).style.fontSize = '18px';
    (el as HTMLElement).style.fontWeight = '600';
    (el as HTMLElement).style.color = '#555';
    (el as HTMLElement).style.marginTop = '24px';
    (el as HTMLElement).style.marginBottom = '12px';
  });

  // Paragraphs
  const pElements = container.querySelectorAll('p');
  pElements.forEach(el => {
    (el as HTMLElement).style.marginBottom = '12px';
    (el as HTMLElement).style.lineHeight = '1.8';
  });

  // Lists
  const ulElements = container.querySelectorAll('ul');
  ulElements.forEach(el => {
    (el as HTMLElement).style.marginTop = '12px';
    (el as HTMLElement).style.marginBottom = '12px';
    (el as HTMLElement).style.paddingLeft = '24px';
  });

  const liElements = container.querySelectorAll('li');
  liElements.forEach(el => {
    (el as HTMLElement).style.marginBottom = '8px';
  });

  // Code
  const codeElements = container.querySelectorAll('code');
  codeElements.forEach(el => {
    (el as HTMLElement).style.backgroundColor = '#f0f0f0';
    (el as HTMLElement).style.padding = '2px 6px';
    (el as HTMLElement).style.borderRadius = '4px';
    (el as HTMLElement).style.fontFamily = 'Courier New, monospace';
    (el as HTMLElement).style.fontSize = '13px';
    (el as HTMLElement).style.color = '#e83e8c';
  });

  // Strong
  const strongElements = container.querySelectorAll('strong');
  strongElements.forEach(el => {
    (el as HTMLElement).style.fontWeight = 'bold';
    (el as HTMLElement).style.color = '#2c3e50';
  });

  // Links
  const linkElements = container.querySelectorAll('a');
  linkElements.forEach(el => {
    (el as HTMLElement).style.color = '#667eea';
    (el as HTMLElement).style.textDecoration = 'underline';
  });
};
