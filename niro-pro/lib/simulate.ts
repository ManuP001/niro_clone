export async function simulateDelay(ms = 1200): Promise<void> {
  await new Promise(r => setTimeout(r, ms));
}

export async function simulatePayment(
  onStep: (step: string) => void
): Promise<void> {
  onStep("Initiating payment...");
  await simulateDelay(800);
  onStep("Processing ₹99 platform fee...");
  await simulateDelay(1200);
  onStep("Payment confirmed ✓");
  await simulateDelay(500);
}

export async function simulateTextCleanup(text: string): Promise<{
  corrected: string;
  changes_made: boolean;
  changes: string[];
}> {
  await simulateDelay(1000);
  const corrected = text.replace(/\s{2,}/g, " ").trim();
  const changed = corrected !== text.trim();
  return {
    corrected: changed ? corrected : text,
    changes_made: changed,
    changes: changed ? ["Fixed extra whitespace"] : [],
  };
}

export async function simulateOfferSend(details: {
  clientName: string;
  packageName: string;
  price: number;
  expiryHours: number;
}): Promise<{ whatsapp_template: string }> {
  await simulateDelay(1000);
  return {
    whatsapp_template:
      `${details.clientName}, it was wonderful speaking with you today 🙏\n\n` +
      `I've put together a special offer based on our conversation:\n\n` +
      `✨ ${details.packageName}\n` +
      `₹${details.price.toLocaleString("en-IN")}\n\n` +
      `This offer is valid for ${details.expiryHours} hours.\n` +
      `To book: [Payment link will appear here]\n\n` +
      `Looking forward to continuing this journey with you 🌙`,
  };
}
