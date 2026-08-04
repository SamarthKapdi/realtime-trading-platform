/**
 * Trades API functions.
 */
import apiClient from "./client";
import type { Trade, Stats } from "../types";

export const tradesApi = {
  getAll: async (limit = 100, offset = 0): Promise<Trade[]> => {
    const { data } = await apiClient.get<Trade[]>("/trades", {
      params: { limit, offset },
    });
    return data;
  },

  getStats: async (): Promise<Stats> => {
    const { data } = await apiClient.get<Stats>("/stats");
    return data;
  },
};
