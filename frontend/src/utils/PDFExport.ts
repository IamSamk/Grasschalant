/**
 * PDFExport — Client-side storybook PDF generation
 * 
 * Uses jspdf to create an A4 landscape storybook PDF with:
 * - Cover page with expedition stats
 * - Photo spreads (left: outdoor photo, right: meme match)
 * - Back cover with journey summary
 * 
 * Zero server overhead — runs entirely in the browser.
 */

import jsPDF from 'jspdf';

interface Page {
  page_index: number;
  real_image_url: string;
  meme_image_url: string;
  meme_name: string;
  literal_description: string;
  meme_analogy_concept: string;
  explanation: string;
  match_confidence: number;
  step_count: number;
  timestamp: string;
}

interface Outing {
  id: string;
  goal_steps: number;
  total_photos_target: number;
  current_steps: number;
  pages: Page[];
  started_at: string;
  status: string;
}

/**
 * Load an image from URL and convert to base64 data URL.
 */
async function loadImageAsBase64(url: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Failed to get canvas context'));
        return;
      }
      ctx.drawImage(img, 0, 0);
      resolve(canvas.toDataURL('image/jpeg', 0.85));
    };
    img.onerror = () => reject(new Error(`Failed to load image: ${url}`));
    img.src = url;
  });
}

/**
 * Export the outing storybook as an A4 landscape PDF.
 */
export async function exportToPDF(outing: Outing): Promise<void> {
  const pdf = new jsPDF({
    orientation: 'landscape',
    unit: 'mm',
    format: 'a4',
  });

  const pageWidth = 297; // A4 landscape width in mm
  const pageHeight = 210; // A4 landscape height in mm
  const margin = 15;
  const halfWidth = pageWidth / 2;

  // ── Cover Page ──────────────────────────────────────────────────────
  // Background
  pdf.setFillColor(15, 23, 42); // slate-900
  pdf.rect(0, 0, pageWidth, pageHeight, 'F');

  // Title
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(32);
  pdf.text('My Touch Grass Expedition', pageWidth / 2, 60, { align: 'center' });

  // Decorative line
  pdf.setDrawColor(74, 222, 128); // green-400
  pdf.setLineWidth(1);
  pdf.line(pageWidth / 2 - 40, 70, pageWidth / 2 + 40, 70);

  // Stats
  pdf.setFontSize(16);
  pdf.setTextColor(148, 163, 184); // slate-400
  const startDate = new Date(outing.started_at);
  const dateStr = startDate.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  pdf.text(`${outing.current_steps.toLocaleString()} Steps`, pageWidth / 2, 90, { align: 'center' });
  pdf.text(`${outing.pages.length} Discoveries`, pageWidth / 2, 102, { align: 'center' });
  pdf.text(dateStr, pageWidth / 2, 114, { align: 'center' });

  // Subtitle
  pdf.setFontSize(12);
  pdf.setTextColor(74, 222, 128);
  pdf.text('A Grasschalant Adventure 🌿', pageWidth / 2, 140, { align: 'center' });

  // ── Content Spreads ─────────────────────────────────────────────────
  for (let i = 0; i < outing.pages.length; i++) {
    const page = outing.pages[i];
    pdf.addPage();

    // Page background
    pdf.setFillColor(241, 245, 249); // slate-100
    pdf.rect(0, 0, pageWidth, pageHeight, 'F');

    // Center divider
    pdf.setDrawColor(203, 213, 225); // slate-300
    pdf.setLineWidth(0.5);
    pdf.line(halfWidth, margin, halfWidth, pageHeight - margin);

    // ── Left page: Outdoor Photo ──
    try {
      const photoData = await loadImageAsBase64(page.real_image_url);
      const imgWidth = halfWidth - margin * 2 - 5;
      const imgHeight = imgWidth * 0.75;
      pdf.addImage(photoData, 'JPEG', margin + 5, margin + 5, imgWidth, imgHeight);
    } catch {
      // Placeholder if image fails to load
      pdf.setFillColor(226, 232, 240);
      pdf.rect(margin + 5, margin + 5, halfWidth - margin * 2 - 5, 90, 'F');
      pdf.setTextColor(100, 116, 139);
      pdf.setFontSize(10);
      pdf.text('Photo unavailable', margin + halfWidth / 2, margin + 50, { align: 'center' });
    }

    // Step badge
    pdf.setFillColor(74, 222, 128);
    pdf.roundedRect(margin + 5, margin + 100, 60, 8, 2, 2, 'F');
    pdf.setTextColor(15, 23, 42);
    pdf.setFontSize(8);
    pdf.text(`Discovered at Step ${page.step_count.toLocaleString()}`, margin + 35, margin + 105.5, { align: 'center' });

    // Literal description
    pdf.setTextColor(30, 41, 59); // slate-800
    pdf.setFontSize(10);
    const descLines = pdf.splitTextToSize(page.literal_description, halfWidth - margin * 2 - 10);
    pdf.text(descLines, margin + 5, margin + 118);

    // Page number
    pdf.setTextColor(148, 163, 184);
    pdf.setFontSize(9);
    pdf.text(`${i * 2 + 1}`, halfWidth / 2, pageHeight - margin, { align: 'center' });

    // ── Right page: Meme Match ──
    try {
      const memeData = await loadImageAsBase64(page.meme_image_url);
      const imgWidth = halfWidth - margin * 2 - 5;
      const imgHeight = imgWidth * 0.75;
      pdf.addImage(memeData, 'JPEG', halfWidth + margin, margin + 5, imgWidth, imgHeight);
    } catch {
      pdf.setFillColor(226, 232, 240);
      pdf.rect(halfWidth + margin, margin + 5, halfWidth - margin * 2 - 5, 90, 'F');
      pdf.setTextColor(100, 116, 139);
      pdf.setFontSize(10);
      pdf.text('Meme unavailable', halfWidth + halfWidth / 2, margin + 50, { align: 'center' });
    }

    // Match badge
    pdf.setFillColor(167, 139, 250); // violet-400
    pdf.roundedRect(halfWidth + margin, margin + 100, 45, 8, 2, 2, 'F');
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(8);
    pdf.text(`${Math.round(page.match_confidence * 100)}% Match`, halfWidth + margin + 22.5, margin + 105.5, { align: 'center' });

    // Meme name
    pdf.setTextColor(30, 41, 59);
    pdf.setFontSize(13);
    pdf.text(page.meme_name, halfWidth + margin, margin + 118);

    // Explanation
    pdf.setFontSize(9);
    pdf.setTextColor(71, 85, 105); // slate-500
    const explLines = pdf.splitTextToSize(page.explanation, halfWidth - margin * 2 - 5);
    pdf.text(explLines, halfWidth + margin, margin + 128);

    // Page number
    pdf.setTextColor(148, 163, 184);
    pdf.setFontSize(9);
    pdf.text(`${i * 2 + 2}`, halfWidth + halfWidth / 2, pageHeight - margin, { align: 'center' });
  }

  // ── Back Cover ──────────────────────────────────────────────────────
  pdf.addPage();
  pdf.setFillColor(15, 23, 42);
  pdf.rect(0, 0, pageWidth, pageHeight, 'F');

  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(28);
  pdf.text('The End', pageWidth / 2, 80, { align: 'center' });

  pdf.setFontSize(12);
  pdf.setTextColor(148, 163, 184);
  pdf.text(
    `You walked ${outing.current_steps.toLocaleString()} steps and discovered ${outing.pages.length} hidden memes in the wild.`,
    pageWidth / 2,
    100,
    { align: 'center' }
  );

  pdf.setTextColor(74, 222, 128);
  pdf.setFontSize(10);
  pdf.text('Made with 🌿 by Grasschalant', pageWidth / 2, 130, { align: 'center' });

  // Save
  const fileName = `grasschalant_${startDate.toISOString().slice(0, 10)}.pdf`;
  pdf.save(fileName);
}
