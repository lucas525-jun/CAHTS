import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText } from 'lucide-react';
import { PlatformStats, DailyMessageVolume } from '@/types/chat';
import { BarChart, Bar, XAxis, ResponsiveContainer, Cell } from 'recharts';

interface StatsPanelProps {
  platformStats: PlatformStats[];
  dailyVolume: DailyMessageVolume[];
}

const platformLabels = {
  instagram: 'Instagram',
  messenger: 'Messenger',
  whatsapp: 'WhatsApp',
};

export const StatsPanel = ({ platformStats, dailyVolume }: StatsPanelProps) => {
  const maxValue = Math.max(...dailyVolume.map(d => d.count));
  
  return (
    <div className="w-80 border-l border-border bg-card p-6 space-y-6">
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Messages Today</h3>
          <Button variant="ghost" size="sm">
            <FileText className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
        <div className="space-y-3">
          {platformStats.map((stat) => (
            <div key={stat.platform} className="flex items-center justify-between">
              <span className="text-sm font-medium text-muted-foreground">
                {platformLabels[stat.platform]}
              </span>
              <span className="text-lg font-bold">{stat.count}</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4">Message Volume</h3>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dailyVolume}>
              <XAxis 
                dataKey="day" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
              />
              <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                {dailyVolume.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={`hsl(var(--chart-${(index % 5) + 1}))`}
                    opacity={0.8}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
