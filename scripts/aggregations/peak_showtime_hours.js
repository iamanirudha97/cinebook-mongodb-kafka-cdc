db.bookings.aggregate([
    {
        $match: { status: "CONFIRMED" }
    },
    {
        $group: {
            _id: {
                $hour: {
                    date: "$show_start_time",
                    timezone: "UTC"
                }
            },
            total_bookings: { $sum: 1 },
            total_seats_sold: {
                $sum: { $size: "$seats" }
            },
            total_revenue: { $sum: "$amount" }
        }
    },
    {
        $project: {
            _id: 0,
            hour: "$_id",
            total_bookings: 1,
            total_seats_sold: 1,
            total_revenue: 1
        }
    },
    {
        $sort: {
            total_seats_sold: -1,
            hour: 1
        }
    }
]);
