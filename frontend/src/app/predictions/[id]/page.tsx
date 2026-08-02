'use client'
import { Card, CardContent, CardHeader } from "@/components/ui/Card"
import dynamic from 'next/dynamic'
import { useState } from 'react'
import { ShieldAlert, Network, ListTree, Activity } from 'lucide-react'

// Dynamically import force graph to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false })

export default function PredictionDetail({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = useState('shap')
  
  // Mock Graph Data for GNNExplainer
  const graphData = {
    nodes: [
      { id: 'Deployer', group: 1, val: 20, color: '#ef4444' }, // Red (Bad actor)
      { id: 'Pool', group: 2, val: 15, color: '#3b82f6' },
      { id: 'Wallet A', group: 3, val: 5, color: '#9ca3af' },
      { id: 'Wallet B', group: 3, val: 5, color: '#9ca3af' },
      { id: 'Wallet C', group: 3, val: 5, color: '#9ca3af' }
    ],
    links: [
      { source: 'Deployer', target: 'Wallet A', value: 10 },
      { source: 'Deployer', target: 'Wallet B', value: 10 },
      { source: 'Deployer', target: 'Wallet C', value: 10 },
      { source: 'Wallet A', target: 'Pool', value: 2 },
      { source: 'Wallet B', target: 'Pool', value: 2 }
    ]
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            Token Analysis
            <span className="text-lg font-mono px-3 py-1 bg-gray-800 rounded-md text-gray-300">{params.id}</span>
          </h1>
          <p className="text-gray-400 mt-2">Comprehensive AI evaluation combining Spatial and Temporal learning.</p>
        </div>
        
        <div className="bg-red-500/10 border border-red-500/20 px-6 py-4 rounded-xl text-center">
          <p className="text-red-400 text-sm font-bold uppercase tracking-wider mb-1">Rug Pull Probability</p>
          <p className="text-4xl font-bold text-white flex items-center gap-2 justify-center">
            94.2% <ShieldAlert className="text-red-500" />
          </p>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-900 p-1 rounded-lg border border-gray-800 w-fit">
        <button onClick={() => setActiveTab('shap')} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'shap' ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800/50'}`}>
          <ListTree size={16} /> SHAP Features
        </button>
        <button onClick={() => setActiveTab('gnn')} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'gnn' ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800/50'}`}>
          <Network size={16} /> GNNExplainer
        </button>
      </div>

      <Card>
        <CardHeader 
          title={activeTab === 'shap' ? "Feature Importance (SHAP)" : "Critical Subgraph (GNNExplainer)"} 
          subtitle={activeTab === 'shap' ? "Which exact features triggered the alert?" : "Which specific wallets and transactions drove the spatial prediction?"} 
        />
        <CardContent>
          {activeTab === 'shap' ? (
            <div className="space-y-4">
              <div className="w-full">
                <div className="flex justify-between mb-1 text-sm text-gray-300"><span>Holder Gini (Supply Concentration)</span> <span className="text-red-400">+0.42</span></div>
                <div className="w-full bg-gray-800 rounded-full h-2.5"><div className="bg-red-500 h-2.5 rounded-full" style={{width: '85%'}}></div></div>
              </div>
              <div className="w-full">
                <div className="flex justify-between mb-1 text-sm text-gray-300"><span>Tx Burstiness (Rapid Automated Trades)</span> <span className="text-red-400">+0.31</span></div>
                <div className="w-full bg-gray-800 rounded-full h-2.5"><div className="bg-red-500 h-2.5 rounded-full" style={{width: '60%'}}></div></div>
              </div>
              <div className="w-full">
                <div className="flex justify-between mb-1 text-sm text-gray-300"><span>Has Mint Function (Smart Contract Risk)</span> <span className="text-orange-400">+0.15</span></div>
                <div className="w-full bg-gray-800 rounded-full h-2.5"><div className="bg-orange-500 h-2.5 rounded-full" style={{width: '30%'}}></div></div>
              </div>
              <div className="w-full">
                <div className="flex justify-between mb-1 text-sm text-gray-300"><span>Pool Connectivity (Structural Isolation)</span> <span className="text-blue-400">-0.05</span></div>
                <div className="w-full bg-gray-800 rounded-full h-2.5 flex justify-end"><div className="bg-blue-500 h-2.5 rounded-full" style={{width: '10%'}}></div></div>
              </div>
            </div>
          ) : (
            <div className="h-[400px] bg-black/50 rounded-lg border border-gray-800 overflow-hidden relative">
              <div className="absolute top-4 left-4 z-10 bg-gray-900/80 p-3 rounded-lg border border-gray-700 text-xs text-gray-300 space-y-2">
                <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500"></div> Suspicious Deployer</div>
                <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-500"></div> Liquidity Pool</div>
                <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-gray-400"></div> Wash-Trading Wallets</div>
              </div>
              <ForceGraph2D
                graphData={graphData}
                nodeAutoColorBy="group"
                nodeRelSize={6}
                linkColor={() => 'rgba(255,255,255,0.2)'}
                backgroundColor="#000000"
                width={800}
                height={400}
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
