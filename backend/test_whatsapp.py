#!/usr/bin/env python
"""
Script to test WhatsApp connection and create test conversations
Run with: docker-compose -f docker-compose.prod.yml exec backend python test_whatsapp.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.platforms.models import PlatformAccount
from apps.messages.models import Conversation, Message
from apps.platforms.services.whatsapp import WhatsAppService
from django.utils import timezone


def test_whatsapp_connection():
    """Test if WhatsApp is connected and credentials are valid"""
    print("\n" + "="*60)
    print("WhatsApp Connection Test")
    print("="*60)

    # Get WhatsApp platform account
    wa_accounts = PlatformAccount.objects.filter(platform='whatsapp')

    if not wa_accounts.exists():
        print("❌ No WhatsApp accounts connected")
        print("Please connect WhatsApp first from the Settings page")
        return None

    wa = wa_accounts.first()
    print(f"✅ WhatsApp account found")
    print(f"   User: {wa.user.email}")
    print(f"   Connected: {wa.created_at}")
    print(f"   Active: {wa.is_active}")
    print(f"   Phone Number ID: {wa.metadata.get('phone_number_id')}")
    print(f"   Business Account ID: {wa.metadata.get('business_account_id')}")
    print(f"   Verified Name: {wa.metadata.get('verified_name')}")

    # Test credentials
    print("\n📡 Testing WhatsApp API credentials...")
    service = WhatsAppService()
    result = service.validate_credentials(
        phone_number_id=wa.metadata.get('phone_number_id'),
        access_token=wa.get_decrypted_access_token()
    )

    if result.get('valid'):
        print("✅ Credentials are VALID")
        print(f"   Verified Name: {result.get('verified_name')}")
        print(f"   Display Phone: {result.get('display_phone_number')}")
        print(f"   Quality Rating: {result.get('quality_rating')}")
    else:
        print(f"❌ Credentials are INVALID")
        print(f"   Error: {result.get('error')}")
        return None

    return wa


def show_conversations(wa):
    """Show existing WhatsApp conversations"""
    print("\n" + "="*60)
    print("WhatsApp Conversations")
    print("="*60)

    conversations = Conversation.objects.filter(platform_account=wa).order_by('-last_message_at')

    if not conversations.exists():
        print("📭 No conversations yet")
        print("\nTo create a conversation:")
        print("  1. Send a message TO your WhatsApp Business number from another phone")
        print("  2. OR use option 3 in the menu to create a test conversation")
        return

    print(f"Found {conversations.count()} conversation(s):\n")

    for i, conv in enumerate(conversations, 1):
        messages_count = conv.messages.count()
        print(f"{i}. {conv.participant_name}")
        print(f"   Phone: {conv.participant_id}")
        print(f"   Messages: {messages_count}")
        print(f"   Unread: {conv.unread_count}")
        print(f"   Last message: {conv.last_message_at}")
        if conv.last_message:
            preview = conv.last_message.content[:50] + "..." if len(conv.last_message.content) > 50 else conv.last_message.content
            print(f"   Preview: {preview}")
        print()


def create_test_conversation(wa):
    """Create a test conversation for WhatsApp"""
    print("\n" + "="*60)
    print("Create Test Conversation")
    print("="*60)

    phone = input("\nEnter recipient phone number (with country code, e.g., +1234567890): ").strip()

    if not phone:
        print("❌ Phone number required")
        return

    if not phone.startswith('+'):
        print("⚠️  Phone number should start with + and country code")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return

    name = input("Enter contact name (or press Enter for default): ").strip()
    if not name:
        name = f"Test Contact {phone[-4:]}"

    # Check if conversation already exists
    existing = Conversation.objects.filter(
        platform_account=wa,
        participant_id=phone
    ).first()

    if existing:
        print(f"\n⚠️  Conversation already exists with {existing.participant_name}")
        print(f"   ID: {existing.id}")
        print(f"   Messages: {existing.messages.count()}")
        overwrite = input("Create anyway? (y/n): ").strip().lower()
        if overwrite != 'y':
            return

    # Create conversation
    conv = Conversation.objects.create(
        platform_account=wa,
        participant_id=phone,
        participant_name=name,
        platform_conversation_id=f"wa_{phone}",
        last_message_at=timezone.now(),
        unread_count=0,
        is_archived=False
    )

    print(f"\n✅ Test conversation created!")
    print(f"   ID: {conv.id}")
    print(f"   Name: {conv.participant_name}")
    print(f"   Phone: {conv.participant_id}")
    print(f"\nYou can now:")
    print(f"  1. Go to the Chats page in the app")
    print(f"  2. Click on '{conv.participant_name}'")
    print(f"  3. Send a test message!")
    print(f"\n⚠️  Note: The recipient will receive an actual WhatsApp message!")


def send_test_message(wa):
    """Send a test WhatsApp message"""
    print("\n" + "="*60)
    print("Send Test Message")
    print("="*60)

    # Show conversations
    conversations = Conversation.objects.filter(platform_account=wa).order_by('-last_message_at')

    if not conversations.exists():
        print("❌ No conversations found")
        print("Create a conversation first (option 3)")
        return

    print("\nAvailable conversations:\n")
    for i, conv in enumerate(conversations, 1):
        print(f"{i}. {conv.participant_name} ({conv.participant_id})")

    try:
        choice = int(input("\nSelect conversation number: ").strip())
        if choice < 1 or choice > conversations.count():
            print("❌ Invalid choice")
            return

        conv = list(conversations)[choice - 1]
    except (ValueError, IndexError):
        print("❌ Invalid input")
        return

    message_text = input("\nEnter message to send: ").strip()
    if not message_text:
        print("❌ Message cannot be empty")
        return

    print(f"\n📤 Sending message to {conv.participant_name}...")

    service = WhatsAppService()
    result = service.send_text_message(
        recipient_phone=conv.participant_id,
        message_text=message_text,
        phone_number_id=wa.metadata.get('phone_number_id'),
        access_token=wa.get_decrypted_access_token()
    )

    if result:
        print("✅ Message sent successfully!")
        print(f"   Message ID: {result.get('messages', [{}])[0].get('id')}")

        # Create message record in database
        msg_id = result.get('messages', [{}])[0].get('id')
        Message.objects.create(
            conversation=conv,
            platform_account=wa,
            platform_message_id=msg_id,
            message_type='text',
            content=message_text,
            sender_id=wa.platform_user_id,
            sender_name=wa.platform_username or 'Me',
            is_incoming=False,
            is_read=True,
            sent_at=timezone.now(),
            delivered_at=timezone.now()
        )

        conv.last_message_at = timezone.now()
        conv.save()

        print("✅ Message saved to database")
    else:
        print("❌ Failed to send message")
        print("Check the error logs above")


def main():
    """Main menu"""
    wa = test_whatsapp_connection()

    if not wa:
        return

    while True:
        print("\n" + "="*60)
        print("WhatsApp Test Menu")
        print("="*60)
        print("1. Show conversations")
        print("2. Send test message")
        print("3. Create test conversation")
        print("4. Recheck WhatsApp connection")
        print("5. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == '1':
            show_conversations(wa)
        elif choice == '2':
            send_test_message(wa)
        elif choice == '3':
            create_test_conversation(wa)
        elif choice == '4':
            wa = test_whatsapp_connection()
            if not wa:
                break
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")


if __name__ == '__main__':
    main()
