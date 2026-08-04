/**
 * Order entry form component.
 */
import { useState, type FormEvent } from "react";
import { useCreateOrder } from "../hooks/useQueries";

export default function OrderForm() {
  const [side, setSide] = useState<"BUY" | "SELL">("BUY");
  const [orderType, setOrderType] = useState<"LIMIT" | "MARKET">("LIMIT");
  const [price, setPrice] = useState("");
  const [quantity, setQuantity] = useState("");

  const createOrder = useCreateOrder();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    const qty = parseFloat(quantity);
    if (isNaN(qty) || qty <= 0) return;

    if (orderType === "LIMIT") {
      const prc = parseFloat(price);
      if (isNaN(prc) || prc <= 0) return;
      createOrder.mutate({ side, price: prc, quantity: qty, order_type: "LIMIT" });
    } else {
      createOrder.mutate({ side, quantity: qty, order_type: "MARKET" });
    }

    setPrice("");
    setQuantity("");
  };

  const isBuy = side === "BUY";

  return (
    <div className="bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 shadow-2xl">
      <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" />
        Place Order
      </h2>

      {/* Side Toggle */}
      <div className="grid grid-cols-2 gap-2 mb-5">
        <button
          type="button"
          onClick={() => setSide("BUY")}
          className={`py-2.5 rounded-xl font-semibold text-sm transition-all duration-200 ${
            isBuy
              ? "bg-emerald-500/20 text-emerald-400 border-2 border-emerald-500/50 shadow-lg shadow-emerald-500/10"
              : "bg-gray-800/50 text-gray-400 border-2 border-transparent hover:border-gray-600"
          }`}
        >
          BUY
        </button>
        <button
          type="button"
          onClick={() => setSide("SELL")}
          className={`py-2.5 rounded-xl font-semibold text-sm transition-all duration-200 ${
            !isBuy
              ? "bg-rose-500/20 text-rose-400 border-2 border-rose-500/50 shadow-lg shadow-rose-500/10"
              : "bg-gray-800/50 text-gray-400 border-2 border-transparent hover:border-gray-600"
          }`}
        >
          SELL
        </button>
      </div>

      {/* Order Type Toggle */}
      <div className="grid grid-cols-2 gap-2 mb-5">
        <button
          type="button"
          onClick={() => setOrderType("LIMIT")}
          className={`py-2 rounded-lg text-xs font-medium transition-all ${
            orderType === "LIMIT"
              ? "bg-violet-500/20 text-violet-400 border border-violet-500/40"
              : "bg-gray-800/50 text-gray-500 border border-transparent hover:border-gray-600"
          }`}
        >
          LIMIT
        </button>
        <button
          type="button"
          onClick={() => setOrderType("MARKET")}
          className={`py-2 rounded-lg text-xs font-medium transition-all ${
            orderType === "MARKET"
              ? "bg-violet-500/20 text-violet-400 border border-violet-500/40"
              : "bg-gray-800/50 text-gray-500 border border-transparent hover:border-gray-600"
          }`}
        >
          MARKET
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {orderType === "LIMIT" && (
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">
              Price (USD)
            </label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              placeholder="0.00"
              required
              className="w-full bg-gray-800/60 border border-gray-700/50 rounded-xl px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-violet-500/40 focus:border-violet-500/40 transition-all"
            />
          </div>
        )}

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">
            Quantity (BYTE)
          </label>
          <input
            type="number"
            step="0.00000001"
            min="0.00000001"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="0.00"
            required
            className="w-full bg-gray-800/60 border border-gray-700/50 rounded-xl px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-violet-500/40 focus:border-violet-500/40 transition-all"
          />
        </div>

        {/* Summary */}
        {price && quantity && orderType === "LIMIT" && (
          <div className="bg-gray-800/40 rounded-lg p-3 text-xs text-gray-400">
            <div className="flex justify-between">
              <span>Total</span>
              <span className="text-white font-medium">
                ${(parseFloat(price) * parseFloat(quantity)).toFixed(2)}
              </span>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={createOrder.isPending}
          className={`w-full py-3 rounded-xl font-semibold text-sm transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
            isBuy
              ? "bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white shadow-lg shadow-emerald-500/20"
              : "bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 text-white shadow-lg shadow-rose-500/20"
          }`}
        >
          {createOrder.isPending
            ? "Placing..."
            : `${side} BYTE`}
        </button>

        {createOrder.isError && (
          <p className="text-rose-400 text-xs mt-2 bg-rose-500/10 rounded-lg p-2">
            {createOrder.error.message}
          </p>
        )}

        {createOrder.isSuccess && (
          <p className="text-emerald-400 text-xs mt-2 bg-emerald-500/10 rounded-lg p-2">
            {createOrder.data.message}
          </p>
        )}
      </form>
    </div>
  );
}
