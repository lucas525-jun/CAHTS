import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { platformsApi, handleApiError } from '../services/api';
import { toast } from 'sonner';
import { Loader2, Settings2, Trash2, RefreshCw, CheckCircle, XCircle } from 'lucide-react';
import { InstagramIcon, MessengerIcon, WhatsAppIcon } from '@/components/icons/PlatformIcons';
import { useAuth } from '../contexts/AuthContext';

// Helper function to generate secure random state
const generateState = (): string => {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
};

const Settings = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [whatsappDialogOpen, setWhatsappDialogOpen] = useState(false);
  const [whatsappPhone, setWhatsappPhone] = useState('');
  const [whatsappToken, setWhatsappToken] = useState('');

  // Fetch connected platforms
  const { data: platforms, isLoading } = useQuery({
    queryKey: ['platforms'],
    queryFn: () => platformsApi.list(),
  });

  // Listen for OAuth callback messages from popup
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // Verify origin for security
      if (event.origin !== window.location.origin) {
        return;
      }

      const { type, platform, error, description } = event.data;

      if (type === 'oauth_success') {
        toast.success(`${platform} connected successfully!`);
        queryClient.invalidateQueries({ queryKey: ['platforms'] });
      } else if (type === 'oauth_error') {
        toast.error(description || error || 'OAuth connection failed');
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [queryClient]);

  // Connect Instagram mutation
  const connectInstagram = useMutation({
    mutationFn: () => platformsApi.connectInstagram(),
    onSuccess: (data) => {
      // Generate and store state in localStorage for CSRF protection
      const state = generateState();
      localStorage.setItem('oauth_state', state);
      localStorage.setItem('oauth_platform', 'instagram');

      // Append state to OAuth URL
      const oauthUrl = new URL(data.oauth_url);
      oauthUrl.searchParams.set('state', state);

      // Update redirect_uri to point to frontend callback
      const callbackUrl = `${window.location.origin}/oauth/callback`;
      oauthUrl.searchParams.set('redirect_uri', callbackUrl);

      // Open OAuth popup
      const width = 600;
      const height = 700;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;

      window.open(
        oauthUrl.toString(),
        'Instagram OAuth',
        `width=${width},height=${height},left=${left},top=${top}`
      );
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
  });

  // Connect Messenger mutation
  const connectMessenger = useMutation({
    mutationFn: () => platformsApi.connectMessenger(),
    onSuccess: (data) => {
      // Generate and store state in localStorage for CSRF protection
      const state = generateState();
      localStorage.setItem('oauth_state', state);
      localStorage.setItem('oauth_platform', 'messenger');

      // Append state to OAuth URL
      const oauthUrl = new URL(data.oauth_url);
      oauthUrl.searchParams.set('state', state);

      // Update redirect_uri to point to frontend callback
      const callbackUrl = `${window.location.origin}/oauth/callback`;
      oauthUrl.searchParams.set('redirect_uri', callbackUrl);

      // Open OAuth popup
      const width = 600;
      const height = 700;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;

      window.open(
        oauthUrl.toString(),
        'Messenger OAuth',
        `width=${width},height=${height},left=${left},top=${top}`
      );
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
  });

  // Connect WhatsApp mutation
  const connectWhatsApp = useMutation({
    mutationFn: (data: { phone_number_id: string; access_token: string }) =>
      platformsApi.connectWhatsApp(data.phone_number_id, data.access_token),
    onSuccess: () => {
      toast.success('WhatsApp connected successfully!');
      setWhatsappDialogOpen(false);
      setWhatsappPhone('');
      setWhatsappToken('');
      queryClient.invalidateQueries({ queryKey: ['platforms'] });
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
  });

  // Disconnect platform mutation
  const disconnectPlatform = useMutation({
    mutationFn: (id: string) => platformsApi.disconnect(id),
    onSuccess: () => {
      toast.success('Platform disconnected successfully!');
      queryClient.invalidateQueries({ queryKey: ['platforms'] });
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
  });

  // Sync platform mutation
  const syncPlatform = useMutation({
    mutationFn: (id: string) => platformsApi.sync(id),
    onSuccess: () => {
      toast.success('Sync started!');
      queryClient.invalidateQueries({ queryKey: ['platforms'] });
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
  });

  const handleWhatsAppSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    connectWhatsApp.mutate({
      phone_number_id: whatsappPhone,
      access_token: whatsappToken,
    });
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'instagram':
        return <InstagramIcon className="h-6 w-6" />;
      case 'messenger':
        return <MessengerIcon className="h-6 w-6" />;
      case 'whatsapp':
        return <WhatsAppIcon className="h-6 w-6" />;
      default:
        return <Settings2 className="h-6 w-6" />;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'instagram':
        return 'from-instagram-start to-instagram-end';
      case 'messenger':
        return 'from-messenger to-messenger';
      case 'whatsapp':
        return 'from-whatsapp to-whatsapp';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Settings</h1>
          <p className="text-muted-foreground">
            Manage your platform connections and preferences
          </p>
        </div>

        {/* User Info */}
        {user && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <span className="text-sm text-muted-foreground">Name:</span>
                  <p className="font-medium">
                    {user.first_name} {user.last_name}
                  </p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Email:</span>
                  <p className="font-medium">{user.email}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Connected Platforms */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Connected Platforms</CardTitle>
            <CardDescription>
              Manage your Instagram, Messenger, and WhatsApp connections
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : platforms && platforms.length > 0 ? (
              <div className="space-y-4">
                {platforms.map((platform) => (
                  <div
                    key={platform.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`p-3 rounded-full bg-gradient-to-r ${getPlatformColor(platform.platform)}`}>
                        <div className="text-white">
                          {getPlatformIcon(platform.platform)}
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold capitalize">{platform.platform}</h3>
                          {platform.is_active ? (
                            <Badge variant="default" className="bg-green-500">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Active
                            </Badge>
                          ) : (
                            <Badge variant="destructive">
                              <XCircle className="h-3 w-3 mr-1" />
                              Inactive
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          @{platform.username}
                        </p>
                        {platform.last_sync_at && (
                          <p className="text-xs text-muted-foreground">
                            Last synced: {new Date(platform.last_sync_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => syncPlatform.mutate(platform.id)}
                        disabled={syncPlatform.isPending}
                      >
                        {syncPlatform.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <RefreshCw className="h-4 w-4" />
                        )}
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => {
                          if (confirm(`Disconnect ${platform.platform}?`)) {
                            disconnectPlatform.mutate(platform.id);
                          }
                        }}
                        disabled={disconnectPlatform.isPending}
                      >
                        {disconnectPlatform.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-8">
                No platforms connected yet
              </p>
            )}
          </CardContent>
        </Card>

        {/* Connect New Platform */}
        <Card>
          <CardHeader>
            <CardTitle>Connect New Platform</CardTitle>
            <CardDescription>
              Add Instagram, Messenger, or WhatsApp to your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Instagram */}
              <Button
                variant="outline"
                className="h-auto flex-col gap-3 p-6"
                onClick={() => connectInstagram.mutate()}
                disabled={connectInstagram.isPending}
              >
                <div className="p-3 rounded-full bg-gradient-to-r from-instagram-start to-instagram-end">
                  <InstagramIcon className="h-6 w-6 text-white" />
                </div>
                <div className="text-center">
                  <h3 className="font-semibold">Instagram</h3>
                  <p className="text-xs text-muted-foreground">
                    Connect via Facebook OAuth
                  </p>
                </div>
                {connectInstagram.isPending && (
                  <Loader2 className="h-4 w-4 animate-spin" />
                )}
              </Button>

              {/* Messenger */}
              <Button
                variant="outline"
                className="h-auto flex-col gap-3 p-6"
                onClick={() => connectMessenger.mutate()}
                disabled={connectMessenger.isPending}
              >
                <div className="p-3 rounded-full bg-messenger">
                  <MessengerIcon className="h-6 w-6 text-white" />
                </div>
                <div className="text-center">
                  <h3 className="font-semibold">Messenger</h3>
                  <p className="text-xs text-muted-foreground">
                    Connect via Facebook OAuth
                  </p>
                </div>
                {connectMessenger.isPending && (
                  <Loader2 className="h-4 w-4 animate-spin" />
                )}
              </Button>

              {/* WhatsApp */}
              <Dialog open={whatsappDialogOpen} onOpenChange={setWhatsappDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="h-auto flex-col gap-3 p-6">
                    <div className="p-3 rounded-full bg-whatsapp">
                      <WhatsAppIcon className="h-6 w-6 text-white" />
                    </div>
                    <div className="text-center">
                      <h3 className="font-semibold">WhatsApp</h3>
                      <p className="text-xs text-muted-foreground">
                        Business API
                      </p>
                    </div>
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Connect WhatsApp Business</DialogTitle>
                    <DialogDescription>
                      Enter your WhatsApp Business API credentials
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleWhatsAppSubmit} className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">Phone Number ID</label>
                      <Input
                        type="text"
                        placeholder="1234567890"
                        value={whatsappPhone}
                        onChange={(e) => setWhatsappPhone(e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Access Token</label>
                      <Input
                        type="password"
                        placeholder="Your WhatsApp access token"
                        value={whatsappToken}
                        onChange={(e) => setWhatsappToken(e.target.value)}
                        required
                      />
                    </div>
                    <Button
                      type="submit"
                      className="w-full"
                      disabled={connectWhatsApp.isPending}
                    >
                      {connectWhatsApp.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Connecting...
                        </>
                      ) : (
                        'Connect WhatsApp'
                      )}
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Settings;
