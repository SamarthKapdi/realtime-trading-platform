/**
 * Order book display component.
 */
import { useOrderBook } from "../hooks/useQueries";

export default function OrderBook() {
  const { data, isLoading, isError } = useOrderBook();

  if (isLoading) {
    return (
      <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 shadow-2xl">
        <h2 className="text-lg font-semibold text-white mb-4">Order Book</h2>
        <div className="animate-pulse space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-8 bg-gray-800/60 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 shadow-2xl">
        <h2 className="text-lg font-semibold text-white mb-4">Order Book</h2>
        <p className="text-rose-400 text-sm">Failed to load order book</p>
      </div>
    );
  }

  const buyOrders = data?.buy_orders ?? [];
  const sellOrders = data?.sell_orders ?? [];

  // Calculate max quantity for bar width
  const allQuantities = [
    ...buyOrders.map((o) => Number(o.quantity)),
    ...sellOrders.map((o) => Number(o.quantity)),
  ];
  const maxQty = Math.max(...allQuantities, 1);

  return (
    <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 shadow-2xl">
      <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
        Order Book
        <span className="text-xs text-gray-500 font-normal ml-auto">BYTE/USD</span>
      </h2>

      {/* Header */}
      <div className="grid grid-cols-3 text-xs text-gray-500 font-medium mb-2 px-2">
        <span>Price</span>
        <span className="text-center">Quantity</span>
        <span className="text-right">Orders</span>
      </div>

      {/* Sell Orders (reversed so lowest is at bottom, closest to spread) */}
      <div className="space-y-0.5 mb-1">
        {sellOrders.length === 0 ? (
          <div className="text-center text-gray-600 text-xs py-3">No sell orders</div>
        ) : (
          [...sellOrders].reverse().slice(0, 10).map((order, idx) => {
            const pct = (Number(order.quantity) / maxQty) * 100;
            return (
              <div
                key={`sell-${idx}`}
                className="relative grid grid-cols-3 text-sm py-1.5 px-2 rounded-lg hover:bg-rose-500/5 transition-colors"
              >
                <div
                  className="absolute inset-0 bg-rose-500/8 rounded-lg"
                  style={{ width: `${pct}%`, right: 0, left: "auto" }}
                />
                <span className="relative text-rose-400 font-mono text-xs">
                  ${Number(order.price).toFixed(2)}
                </span>
                <span className="relative text-gray-300 text-center font-mono text-xs">
                  {Number(order.quantity).toFixed(4)}
                </span>
                <span className="relative text-gray-500 text-right text-xs">
                  {order.order_count}
                </span>
              </div>
            );
          })
        )}
      </div>

      {/* Spread Indicator */}
      <div className="border-t border-b border-gray-700/50 py-2 my-1 text-center">
        {buyOrders.length > 0 && sellOrders.length > 0 ? (
          <span className="text-xs text-gray-400">
            Spread:{" "}
            <span className="text-white font-medium">
              ${(Number(sellOrders[0].price) - Number(buyOrders[0].price)).toFixed(2)}
            </span>
          </span>
        ) : (
          <span className="text-xs text-gray-600">—</span>
        )}
      </div>

      {/* Buy Orders */}
      <div className="space-y-0.5 mt-1">
        {buyOrders.length === 0 ? (
          <div className="text-center text-gray-600 text-xs py-3">No buy orders</div>
        ) : (
          buyOrders.slice(0, 10).map((order, idx) => {
            const pct = (Number(order.quantity) / maxQty) * 100;
            return (
              <div
                key={`buy-${idx}`}
                className="relative grid grid-cols-3 text-sm py-1.5 px-2 rounded-lg hover:bg-emerald-500/5 transition-colors"
              >
                <div
                  className="absolute inset-0 bg-emerald-500/8 rounded-lg"
                  style={{ width: `${pct}%` }}
                />
                <span className="relative text-emerald-400 font-mono text-xs">
                  ${Number(order.price).toFixed(2)}
                </span>
                <span className="relative text-gray-300 text-center font-mono text-xs">
                  {Number(order.quantity).toFixed(4)}
                </span>
                <span className="relative text-gray-500 text-right text-xs">
                  {order.order_count}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
