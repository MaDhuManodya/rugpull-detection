import Link from 'next/link'
import { Activity, ShieldAlert, LineChart, Search, Settings } from 'lucide-react'

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 h-screen border-r border-gray-800 flex flex-col hidden md:flex">
      <div className="p-6">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <ShieldAlert className="text-red-500" />
          RugPull AI
        </h1>
      </div>
      <nav className="flex-1 px-4 space-y-2">
        <Link href="/" className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors">
          <Activity size={20} /> Dashboard
        </Link>
        <Link href="/predictions" className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors">
          <Search size={20} /> Live Predictions
        </Link>
        <Link href="/metrics" className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors">
          <LineChart size={20} /> Model Metrics
        </Link>
      </nav>
      <div className="p-4 border-t border-gray-800">
        <Link href="/settings" className="flex items-center gap-3 px-4 py-3 text-gray-400 hover:text-white transition-colors">
          <Settings size={20} /> Settings
        </Link>
      </div>
    </aside>
  )
}
