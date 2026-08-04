/**
 * WebSocket connection status indicator.
 */

interface ConnectionStatusProps {
  isConnected: boolean;
}

export default function ConnectionStatus({ isConnected }: ConnectionStatusProps) {
  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <div
          className={`w-2.5 h-2.5 rounded-full transition-colors duration-300 ${
            isConnected ? "bg-emerald-400" : "bg-rose-400"
          }`}
        />
        {isConnected && (
          <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping opacity-50" />
        )}
      </div>
      <span className={`text-xs font-medium ${isConnected ? "text-emerald-400" : "text-rose-400"}`}>
        {isConnected ? "Live" : "Disconnected"}
      </span>
    </div>
  );
}
