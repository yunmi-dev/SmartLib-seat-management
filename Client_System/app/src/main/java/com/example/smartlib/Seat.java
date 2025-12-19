package com.example.smartlib;

public class Seat {
    private int seatNumber;
    private String status;
    private String userName;

    public Seat(int seatNumber, String status, String userName) {
        this.seatNumber = seatNumber;
        this.status = status;
        this.userName = userName;
    }

    public int getSeatNumber() {
        return seatNumber;
    }

    public String getStatus() {
        return status;
    }

    public String getUserName() {
        return userName;
    }

    public String getStatusKorean() {
        switch (status) {
            case "empty": return "사용 가능";
            case "occupied": return "사용 중";
            case "reserved": return "예약됨";
            default: return "알 수 없음";
        }
    }
}