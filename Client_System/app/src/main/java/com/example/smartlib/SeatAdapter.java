package com.example.smartlib;

import android.content.Context;
import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;
import java.util.List;

public class SeatAdapter extends BaseAdapter {
    private Context context;
    private List<Seat> seatList;

    public SeatAdapter(Context context, List<Seat> seatList) {
        this.context = context;
        this.seatList = seatList;
    }

    @Override
    public int getCount() {
        return seatList.size();
    }

    @Override
    public Object getItem(int position) {
        return seatList.get(position);
    }

    @Override
    public long getItemId(int position) {
        return position;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        if (convertView == null) {
            LayoutInflater inflater = LayoutInflater.from(context);
            convertView = inflater.inflate(R.layout.item_seat, parent, false);
        }

        TextView tvSeatNumber = convertView.findViewById(R.id.tvSeatNumber);
        View seatBackground = convertView.findViewById(R.id.seatBackground);

        Seat seat = seatList.get(position);
        tvSeatNumber.setText(String.valueOf(seat.getSeatNumber()));

        switch (seat.getStatus()) {
            case "empty":
                seatBackground.setBackgroundColor(Color.parseColor("#4CAF50"));
                break;
            case "occupied":
                seatBackground.setBackgroundColor(Color.parseColor("#F44336"));
                break;
            case "reserved":
                seatBackground.setBackgroundColor(Color.parseColor("#FF9800"));
                break;
            default:
                seatBackground.setBackgroundColor(Color.parseColor("#9E9E9E"));
                break;
        }

        return convertView;
    }
}