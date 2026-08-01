'use client'
import { Card, CardContent, CardHeader } from "@/components/ui/Card"

export default function Metrics() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-white">Model Metrics</h1>
      <p className="text-gray-400">Global performance of the Spatio-Temporal AI model.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="ROC-AUC Score" subtitle="Receiver Operating Characteristic" />
          <CardContent className="flex justify-center items-center h-64">
            <p className="text-5xl font-bold text-blue-500">0.984</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader title="F1-Score" subtitle="Harmonic Mean of Precision & Recall" />
          <CardContent className="flex justify-center items-center h-64">
             <p className="text-5xl font-bold text-green-500">0.921</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}\n