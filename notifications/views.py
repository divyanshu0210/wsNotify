from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from .serializers import NotificationSerializer
import logging
from django.db.models import Q

logger = logging.getLogger(__name__)  # You can configure this logger in your Django settings

@api_view(['POST'])
def create_notification(request):
    sender = request.data.get("sender_id")
    receiver = request.data.get("receiver_id")
    type = request.data.get("type")
    sender_name = request.data.get("sender_name", "")
    receiver_name = request.data.get("receiver_name", "")

    notification = Notification.objects.create(
        sender_id=sender,
        receiver_id=receiver,
        type=type,
        sender_name=sender_name,
        receiver_name=receiver_name,
    )

    # Use group_send instead of channel_send
    try:
        channel_layer = get_channel_layer()
        group_name = f"user_{str(receiver)}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "content": {
                    "sender_id": sender,
                    "sender_name": sender_name,
                    "type": type,
                    "created_at": str(notification.created_at),
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to send notification to group {group_name}: {e}")

    return Response({"status": "ok"}, status=status.HTTP_201_CREATED)






@api_view(['GET'])
def get_pending_notifications(request):
    receiver_id = request.query_params.get('receiver_id')
    print(receiver_id)
    if not receiver_id:
        return Response({"error": "receiver_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch pending notifications
    notifications = Notification.objects.filter(receiver_id=str(receiver_id), status='pending')
    print(notifications)
    serializer = NotificationSerializer(notifications, many=True)
    print(serializer.data)

    notifications.update(status='sent')

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_sent_notifications(request):
    receiver_id = request.query_params.get('receiver_id')
    print(receiver_id)
    if not receiver_id:
        return Response({"error": "receiver_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch pending notifications
    notifications = Notification.objects.filter(
        Q(receiver_id=str(receiver_id)) & 
        (Q(status='sent') | (Q(status='viewed') & Q(id__in=Notification.objects.filter(
            receiver_id=str(receiver_id), 
            status='viewed'
        ).order_by('-created_at')[:10]))
    )).order_by('-created_at')
    # print(notifications)
    serializer = NotificationSerializer(notifications, many=True)
    # print(serializer.data)

    # notifications.update(status='viewed')

    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_sent_notifications_count(request):
    receiver_id = request.query_params.get('receiver_id')
    print(receiver_id)
    if not receiver_id:
        return Response({"error": "receiver_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    notifications = Notification.objects.filter(receiver_id=str(receiver_id), status='sent')
    return Response({'sent_notifications_count':notifications.count()}, status=status.HTTP_200_OK)

@api_view(['POST'])  # Use POST since we're modifying data
def mark_notifications_as_viewed(request):
    receiver_id = request.data.get('receiver_id')
    print(receiver_id)

    if not receiver_id:
        return Response({"error": "receiver_id is required."}, status=status.HTTP_400_BAD_REQUEST)
    # Get notifications with status='sent' for this receiver
    notifications = Notification.objects.filter(receiver_id=str(receiver_id), status='sent')
    print(f"Found {notifications.count()} notifications to mark as viewed")
    # Update them to 'viewed'
    notifications.update(status='viewed')

    return Response({"message": "Notifications marked as viewed."}, status=status.HTTP_200_OK)

