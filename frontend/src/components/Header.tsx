export default function Header() {
  return (
    <header className="h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6">
      <div className="text-gray-400 font-medium">Network: Ethereum Mainnet</div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-sm text-gray-300">API Connected</span>
        </div>
      </div>
    </header>
  )
}
