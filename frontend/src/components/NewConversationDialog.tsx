import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import apiClient from '../services/api/client';

interface NewConversationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const NewConversationDialog = ({ open, onOpenChange }: NewConversationDialogProps) => {
  const queryClient = useQueryClient();
  const [phoneNumber, setPhoneNumber] = useState('');
  const [contactName, setContactName] = useState('');
  const [platform, setPlatform] = useState<'whatsapp'>('whatsapp');

  const createConversationMutation = useMutation({
    mutationFn: async (data: { phone_number: string; contact_name: string; platform: string }) => {
      const response = await apiClient.post('/messages/conversations/create/', data);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success('Conversation created!');
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      onOpenChange(false);
      setPhoneNumber('');
      setContactName('');

      // Navigate to the new conversation
      window.location.href = `/conversation/${data.conversation.id}`;
    },
    onError: (error: any) => {
      const errorMsg = error.response?.data?.error || 'Failed to create conversation';
      toast.error(errorMsg);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate phone number
    if (!phoneNumber.trim()) {
      toast.error('Please enter a phone number');
      return;
    }

    // Ensure phone number starts with +
    let formattedPhone = phoneNumber.trim();
    if (!formattedPhone.startsWith('+')) {
      formattedPhone = '+' + formattedPhone;
    }

    // Validate phone number format (basic)
    const phoneRegex = /^\+[1-9]\d{1,14}$/;
    if (!phoneRegex.test(formattedPhone)) {
      toast.error('Please enter a valid phone number with country code (e.g., +380685375495)');
      return;
    }

    const name = contactName.trim() || `Contact ${formattedPhone.slice(-4)}`;

    createConversationMutation.mutate({
      phone_number: formattedPhone,
      contact_name: name,
      platform,
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Start New Conversation</DialogTitle>
          <DialogDescription>
            Enter the recipient's phone number to start a new WhatsApp conversation.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="platform">Platform</Label>
            <Select value={platform} onValueChange={(value: any) => setPlatform(value)}>
              <SelectTrigger id="platform">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="whatsapp">WhatsApp</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone">Phone Number *</Label>
            <Input
              id="phone"
              type="tel"
              placeholder="+380685375495"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              disabled={createConversationMutation.isPending}
            />
            <p className="text-xs text-muted-foreground">
              Include country code (e.g., +380 for Ukraine, +1 for USA)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Contact Name (optional)</Label>
            <Input
              id="name"
              type="text"
              placeholder="John Doe"
              value={contactName}
              onChange={(e) => setContactName(e.target.value)}
              disabled={createConversationMutation.isPending}
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={createConversationMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createConversationMutation.isPending}>
              {createConversationMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Conversation'
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
