from django.conf import settings
from django.db import models
from django.utils import timezone

class Post(models.Model):
    """기존 이미지 블로그 모델"""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='blog_image/%Y/%m/%d/', blank=True)
    
    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    def __str__(self):
        return self.title


class Seat(models.Model):
    """도서관 좌석 모델"""
    STATUS_CHOICES = [
        ('empty', 'Empty'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
    ]
    
    seat_number = models.IntegerField(unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='empty')
    user_name = models.CharField(max_length=100, blank=True, null=True)
    reserved_at = models.DateTimeField(blank=True, null=True)
    last_detected_at = models.DateTimeField(blank=True, null=True)
    auto_released = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['seat_number']
    
    def __str__(self):
        return f"Seat {self.seat_number} - {self.status}"
    
    def reserve(self, user_name):
        """좌석 예약"""
        self.status = 'occupied'
        self.user_name = user_name
        self.reserved_at = timezone.now()
        self.last_detected_at = timezone.now()
        self.auto_released = False
        self.save()
    
    def release(self, auto=False):
        """좌석 반납"""
        self.status = 'empty'
        self.user_name = None
        self.reserved_at = None
        self.last_detected_at = None
        self.auto_released = auto
        self.save()
    
    def update_detection(self):
        """사람 감지 시 호출"""
        self.last_detected_at = timezone.now()
        self.save()
    
    def should_auto_release(self, minutes=15):
        """자동 퇴실 조건 체크"""
        if self.status == 'occupied' and self.last_detected_at:
            time_diff = timezone.now() - self.last_detected_at
            return time_diff.total_seconds() > minutes * 60
        return False