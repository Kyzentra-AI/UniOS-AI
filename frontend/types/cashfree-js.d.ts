declare module '@cashfreepayments/cashfree-js' {
  export type CashfreeMode = 'sandbox' | 'production';

  export interface CashfreeCheckoutOptions {
    paymentSessionId: string;
    redirectTarget?: '_self' | '_blank' | '_top' | '_modal';
  }

  export interface CashfreeInstance {
    checkout(
      options: CashfreeCheckoutOptions
    ): Promise<unknown>;
  }

  export function load(options: {
    mode: CashfreeMode;
  }): Promise<CashfreeInstance | null>;
}