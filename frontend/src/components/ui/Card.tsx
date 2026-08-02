import React from 'react'

export function Card({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return <div className={`bg-gray-900 border border-gray-800 rounded-xl overflow-hidden ${className}`}>{children}</div>
}

export function CardHeader({ title, subtitle }: { title: string, subtitle?: string }) {
  return (
    <div className="p-6 border-b border-gray-800">
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
    </div>
  )
}

export function CardContent({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return <div className={`p-6 ${className}`}>{children}</div>
}
