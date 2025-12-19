#!/usr/bin/env python3
"""
SmartLib - 도서관 좌석 사람 감지 시스템
YOLOv5 기반 실시간 좌석 모니터링
"""

import cv2
import torch
import requests
import numpy as np
from datetime import datetime

class SeatDetection:
    def __init__(self):
        print("🚀 SmartLib Seat Detection System Starting...")
        
        # YOLO 모델 로드
        print("📦 Loading YOLOv5 model...")
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        self.model.conf = 0.5  # confidence threshold
        print("✅ Model loaded!")
        
        # 서버 설정
        self.HOST = 'http://127.0.0.1:8000'
        self.token = self._get_token()
        
        # 좌석 ROI 설정 (640x480 화면 4등분)
        self.seats = {
            1: {'x1': 0,   'y1': 0,   'x2': 320, 'y2': 240, 'name': 'Seat 1', 'last_status': None},
            2: {'x1': 320, 'y1': 0,   'x2': 640, 'y2': 240, 'name': 'Seat 2', 'last_status': None},
            3: {'x1': 0,   'y1': 240, 'x2': 320, 'y2': 480, 'name': 'Seat 3', 'last_status': None},
            4: {'x1': 320, 'y1': 240, 'x2': 640, 'y2': 480, 'name': 'Seat 4', 'last_status': None},
        }
        
        # 쿨다운 (5초마다 전송)
        self.last_send_time = {}
        self.COOLDOWN_SECONDS = 5
        
        print("✅ Initialization complete!")
    
    def _get_token(self):
        """JWT 토큰 획득"""
        try:
            print("🔑 Getting JWT token...")
            res = requests.post(f'{self.HOST}/api-token-auth/', {
                'username': 'jeong-yunmi',
                'password': 'oppopp0912!'
            }, timeout=5)
            
            res.raise_for_status()
            token_data = res.json()
            token = token_data.get('access') or token_data.get('token')
            
            if token:
                print(f"✅ Token acquired: {token[:30]}...")
                return token
            else:
                print("❌ No token in response")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Is Django running?")
            return None
        except Exception as e:
            print(f"❌ Token error: {e}")
            return None
    
    def detect_person_in_roi(self, results, roi):
        """ROI 내에 사람이 있는지 확인"""
        x1, y1, x2, y2 = roi['x1'], roi['y1'], roi['x2'], roi['y2']
        
        # YOLO 결과에서 person (class 0) 필터링
        for *box, conf, cls in results.xyxy[0]:
            if int(cls) == 0:  # person
                bx1, by1, bx2, by2 = map(int, box)
                
                # 바운딩 박스 중심점 계산
                center_x = (bx1 + bx2) // 2
                center_y = (by1 + by2) // 2
                
                # ROI 내에 중심점이 있는지 확인
                if x1 <= center_x <= x2 and y1 <= center_y <= y2:
                    return True
        
        return False
    
    def send_to_server(self, seat_number, person_detected):
        """서버에 좌석 상태 전송"""
        if not self.token:
            return
        
        now = datetime.now()
        
        # 쿨다운 체크
        if seat_number in self.last_send_time:
            time_diff = (now - self.last_send_time[seat_number]).total_seconds()
            if time_diff < self.COOLDOWN_SECONDS:
                return
        
        self.last_send_time[seat_number] = now
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'seat_number': seat_number,
            'person_detected': person_detected,
            'timestamp': now.isoformat()
        }
        
        try:
            res = requests.post(
                f'{self.HOST}/api_root/Seat/update_from_edge/',
                json=data,
                headers=headers,
                timeout=3
            )
            
            if res.status_code == 200:
                status_icon = '👤' if person_detected else '🪑'
                status_text = 'Person' if person_detected else 'Empty'
                print(f"✅ Seat {seat_number}: {status_icon} {status_text}")
            else:
                print(f"❌ Server error: {res.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout for Seat {seat_number}")
        except Exception as e:
            print(f"❌ Network error: {e}")
    
    def draw_rois(self, frame, seat_statuses):
        """ROI 박스 및 상태 그리기"""
        for seat_num, roi in self.seats.items():
            person_detected = seat_statuses.get(seat_num, False)
            
            # 색상 결정 (사람 있으면 빨강, 없으면 초록)
            color = (0, 0, 255) if person_detected else (0, 255, 0)
            
            # 박스 그리기
            cv2.rectangle(
                frame,
                (roi['x1'], roi['y1']),
                (roi['x2'], roi['y2']),
                color,
                3
            )
            
            # 텍스트 배경
            text = f"{roi['name']} {'OCCUPIED' if person_detected else 'EMPTY'}"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(
                frame,
                (roi['x1'], roi['y1'] - 30),
                (roi['x1'] + text_size[0] + 10, roi['y1']),
                color,
                -1
            )
            
            # 텍스트
            cv2.putText(
                frame,
                text,
                (roi['x1'] + 5, roi['y1'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
    
    def run(self):
        """웹캠으로 실시간 감지 시작"""
        print("\n🎥 Starting camera...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Cannot open camera")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("✅ Camera ready!")
        print("\n" + "="*50)
        print("📹 LIVE MONITORING")
        print("="*50)
        print("Press 'q' to quit")
        print("Press 's' to take screenshot")
        print("="*50 + "\n")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to grab frame")
                break
            
            frame_count += 1
            
            # YOLO 추론 (매 프레임마다)
            results = self.model(frame)
            
            # 각 좌석 상태 확인
            seat_statuses = {}
            for seat_num, roi in self.seats.items():
                person_detected = self.detect_person_in_roi(results, roi)
                seat_statuses[seat_num] = person_detected
                
                # 서버에 전송 (쿨다운 적용)
                self.send_to_server(seat_num, person_detected)
            
            # 화면에 ROI 표시
            annotated_frame = np.squeeze(results.render())
            self.draw_rois(annotated_frame, seat_statuses)
            
            # FPS 표시
            cv2.putText(
                annotated_frame,
                f"Frame: {frame_count}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            # 화면 표시
            cv2.imshow('SmartLib - Seat Detection', annotated_frame)
            
            # 키 입력 처리
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n👋 Shutting down...")
                break
            elif key == ord('s'):
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, annotated_frame)
                print(f"📸 Screenshot saved: {filename}")
        
        cap.release()
        cv2.destroyAllWindows()
        print("✅ System stopped.")


def main():
    print("""
    ╔═══════════════════════════════════════╗
    ║   SmartLib Seat Detection System      ║
    ║   도서관 자동 퇴실 감지 시스템               ║
    ╚═══════════════════════════════════════╝
    """)
    
    detector = SeatDetection()
    detector.run()


if __name__ == '__main__':
    main()