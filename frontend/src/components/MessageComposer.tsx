import { useState, KeyboardEvent, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Loader2, Paperclip, X, Image as ImageIcon, Video, File } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMutation } from '@tanstack/react-query';
import { uploadApi, handleApiError } from '../services/api';
import { toast } from 'sonner';

interface MessageComposerProps {
  onSend: (content: string, mediaUrl?: string, messageType?: string) => void;
  disabled?: boolean;
  loading?: boolean;
  placeholder?: string;
  className?: string;
}

interface AttachedFile {
  file: File;
  preview?: string;
  mediaUrl?: string;
  fileType: string;
}

export const MessageComposer = ({
  onSend,
  disabled = false,
  loading = false,
  placeholder = 'Type a message...',
  className,
}: MessageComposerProps) => {
  const [content, setContent] = useState('');
  const [attachedFile, setAttachedFile] = useState<AttachedFile | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Upload file mutation
  const uploadMutation = useMutation({
    mutationFn: uploadApi.uploadFile,
    onSuccess: (data) => {
      setAttachedFile((prev) => prev ? { ...prev, mediaUrl: data.data.media_url } : null);
      toast.success('File uploaded successfully!');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
      setAttachedFile(null);
    },
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (10MB for most, 25MB for videos)
    const maxSize = file.type.startsWith('video/') ? 25 * 1024 * 1024 : 10 * 1024 * 1024;
    if (file.size > maxSize) {
      toast.error(`File too large. Max size: ${maxSize / (1024 * 1024)}MB`);
      return;
    }

    // Get file type
    let fileType = 'file';
    if (file.type.startsWith('image/')) fileType = 'image';
    else if (file.type.startsWith('video/')) fileType = 'video';
    else if (file.type.startsWith('audio/')) fileType = 'audio';

    // Create preview for images
    let preview: string | undefined;
    if (fileType === 'image') {
      preview = URL.createObjectURL(file);
    }

    setAttachedFile({ file, preview, fileType });

    // Upload file immediately
    uploadMutation.mutate(file);

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleRemoveFile = () => {
    if (attachedFile?.preview) {
      URL.revokeObjectURL(attachedFile.preview);
    }
    setAttachedFile(null);
  };

  const handleSend = () => {
    const hasContent = content.trim();
    const hasFile = attachedFile?.mediaUrl;

    if ((hasContent || hasFile) && !disabled && !loading && !uploadMutation.isPending) {
      onSend(
        content.trim(),
        attachedFile?.mediaUrl,
        attachedFile?.fileType
      );
      setContent('');
      handleRemoveFile();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getFileIcon = () => {
    switch (attachedFile?.fileType) {
      case 'image':
        return <ImageIcon className="h-4 w-4" />;
      case 'video':
        return <Video className="h-4 w-4" />;
      default:
        return <File className="h-4 w-4" />;
    }
  };

  const canSend = (content.trim() || attachedFile?.mediaUrl) && !disabled && !loading && !uploadMutation.isPending;

  return (
    <div className={cn('flex flex-col gap-2 p-4 bg-background border-t', className)}>
      {/* File Preview */}
      {attachedFile && (
        <div className="flex items-center gap-2 p-2 bg-muted rounded-lg">
          <div className="flex items-center gap-2 flex-1">
            {attachedFile.preview ? (
              <img
                src={attachedFile.preview}
                alt="Preview"
                className="h-12 w-12 object-cover rounded"
              />
            ) : (
              <div className="h-12 w-12 bg-muted-foreground/20 rounded flex items-center justify-center">
                {getFileIcon()}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{attachedFile.file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(attachedFile.file.size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>
          {uploadMutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          ) : (
            <Button
              variant="ghost"
              size="icon"
              onClick={handleRemoveFile}
              className="h-8 w-8 shrink-0"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      )}

      {/* Input Area */}
      <div className="flex items-end gap-2">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.txt"
          onChange={handleFileSelect}
          className="hidden"
        />

        <Button
          variant="outline"
          size="icon"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || loading || uploadMutation.isPending || !!attachedFile}
          className="h-[60px] w-[60px] shrink-0"
        >
          <Paperclip className="h-5 w-5" />
        </Button>

        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || loading}
          className="min-h-[60px] max-h-[200px] resize-none"
          rows={2}
        />

        <Button
          onClick={handleSend}
          disabled={!canSend}
          size="icon"
          className="h-[60px] w-[60px] shrink-0"
        >
          {loading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
        </Button>
      </div>
    </div>
  );
};
