/**
 * Main dashboard page - assembles all components.
 */
import { useQueryClient } from "@tanstack/react-query";
import { useWebSocket } from "../hooks/useWebSocket";
import { queryKeys } from "../hooks/useQueries";
import OrderForm from "../components/OrderForm";
import OrderBook from "../components/OrderBook";
import TradeHistory from "../components/TradeHistory";
import StatsCards from "../components/StatsCards";
import DepthChart from "../components/DepthChart";
import ConnectionStatus from "../components/ConnectionStatus";

export default function Dashboard() {
  const queryClient = useQueryClient();

  const { isConnected } = useWebSocket((message) => {
    // Invalidate relevant queries on WebSocket updates
    switch (message.type) {
      case "orderbook_update":
        queryClient.invalidateQueries({ queryKey: queryKeys.orderBook });
        break;
      case "trade":
        queryClient.invalidateQueries({ queryKey: queryKeys.trades });
        queryClient.invalidateQueries({ queryKey: queryKeys.orderBook });
        break;
      case "stats_update":
        queryClient.invalidateQueries({ queryKey: queryKeys.stats });
        break;
    }
  });

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Background gradient effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-violet-600 to-cyan-500 rounded-xl flex items-center justify-center font-bold text-lg shadow-lg shadow-violet-500/20">
              B
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                ByteVox Exchange
              </h1>
              <p className="text-xs text-gray-500">BYTE/USD Trading</p>
            </div>
          </div>
          <ConnectionStatus isConnected={isConnected} />
        </header>

        {/* Stats Cards */}
        <section className="mb-6">
          <StatsCards />
        </section>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Order Form */}
          <div className="lg:col-span-3">
            <OrderForm />
          </div>

          {/* Order Book */}
          <div className="lg:col-span-4">
            <OrderBook />
          </div>

          {/* Trade History */}
          <div className="lg:col-span-5">
            <TradeHistory />
          </div>
        </div>

        {/* Depth Chart */}
        <section className="mt-6">
          <DepthChart />
        </section>

        {/* Footer */}
        <footer className="mt-8 text-center text-xs text-gray-600">
          <p>ByteVox Exchange Simulator • Built with FastAPI + React + TypeScript</p>
        </footer>
      </div>
    </div>
  );
}
