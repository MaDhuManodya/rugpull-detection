'use client'
import { Card, CardContent, CardHeader } from "@/components/ui/Card"
import { ShieldAlert, Activity, Users, Database } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard Overview</h1>
        <p className="text-gray-400 mt-2">Real-time monitoring of live smart contracts and predictions.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="Blocks Processed" value="14,204" icon={<Database size={24} className="text-blue-500"/>} />
        <StatCard title="Tokens Analyzed" value="342" icon={<Activity size={24} className="text-green-500"/>} />
        <StatCard title="High Risk Detected" value="12" icon={<ShieldAlert size={24} className="text-red-500"/>} />
        <StatCard title="Wallets Mapped" value="45.2K" icon={<Users size={24} className="text-purple-500"/>} />
      </div>
      
      <Card>
        <CardHeader title="Recent High-Risk Flags" subtitle="Tokens flagged with >80% rug pull probability" />
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="text-gray-400 border-b border-gray-800 text-sm">
                  <th className="pb-3 font-medium">Token Address</th>
                  <th className="pb-3 font-medium">Probability</th>
                  <th className="pb-3 font-medium">Top Risk Factor</th>
                  <th className="pb-3 font-medium">Time Flagged</th>
                  <th className="pb-3 font-medium">Action</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                <tr className="border-b border-gray-800/50">
                  <td className="py-4 font-mono text-gray-300">0x742d...44e</td>
                  <td className="py-4"><span className="px-2 py-1 bg-red-500/10 text-red-400 rounded text-xs font-bold border border-red-500/20">94.2%</span></td>
                  <td className="py-4 text-gray-300">Holder Concentration (Gini)</td>
                  <td className="py-4 text-gray-500">2 mins ago</td>
                  <td className="py-4"><a href="/predictions/0x742d" className="text-blue-400 hover:text-blue-300">View Explainability &rarr;</a></td>
                </tr>
                <tr>
                  <td className="py-4 font-mono text-gray-300">0x19a2...9b1</td>
                  <td className="py-4"><span className="px-2 py-1 bg-orange-500/10 text-orange-400 rounded text-xs font-bold border border-orange-500/20">81.7%</span></td>
                  <td className="py-4 text-gray-300">Deployer Graph Centrality</td>
                  <td className="py-4 text-gray-500">14 mins ago</td>
                  <td className="py-4"><a href="/predictions/0x19a2" className="text-blue-400 hover:text-blue-300">View Explainability &rarr;</a></td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function StatCard({title, value, icon}: {title: string, value: string, icon: React.ReactNode}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 py-6">
        <div className="p-4 bg-gray-800 rounded-lg">{icon}</div>
        <div>
          <p className="text-sm text-gray-400 font-medium">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
        </div>
      </CardContent>
    </Card>
  )
}
