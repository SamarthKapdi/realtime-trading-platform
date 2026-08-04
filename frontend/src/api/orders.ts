/**
 * Order API functions.
 */
import apiClient from "./client";
import type {
  OrderCreate,
  OrderBook,
  CreateOrderResponse,
  Order,
} from "../types";

export const ordersApi = {
  create: async (order: OrderCreate): Promise<CreateOrderResponse> => {
    const { data } = await apiClient.post<CreateOrderResponse>("/orders", order);
    return data;
  },

  getOrderBook: async (): Promise<OrderBook> => {
    const { data } = await apiClient.get<OrderBook>("/orderbook");
    return data;
  },

  cancel: async (orderId: number): Promise<Order> => {
    const { data } = await apiClient.delete<Order>(`/orders/${orderId}`);
    return data;
  },

  getById: async (orderId: number): Promise<Order> => {
    const { data } = await apiClient.get<Order>(`/orders/${orderId}`);
    return data;
  },
};
