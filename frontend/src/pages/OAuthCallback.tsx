import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import { platformsApi } from '@/services/api';

const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Processing OAuth callback...');

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Get OAuth parameters from URL
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');

        // Handle OAuth error
        if (error) {
          setStatus('error');
          setMessage(errorDescription || `OAuth failed: ${error}`);

          // Send error to parent window
          if (window.opener) {
            window.opener.postMessage({
              type: 'oauth_error',
              error: error,
              description: errorDescription,
            }, window.location.origin);
          }

          setTimeout(() => window.close(), 3000);
          return;
        }

        // Validate required parameters
        if (!code || !state) {
          setStatus('error');
          setMessage('Missing OAuth parameters');
          setTimeout(() => window.close(), 3000);
          return;
        }

        // Retrieve and validate state from localStorage
        const storedState = localStorage.getItem('oauth_state');
        const storedPlatform = localStorage.getItem('oauth_platform');

        if (!storedState || !storedPlatform) {
          setStatus('error');
          setMessage('OAuth session expired. Please try again.');
          setTimeout(() => window.close(), 3000);
          return;
        }

        if (state !== storedState) {
          setStatus('error');
          setMessage('Invalid state parameter. Possible CSRF attack.');

          // Clean up
          localStorage.removeItem('oauth_state');
          localStorage.removeItem('oauth_platform');

          setTimeout(() => window.close(), 3000);
          return;
        }

        // Exchange code for token via backend
        setMessage(`Connecting ${storedPlatform}...`);

        let response;
        if (storedPlatform === 'instagram') {
          response = await platformsApi.completeInstagramOAuth(code, state);
        } else if (storedPlatform === 'messenger') {
          response = await platformsApi.completeMessengerOAuth(code, state);
        } else {
          throw new Error(`Unsupported platform: ${storedPlatform}`);
        }

        // Success!
        setStatus('success');
        setMessage(`${storedPlatform} connected successfully!`);

        // Clean up localStorage
        localStorage.removeItem('oauth_state');
        localStorage.removeItem('oauth_platform');

        // Notify parent window of success
        if (window.opener) {
          window.opener.postMessage({
            type: 'oauth_success',
            platform: storedPlatform,
            data: response,
          }, window.location.origin);
        }

        // Close popup after short delay
        setTimeout(() => window.close(), 2000);

      } catch (error: any) {
        console.error('OAuth callback error:', error);
        setStatus('error');
        setMessage(error.response?.data?.message || error.message || 'Failed to complete OAuth');

        // Notify parent window of error
        if (window.opener) {
          window.opener.postMessage({
            type: 'oauth_error',
            error: 'connection_failed',
            description: error.response?.data?.message || error.message,
          }, window.location.origin);
        }

        setTimeout(() => window.close(), 3000);
      }
    };

    handleOAuthCallback();
  }, [searchParams]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center justify-center gap-2">
            {status === 'loading' && (
              <>
                <Loader2 className="h-6 w-6 animate-spin" />
                Processing...
              </>
            )}
            {status === 'success' && (
              <>
                <CheckCircle className="h-6 w-6 text-green-500" />
                Success!
              </>
            )}
            {status === 'error' && (
              <>
                <XCircle className="h-6 w-6 text-red-500" />
                Error
              </>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground">{message}</p>
          {status !== 'loading' && (
            <p className="text-center text-sm text-muted-foreground mt-4">
              This window will close automatically...
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default OAuthCallback;
