db.shows.aggregate([
    {
        $project: {
            _id: 0,
            show_id: "$_id",
            movie_id: 1,
            city: 1,
            seats_total: 1,
            seats_available: 1,
            seats_booked: {
                $subtract: ["$seats_total", "$seats_available"]
            },
            occupancy_percentage: {
                $round: [
                    {
                        $multiply: [
                            {
                                $divide: [
                                    {
                                        $subtract: [
                                            "$seats_total",
                                            "$seats_available"
                                        ]
                                    },
                                    "$seats_total"
                                ]
                            },
                            100
                        ]
                    },
                    2
                ]
            }
        }
    },
    {
        $sort: {
            occupancy_percentage: -1,
            show_id: 1
        }
    }
]);
