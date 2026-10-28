
import { load } from '@cashfreepayments/cashfree-js';

type CashfreeEnvironment = 'sandbox' | 'production';

function getCashfreeEnvironment(
  environment: string
): CashfreeEnvironment {
  const normalized = environment.toLowerCase();

  if (normalized === 'sandbox') {
    return 'sandbox';
  }

  if (normalized === 'production') {
    return 'production';
  }

  throw new Error(
    `Unsupported Cashfree environment: ${environment}`
  );
}

export async function openCashfreeCheckout(
  paymentSessionId: string,
  environment: string
): Promise<void> {
  if (!paymentSessionId) {
    throw new Error('Missing Cashfree payment session.');
  }

  const cashfree = await load({
    mode: getCashfreeEnvironment(environment),
  });

  if (!cashfree) {
    throw new Error('Unable to initialize Cashfree checkout.');
  }

  await cashfree.checkout({
    paymentSessionId,
    redirectTarget: '_modal',
  });
}
