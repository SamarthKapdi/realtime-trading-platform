/**
 * Trade history component.
 */
import { useTrades } from "../hooks/useQueries";

export default function TradeHistory() {
  const { data: trades, isLoading, isError } = useTrades();

  if (isLoading) {
    return (
      <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 shadow-2xl">
        <h2 className="text-lg font-semibold text-white mb-4">Recent Trades</h2>
        <div className="animate-pulse space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-6 bg-gray-800/60 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 shadow-2xl">
        <h2 className="text-lg font-semibold text-white mb-4">Recent Trades</h2>
        <p className="text-rose-400 text-sm">Failed to load trades</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 shadow-2xl">
      <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
        Recent Trades
      </h2>

      {/* Header */}
      <div className="grid grid-cols-3 text-xs text-gray-500 font-medium mb-2 px-1">
        <span>Price</span>
        <span className="text-center">Quantity</span>
        <span className="text-right">Time</span>
      </div>

      <div className="space-y-0.5 max-h-80 overflow-y-auto scrollbar-thin">
        {!trades || trades.length === 0 ? (
          <div className="text-center text-gray-600 text-xs py-8">
            No trades yet
          </div>
        ) : (
          trades.slice(0, 50).map((trade) => (
            <div
              key={trade.id}
              className="grid grid-cols-3 text-xs py-1.5 px-1 rounded-lg hover:bg-gray-800/40 transition-colors"
            >
              <span className="text-white font-mono">
                ${Number(trade.price).toFixed(2)}
              </span>
              <span className="text-gray-300 text-center font-mono">
                {Number(trade.quantity).toFixed(4)}
              </span>
              <span className="text-gray-500 text-right">
                {new Date(trade.executed_at).toLocaleTimeString()}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
