/**
 * Statistics cards component.
 */
import { useStats } from "../hooks/useQueries";

interface StatCardProps {
  label: string;
  value: string | number;
  color: string;
  icon: string;
}

function StatCard({ label, value, color, icon }: StatCardProps) {
  return (
    <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-5 shadow-2xl hover:border-gray-600/50 transition-all duration-300 group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-400 font-medium mb-1">{label}</p>
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
        </div>
        <span className="text-2xl opacity-60 group-hover:opacity-100 transition-opacity">
          {icon}
        </span>
      </div>
    </div>
  );
}

export default function StatsCards() {
  const { data: stats, isLoading } = useStats();

  if (isLoading || !stats) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="bg-gray-900/80 rounded-2xl border border-gray-700/50 p-5 animate-pulse"
          >
            <div className="h-4 bg-gray-800 rounded w-20 mb-3" />
            <div className="h-8 bg-gray-800 rounded w-16" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        label="Buy Orders"
        value={stats.total_buy_orders}
        color="text-emerald-400"
        icon="📈"
      />
      <StatCard
        label="Sell Orders"
        value={stats.total_sell_orders}
        color="text-rose-400"
        icon="📉"
      />
      <StatCard
        label="Trades Executed"
        value={stats.total_trades}
        color="text-violet-400"
        icon="⚡"
      />
      <StatCard
        label="Last Price"
        value={stats.last_trade_price ? `$${stats.last_trade_price.toFixed(2)}` : "—"}
        color="text-amber-400"
        icon="💰"
      />
    </div>
  );
}
