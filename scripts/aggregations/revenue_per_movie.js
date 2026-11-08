db.bookings.aggregate([
    {
        $match: { status: "CONFIRMED" }
    },
    {
        $group: {
            _id: "$movie_id",
            movie_title: { $first: "$movie_title" },
            total_revenue: { $sum: "$amount" },
            total_bookings: { $sum: 1 },
            total_seats_sold: {
                $sum: { $size: "$seats" }
            }
        }
    },
    {
        $project: {
            _id: 0,
            movie_id: "$_id",
            movie_title: 1,
            total_revenue: 1,
            total_bookings: 1,
            total_seats_sold: 1
        }
    },
    {
        $sort: { total_revenue: -1 }
    }
]);
