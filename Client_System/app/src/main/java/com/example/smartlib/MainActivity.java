package com.example.smartlib;

import android.os.Bundle;
import android.os.Handler;
import android.widget.GridView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.Volley;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    // 로컬 테스트용
    private static final String API_URL = "http://10.0.2.2:8000/api_root/Seat/";
    // PythonAnywhere 배포 후: "https://yunmee2765.pythonanywhere.com/api_root/Seat/";

    private GridView gridViewSeats;
    private TextView tvTotalSeats, tvOccupied, tvAvailable;
    private SeatAdapter seatAdapter;
    private List<Seat> seatList;
    private RequestQueue requestQueue;
    private Handler handler;
    private Runnable refreshRunnable;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        gridViewSeats = findViewById(R.id.gridViewSeats);
        tvTotalSeats = findViewById(R.id.tvTotalSeats);
        tvOccupied = findViewById(R.id.tvOccupied);
        tvAvailable = findViewById(R.id.tvAvailable);

        seatList = new ArrayList<>();
        seatAdapter = new SeatAdapter(this, seatList);
        gridViewSeats.setAdapter(seatAdapter);

        requestQueue = Volley.newRequestQueue(this);

        gridViewSeats.setOnItemClickListener((parent, view, position, id) -> {
            Seat seat = seatList.get(position);
            Toast.makeText(this,
                    "좌석 " + seat.getSeatNumber() + "\n상태: " + seat.getStatusKorean(),
                    Toast.LENGTH_SHORT).show();
        });

        handler = new Handler();
        refreshRunnable = new Runnable() {
            @Override
            public void run() {
                fetchSeats();
                handler.postDelayed(this, 5000);
            }
        };

        fetchSeats();
        handler.post(refreshRunnable);
    }

    private void fetchSeats() {
        JsonArrayRequest request = new JsonArrayRequest(
                Request.Method.GET,
                API_URL,
                null,
                response -> {
                    seatList.clear();
                    try {
                        for (int i = 0; i < response.length(); i++) {
                            JSONObject obj = response.getJSONObject(i);
                            int seatNumber = obj.getInt("seat_number");
                            String status = obj.getString("status");
                            String userName = obj.optString("user_name", "");
                            seatList.add(new Seat(seatNumber, status, userName));
                        }
                        seatAdapter.notifyDataSetChanged();
                        updateStats();
                    } catch (Exception e) {
                        e.printStackTrace();
                        Toast.makeText(this, "데이터 파싱 오류", Toast.LENGTH_SHORT).show();
                    }
                },
                error -> Toast.makeText(this, "서버 연결 실패: " + error.getMessage(), Toast.LENGTH_SHORT).show()
        );
        requestQueue.add(request);
    }

    private void updateStats() {
        int total = seatList.size();
        int occupied = 0;
        for (Seat seat : seatList) {
            if (seat.getStatus().equals("occupied")) {
                occupied++;
            }
        }
        int available = total - occupied;

        tvTotalSeats.setText("전체: " + total);
        tvOccupied.setText("사용 중: " + occupied);
        tvAvailable.setText("사용 가능: " + available);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacks(refreshRunnable);
    }
}