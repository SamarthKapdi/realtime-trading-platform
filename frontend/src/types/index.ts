/* ── API Types ──────────────────────────────── */

export interface OrderCreate {
  side: "BUY" | "SELL";
  price?: number;
  quantity: number;
  order_type?: "LIMIT" | "MARKET";
}

export interface Order {
  id: number;
  side: "BUY" | "SELL";
  order_type: "LIMIT" | "MARKET";
  price: number | null;
  quantity: number;
  remaining_quantity: number;
  status: "OPEN" | "PARTIALLY_FILLED" | "FILLED" | "CANCELLED";
  created_at: string;
}

export interface OrderBookEntry {
  price: number;
  quantity: number;
  order_count: number;
}

export interface OrderBook {
  buy_orders: OrderBookEntry[];
  sell_orders: OrderBookEntry[];
}

export interface Trade {
  id: number;
  buy_order_id: number;
  sell_order_id: number;
  price: number;
  quantity: number;
  executed_at: string;
}

export interface Stats {
  total_buy_orders: number;
  total_sell_orders: number;
  total_trades: number;
  open_buy_orders: number;
  open_sell_orders: number;
  last_trade_price: number | null;
  total_volume: number;
}

export interface CreateOrderResponse {
  order: Order;
  trades: Trade[];
  message: string;
}

export interface WebSocketMessage {
  type: "orderbook_update" | "trade" | "stats_update" | "pong";
  data?: Trade;
}
