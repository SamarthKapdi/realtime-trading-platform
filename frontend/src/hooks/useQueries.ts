/**
 * React Query hooks for data fetching.
 */
import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryResult,
  type UseMutationResult,
} from "@tanstack/react-query";
import { ordersApi } from "../api/orders";
import { tradesApi } from "../api/trades";
import type {
  OrderBook,
  Trade,
  Stats,
  OrderCreate,
  CreateOrderResponse,
  Order,
} from "../types";

/* ── Query Keys ───────────────────────────── */

export const queryKeys = {
  orderBook: ["orderbook"] as const,
  trades: ["trades"] as const,
  stats: ["stats"] as const,
};

/* ── Queries ──────────────────────────────── */

export function useOrderBook(): UseQueryResult<OrderBook> {
  return useQuery({
    queryKey: queryKeys.orderBook,
    queryFn: ordersApi.getOrderBook,
    refetchInterval: 5000,
  });
}

export function useTrades(): UseQueryResult<Trade[]> {
  return useQuery({
    queryKey: queryKeys.trades,
    queryFn: () => tradesApi.getAll(),
    refetchInterval: 5000,
  });
}

export function useStats(): UseQueryResult<Stats> {
  return useQuery({
    queryKey: queryKeys.stats,
    queryFn: tradesApi.getStats,
    refetchInterval: 5000,
  });
}

/* ── Mutations ────────────────────────────── */

export function useCreateOrder(): UseMutationResult<
  CreateOrderResponse,
  Error,
  OrderCreate
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ordersApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.orderBook });
      queryClient.invalidateQueries({ queryKey: queryKeys.trades });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats });
    },
  });
}

export function useCancelOrder(): UseMutationResult<Order, Error, number> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ordersApi.cancel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.orderBook });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats });
    },
  });
}

/**
 * Invalidate all data queries. Called on WebSocket updates.
 */
export function useInvalidateAll() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.orderBook });
    queryClient.invalidateQueries({ queryKey: queryKeys.trades });
    queryClient.invalidateQueries({ queryKey: queryKeys.stats });
  };
}
