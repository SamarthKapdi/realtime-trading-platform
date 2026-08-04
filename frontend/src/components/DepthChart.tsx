/**
 * Depth chart visualization component.
 */
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useOrderBook } from "../hooks/useQueries";

interface DepthPoint {
  price: number;
  buyDepth: number | null;
  sellDepth: number | null;
}

export default function DepthChart() {
  const { data, isLoading } = useOrderBook();

  if (isLoading || !data) {
    return (
      <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 shadow-2xl">
        <h2 className="text-lg font-semibold text-white mb-4">Depth Chart</h2>
        <div className="h-48 animate-pulse bg-gray-800/40 rounded-xl" />
      </div>
    );
  }

  const buyOrders = data.buy_orders ?? [];
  const sellOrders = data.sell_orders ?? [];

  if (buyOrders.length === 0 && sellOrders.length === 0) {
    return (
      <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 shadow-2xl">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
          Depth Chart
        </h2>
        <div className="h-48 flex items-center justify-center text-gray-600 text-sm">
          No orders to display
        </div>
      </div>
    );
  }

  // Build cumulative depth data
  const depthData: DepthPoint[] = [];

  // Buy side: sorted highest to lowest (already from API), we need cumulative from highest down
  let cumBuy = 0;
  const buyPoints: DepthPoint[] = [];
  for (const order of buyOrders) {
    cumBuy += Number(order.quantity);
    buyPoints.push({
      price: Number(order.price),
      buyDepth: cumBuy,
      sellDepth: null,
    });
  }
  // Reverse so it goes low to high price
  buyPoints.reverse();

  // Sell side: sorted lowest to highest, cumulative
  let cumSell = 0;
  const sellPoints: DepthPoint[] = [];
  for (const order of sellOrders) {
    cumSell += Number(order.quantity);
    sellPoints.push({
      price: Number(order.price),
      buyDepth: null,
      sellDepth: cumSell,
    });
  }

  depthData.push(...buyPoints, ...sellPoints);

  return (
    <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 shadow-2xl">
      <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
        Depth Chart
        <span className="text-xs text-gray-500 font-normal ml-auto">BYTE/USD</span>
      </h2>

      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={depthData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
            <XAxis
              dataKey="price"
              type="number"
              domain={["dataMin", "dataMax"]}
              tick={{ fill: "#6b7280", fontSize: 10 }}
              axisLine={{ stroke: "#374151" }}
              tickFormatter={(v: number) => `$${v}`}
            />
            <YAxis
              tick={{ fill: "#6b7280", fontSize: 10 }}
              axisLine={{ stroke: "#374151" }}
              width={40}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1f2937",
                border: "1px solid #374151",
                borderRadius: "8px",
                fontSize: "12px",
              }}
              labelFormatter={(v) => `$${Number(v).toFixed(2)}`}
            />
            <Area
              type="stepAfter"
              dataKey="buyDepth"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.15}
              strokeWidth={2}
              name="Buy Depth"
              connectNulls={false}
            />
            <Area
              type="stepAfter"
              dataKey="sellDepth"
              stroke="#f43f5e"
              fill="#f43f5e"
              fillOpacity={0.15}
              strokeWidth={2}
              name="Sell Depth"
              connectNulls={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
