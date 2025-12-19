from rest_framework import serializers
from .models import Post, Seat

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'text', 'created_date', 'published_date', 'image']


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = [
            'id',
            'seat_number',
            'status',
            'user_name',
            'reserved_at',
            'last_detected_at',
            'auto_released'
        ]
        read_only_fields = ['id']


class SeatUpdateSerializer(serializers.Serializer):
    """Edge에서 좌석 상태 업데이트용"""
    seat_number = serializers.IntegerField()
    person_detected = serializers.BooleanField()
    timestamp = serializers.DateTimeField()