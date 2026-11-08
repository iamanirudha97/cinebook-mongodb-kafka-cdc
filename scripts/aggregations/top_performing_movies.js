db.bookings.aggregate([
    {
        $match: { status: "CONFIRMED" }
    },
    {
        $group: {
            _id: "$movie_id",
            movie_title: { $first: "$movie_title" },
            total_bookings: { $sum: 1 },
            seats_sold: {
                $sum: { $size: "$seats" }
            },
            revenue: { $sum: "$amount" }
        }
    },
    {
        $sort: {
            seats_sold: -1,
            revenue: -1
        }
    },
    {
        $limit: 5
    },
    {
        $project: {
            _id: 0,
            movie_id: "$_id",
            movie_title: 1,
            total_bookings: 1,
            seats_sold: 1,
            revenue: 1
        }
    }
]);
