
'use client';

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

import {
  activateBillingTrial,
  createBillingCheckout,
  getBillingHistory,
  getBillingPlans,
  getMyEntitlement,
  getMyUsage,
  renewBillingSubscription,
  verifyBillingPayment,
} from '@/services/billingServices';

import type { CheckoutRequest } from '@/types/billing';

export function useBilling() {
  const queryClient = useQueryClient();

  const plansQuery = useQuery({
    queryKey: ['billing', 'plans'],
    queryFn: getBillingPlans,
    staleTime: 5 * 60 * 1000,
  });

  const entitlementQuery = useQuery({
    queryKey: ['billing', 'entitlement'],
    queryFn: getMyEntitlement,
  });

  const usageQuery = useQuery({
    queryKey: ['billing', 'usage'],
    queryFn: getMyUsage,
  });

  const historyQuery = useQuery({
    queryKey: ['billing', 'history'],
    queryFn: getBillingHistory,
  });

  const refreshBilling = async () => {
    await Promise.all([
      queryClient.invalidateQueries({
        queryKey: ['billing', 'entitlement'],
      }),
      queryClient.invalidateQueries({
        queryKey: ['billing', 'usage'],
      }),
      queryClient.invalidateQueries({
        queryKey: ['billing', 'history'],
      }),
    ]);
  };

  const trialMutation = useMutation({
    mutationFn: activateBillingTrial,
    onSuccess: async () => {
      await refreshBilling();
    },
  });

  const checkoutMutation = useMutation({
    mutationFn: (payload: CheckoutRequest) =>
      createBillingCheckout(payload),
  });

  const renewMutation = useMutation({
    mutationFn: (payload: CheckoutRequest) =>
      renewBillingSubscription(payload),
  });

  const paymentMutation = useMutation({
    mutationFn: verifyBillingPayment,
    onSuccess: async (payment) => {
      if (payment.status === 'SUCCESS') {
        await refreshBilling();
      }
    },
  });

  return {
    plans: plansQuery.data?.plans ?? [],
    entitlement: entitlementQuery.data,
    usage: usageQuery.data,
    history: historyQuery.data,

    isLoading:
      plansQuery.isLoading ||
      entitlementQuery.isLoading ||
      usageQuery.isLoading,

    plansError: plansQuery.error,
    entitlementError: entitlementQuery.error,
    usageError: usageQuery.error,
    historyError: historyQuery.error,

    refetchPlans: plansQuery.refetch,
    refetchEntitlement: entitlementQuery.refetch,
    refetchUsage: usageQuery.refetch,
    refetchHistory: historyQuery.refetch,

    activateTrial: trialMutation.mutateAsync,
    isActivatingTrial: trialMutation.isPending,
    trialError: trialMutation.error,

    createCheckout: checkoutMutation.mutateAsync,
    isCreatingCheckout: checkoutMutation.isPending,
    checkoutError: checkoutMutation.error,

    renewSubscription: renewMutation.mutateAsync,
    isRenewing: renewMutation.isPending,
    renewError: renewMutation.error,

    verifyPayment: paymentMutation.mutateAsync,
    isVerifyingPayment: paymentMutation.isPending,
    paymentError: paymentMutation.error,

    refreshBilling,
  };
}
