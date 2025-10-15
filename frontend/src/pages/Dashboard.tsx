import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageSquare, TrendingUp, Loader2, AlertCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, ResponsiveContainer, Cell } from 'recharts';
import { useDashboardStats, usePlatforms, useDailyStats } from '../hooks/api/useDashboard';
import { useAuth } from '../contexts/AuthContext';
import { InstagramIcon, MessengerIcon, WhatsAppIcon } from '@/components/icons/PlatformIcons';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { stats, isLoading, error } = useDashboardStats();
  const { data: platforms, isLoading: platformsLoading } = usePlatforms();
  const { data: dailyStatsData, isLoading: dailyStatsLoading } = useDailyStats(7);

  // Transform daily stats data for chart
  const dailyMessageVolume = useMemo(() => {
    if (!dailyStatsData) return [];

    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    return dailyStatsData.map(stat => {
      const date = new Date(stat.date);
      const dayName = dayNames[date.getDay()];
      return {
        day: dayName,
        count: stat.message_count,
        fullDate: stat.date
      };
    });
  }, [dailyStatsData]);

  const totalWeeklyMessages = useMemo(() => {
    return dailyMessageVolume.reduce((sum, day) => sum + day.count, 0);
  }, [dailyMessageVolume]);

  if (error) {
    return (
      <div className="min-h-screen bg-background p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col items-center justify-center h-96">
            <AlertCircle className="h-12 w-12 text-destructive mb-4" />
            <h2 className="text-2xl font-semibold mb-2">Failed to load dashboard</h2>
            <p className="text-muted-foreground">Please try refreshing the page</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold">Dashboard</h1>
            {user && (
              <p className="text-muted-foreground mt-2">
                Welcome back, {user.first_name || user.email}!
              </p>
            )}
          </div>
          {platformsLoading ? (
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          ) : (
            <div className="text-sm text-muted-foreground">
              {platforms?.length || 0} platform{platforms?.length !== 1 ? 's' : ''} connected
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Conversations</p>
                {isLoading ? (
                  <Loader2 className="h-8 w-8 animate-spin mt-2" />
                ) : (
                  <p className="text-3xl font-bold mt-2">{stats.totalConversations}</p>
                )}
              </div>
              <MessageSquare className="h-8 w-8 text-chart-1" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Instagram</p>
                {isLoading ? (
                  <Loader2 className="h-8 w-8 animate-spin mt-2" />
                ) : (
                  <p className="text-3xl font-bold mt-2">{stats.instagram}</p>
                )}
              </div>
              <div className="h-12 w-12 rounded-full bg-gradient-to-r from-instagram-start to-instagram-end flex items-center justify-center">
                <InstagramIcon className="h-6 w-6 text-white" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">WhatsApp</p>
                {isLoading ? (
                  <Loader2 className="h-8 w-8 animate-spin mt-2" />
                ) : (
                  <p className="text-3xl font-bold mt-2">{stats.whatsapp}</p>
                )}
              </div>
              <div className="h-12 w-12 rounded-full bg-whatsapp flex items-center justify-center">
                <WhatsAppIcon className="h-6 w-6 text-white" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Messenger</p>
                {isLoading ? (
                  <Loader2 className="h-8 w-8 animate-spin mt-2" />
                ) : (
                  <p className="text-3xl font-bold mt-2">{stats.messenger}</p>
                )}
              </div>
              <div className="h-12 w-12 rounded-full bg-messenger flex items-center justify-center">
                <MessengerIcon className="h-6 w-6 text-white" />
              </div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Weekly Message Volume</h2>
            <div className="h-64">
              {dailyStatsLoading ? (
                <div className="flex items-center justify-center h-full">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : dailyMessageVolume.length > 0 ? (
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
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  <p>No message data available</p>
                </div>
              )}
            </div>
          </Card>

          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-secondary rounded-lg">
                <div className="flex items-center gap-3">
                  <MessageSquare className="h-5 w-5 text-chart-1" />
                  <span className="font-medium">Unread Messages</span>
                </div>
                {isLoading ? (
                  <Loader2 className="h-6 w-6 animate-spin" />
                ) : (
                  <span className="text-2xl font-bold">{stats.unreadMessages}</span>
                )}
              </div>
              <div className="flex items-center justify-between p-4 bg-secondary rounded-lg">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-5 w-5 text-chart-2" />
                  <span className="font-medium">Weekly Total</span>
                </div>
                <span className="text-2xl font-bold">{totalWeeklyMessages}</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-secondary rounded-lg">
                <div className="flex items-center gap-3">
                  <MessageSquare className="h-5 w-5 text-chart-3" />
                  <span className="font-medium">Average per Day</span>
                </div>
                <span className="text-2xl font-bold">
                  {Math.round(totalWeeklyMessages / 7)}
                </span>
              </div>
            </div>
          </Card>
        </div>

        {/* No platforms connected state */}
        {!platformsLoading && (!platforms || platforms.length === 0) && (
          <Card className="p-8 mt-6">
            <div className="text-center">
              <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No platforms connected</h3>
              <p className="text-muted-foreground mb-4">
                Connect Instagram, Messenger, or WhatsApp to start managing your messages
              </p>
              <Button onClick={() => navigate('/settings')}>
                Connect Platform
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
