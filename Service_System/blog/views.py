from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post, Seat
from .serializers import PostSerializer, SeatSerializer, SeatUpdateSerializer


# ==================== 기존 Post 관련 ====================
class BlogImages(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


# ==================== Seat API ====================
class SeatViewSet(viewsets.ModelViewSet):
    """좌석 정보 CRUD API"""
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    
    @action(detail=False, methods=['post'])
    def update_from_edge(self, request):
        """
        Edge에서 호출하는 좌석 상태 업데이트
        POST /api_root/Seat/update_from_edge/
        """
        serializer = SeatUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        seat_number = serializer.validated_data['seat_number']
        person_detected = serializer.validated_data['person_detected']
        
        try:
            seat = Seat.objects.get(seat_number=seat_number)
        except Seat.DoesNotExist:
            return Response(
                {'error': f'Seat {seat_number} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if person_detected:
            # 사람 감지되면 시간 업데이트
            seat.update_detection()
            return Response({
                'message': f'Seat {seat_number} detection updated',
                'seat': SeatSerializer(seat).data
            })
        
        return Response({'message': 'No person detected'})
    
    @action(detail=False, methods=['post'])
    def auto_release_check(self, request):
        """
        자동 퇴실 체크 및 실행
        POST /api_root/Seat/auto_release_check/
        """
        minutes = request.data.get('minutes', 15)
        released_seats = []
        
        for seat in Seat.objects.filter(status='occupied'):
            if seat.should_auto_release(minutes):
                seat.release(auto=True)
                released_seats.append(seat.seat_number)
        
        return Response({
            'message': f'{len(released_seats)} seats auto-released',
            'released_seats': released_seats
        })
    
    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        """좌석 예약"""
        seat = self.get_object()
        
        if seat.status != 'empty':
            return Response(
                {'error': 'Seat is not available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_name = request.data.get('user_name', 'Anonymous')
        seat.reserve(user_name)
        
        return Response({
            'message': f'Seat {seat.seat_number} reserved',
            'seat': SeatSerializer(seat).data
        })
    
    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        """좌석 수동 반납"""
        seat = self.get_object()
        
        if seat.status != 'occupied':
            return Response(
                {'error': 'Seat is not occupied'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seat.release(auto=False)
        
        return Response({
            'message': f'Seat {seat.seat_number} released',
            'seat': SeatSerializer(seat).data
        })