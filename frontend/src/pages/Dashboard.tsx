import { Card } from '@/components/ui/card';
import { MessageSquare, TrendingUp } from 'lucide-react';
import { mockMessages, dailyMessageVolume } from '@/data/mockData';
import { BarChart, Bar, XAxis, ResponsiveContainer, Cell } from 'recharts';

const Dashboard = () => {
  const totalMessages = mockMessages.length;
  const instagramCount = mockMessages.filter(m => m.platform === 'instagram').length;
  const whatsappCount = mockMessages.filter(m => m.platform === 'whatsapp').length;
  const messengerCount = mockMessages.filter(m => m.platform === 'messenger').length;

  const totalWeeklyMessages = dailyMessageVolume.reduce((sum, day) => sum + day.count, 0);

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Messages</p>
                <p className="text-3xl font-bold mt-2">{totalMessages}</p>
              </div>
              <MessageSquare className="h-8 w-8 text-chart-1" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Instagram</p>
                <p className="text-3xl font-bold mt-2">{instagramCount}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-gradient-to-r from-instagram-start to-instagram-end flex items-center justify-center">
                <MessageSquare className="h-6 w-6 text-white" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">WhatsApp</p>
                <p className="text-3xl font-bold mt-2">{whatsappCount}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-whatsapp flex items-center justify-center">
                <MessageSquare className="h-6 w-6 text-white" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Messenger</p>
                <p className="text-3xl font-bold mt-2">{messengerCount}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-messenger flex items-center justify-center">
                <MessageSquare className="h-6 w-6 text-white" />
              </div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Weekly Message Volume</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dailyMessageVolume}>
                  <XAxis 
                    dataKey="day" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                  />
                  <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                    {dailyMessageVolume.map((entry, index) => (
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
          </Card>

          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-secondary rounded-lg">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-5 w-5 text-chart-1" />
                  <span className="font-medium">Weekly Total</span>
                </div>
                <span className="text-2xl font-bold">{totalWeeklyMessages}</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-secondary rounded-lg">
                <div className="flex items-center gap-3">
                  <MessageSquare className="h-5 w-5 text-chart-2" />
                  <span className="font-medium">Average per Day</span>
                </div>
                <span className="text-2xl font-bold">
                  {Math.round(totalWeeklyMessages / 7)}
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-secondary rounded-lg">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-5 w-5 text-chart-3" />
                  <span className="font-medium">Peak Day</span>
                </div>
                <span className="text-2xl font-bold">
                  {Math.max(...dailyMessageVolume.map(d => d.count))}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
