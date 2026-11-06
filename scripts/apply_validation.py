"""Create the five CineBook collections and apply MongoDB $jsonSchema validation.



Uses `docs/data_model.md` as the source of truth.

- Creates collections if they do not exist yet.

- Uses `collMod` to update validators in place if collections already exist.

- Never drops collections or deletes documents.

"""



import os

from dotenv import load_dotenv

from pymongo import MongoClient



load_dotenv()



# Use MONGODB_ADMIN_URI for administrative operations (createCollection / collMod).

# Never print or log the connection URI.

admin_uri = os.getenv("MONGODB_ADMIN_URI")
if not admin_uri:
    raise SystemExit("Set MONGODB_ADMIN_URI in .env before running this script.")

db_name = os.getenv("MONGODB_DB", "cinebook")



INTEGER_TYPES = ["int", "long"]

NUMBER_TYPES = ["int", "long", "double", "decimal"]



# ---------------------------------------------------------------------------

# MongoDB $jsonSchema definitions for all 5 collections (docs/data_model.md §2)

# ---------------------------------------------------------------------------

VALIDATORS = {

    "movies": {

        "$jsonSchema": {

            "bsonType": "object",

            "required": [

                "_id",

                "title",

                "language",

                "genres",

                "duration_min",

                "certification",

                "release_date",

                "cities",

            ],

            "additionalProperties": False,

            "properties": {

                "_id": {"bsonType": "string", "pattern": "^MOV-[A-Z0-9-]+$"},

                "title": {"bsonType": "string", "minLength": 1},

                "language": {"bsonType": "string", "minLength": 1},

                "genres": {

                    "bsonType": "array",

                    "minItems": 1,

                    "items": {"bsonType": "string", "minLength": 1},

                },

                "duration_min": {"bsonType": INTEGER_TYPES, "minimum": 1},

                "certification": {"bsonType": "string", "minLength": 1},

                "release_date": {"bsonType": "date"},

                "cities": {

                    "bsonType": "array",

                    "minItems": 1,

                    "items": {"bsonType": "string", "minLength": 1},

                },

            },

        }

    },

    "theaters": {

        "$jsonSchema": {

            "bsonType": "object",

            "required": ["_id", "name", "city", "screens"],

            "additionalProperties": False,

            "properties": {

                "_id": {"bsonType": "string", "pattern": "^THR-[A-Z0-9-]+$"},

                "name": {"bsonType": "string", "minLength": 1},

                "city": {"bsonType": "string", "minLength": 1},

                # Embedded screen layout templates (never store live availability here)

                "screens": {

                    "bsonType": "array",

                    "minItems": 1,

                    "items": {

                        "bsonType": "object",

                        "required": [

                            "screen_id",

                            "name",

                            "rows",

                            "seats_per_row",

                            "categories",

                        ],

                        "additionalProperties": False,

                        "properties": {

                            "screen_id": {"bsonType": "string", "minLength": 1},

                            "name": {"bsonType": "string", "minLength": 1},

                            "rows": {

                                "bsonType": "array",

                                "minItems": 1,

                                "items": {"bsonType": "string", "pattern": "^[A-Z]$"},

                            },

                            "seats_per_row": {"bsonType": INTEGER_TYPES, "minimum": 1},

                            "categories": {

                                "bsonType": "object",

                                "minProperties": 1,

                                "additionalProperties": {

                                    "bsonType": "string",

                                    "minLength": 1,

                                },

                            },

                        },

                    },

                },

            },

        }

    },

    "shows": {

        "$jsonSchema": {

            "bsonType": "object",

            "required": [

                "_id",

                "movie_id",

                "theater_id",

                "screen_id",

                "city",

                "start_time",

                "status",

                "prices",

                "seats_total",

                "seats_available",

                "seats",

            ],

            "additionalProperties": False,

            "properties": {

                "_id": {"bsonType": "string", "pattern": "^SHW-[0-9]{6}$"},

                "movie_id": {"bsonType": "string", "pattern": "^MOV-[A-Z0-9-]+$"},

                "theater_id": {"bsonType": "string", "pattern": "^THR-[A-Z0-9-]+$"},

                "screen_id": {"bsonType": "string", "minLength": 1},

                "city": {"bsonType": "string", "minLength": 1},

                "start_time": {"bsonType": "date"},

                "status": {"enum": ["SCHEDULED", "CANCELLED"]},

                "prices": {

                    "bsonType": "object",

                    "minProperties": 1,

                    "additionalProperties": {"bsonType": NUMBER_TYPES, "minimum": 0},

                },

                "seats_total": {"bsonType": INTEGER_TYPES, "minimum": 1},

                "seats_available": {"bsonType": INTEGER_TYPES, "minimum": 0},

                # Embedded per-show seat inventory enabling atomic single-document updates

                # Cross-field consistency (booking_id vs status and seat counts)
                # is checked in the service and consistency tests.
                "seats": {

                    "bsonType": "array",

                    "minItems": 1,

                    "items": {

                        "bsonType": "object",

                        "required": ["seat", "category", "status"],

                        "additionalProperties": False,

                        "properties": {

                            "seat": {

                                "bsonType": "string",

                                "pattern": "^[A-Z][0-9]{1,3}$",

                            },

                            "category": {"bsonType": "string", "minLength": 1},

                            "status": {"enum": ["AVAILABLE", "BOOKED"]},

                            "booking_id": {

                                "bsonType": "string",

                                "pattern": "^BKG-[0-9a-f]{32}$",

                            },

                        },

                    },

                },

            },

        }

    },

    "bookings": {

        "$jsonSchema": {

            "bsonType": "object",

            "required": [

                "_id",

                "idempotency_key",

                "show_id",

                "user_id",

                "seats",

                "amount",

                "status",

                "created_at",

                "movie_id",

                "movie_title",

                "theater_id",

                "screen_id",

                "city",

                "show_start_time",

                "price_breakdown",

            ],

            "additionalProperties": False,

            "properties": {

                "_id": {"bsonType": "string", "pattern": "^BKG-[0-9a-f]{32}$"},

                "idempotency_key": {

                    "bsonType": "string",

                    "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",

                },

                "show_id": {"bsonType": "string", "pattern": "^SHW-[0-9]{6}$"},

                "user_id": {"bsonType": "string", "pattern": "^USR-[0-9]{4}$"},

                "seats": {

                    "bsonType": "array",

                    "minItems": 1,

                    "items": {"bsonType": "string", "pattern": "^[A-Z][0-9]{1,3}$"},

                },

                "amount": {"bsonType": NUMBER_TYPES, "minimum": 0},

                "status": {"enum": ["CONFIRMED", "CANCELLED"]},

                "created_at": {"bsonType": "date"},

                "cancelled_at": {"bsonType": "date"},

                "movie_id": {"bsonType": "string", "pattern": "^MOV-[A-Z0-9-]+$"},

                "movie_title": {"bsonType": "string", "minLength": 1},

                "theater_id": {"bsonType": "string", "pattern": "^THR-[A-Z0-9-]+$"},

                "screen_id": {"bsonType": "string", "minLength": 1},

                "city": {"bsonType": "string", "minLength": 1},

                "show_start_time": {"bsonType": "date"},

                # Embedded point-in-time price snapshot per booked seat

                "price_breakdown": {

                    "bsonType": "array",

                    "minItems": 1,

                    "items": {

                        "bsonType": "object",

                        "required": ["seat", "category", "price"],

                        "additionalProperties": False,

                        "properties": {

                            "seat": {

                                "bsonType": "string",

                                "pattern": "^[A-Z][0-9]{1,3}$",

                            },

                            "category": {"bsonType": "string", "minLength": 1},

                            "price": {"bsonType": NUMBER_TYPES, "minimum": 0},

                        },

                    },

                },

            },

        }

    },

    "users": {

        "$jsonSchema": {

            "bsonType": "object",

            "required": ["_id", "name", "email", "city", "created_at"],

            "additionalProperties": False,

            "properties": {

                "_id": {"bsonType": "string", "pattern": "^USR-[0-9]{4}$"},

                "name": {"bsonType": "string", "minLength": 1},

                "email": {"bsonType": "string", "minLength": 3},

                "city": {"bsonType": "string", "minLength": 1},

                "created_at": {"bsonType": "date"},

            },

        }

    },

}





def apply_validators() -> None:
    client = MongoClient(admin_uri, serverSelectionTimeoutMS=10000, tz_aware=True)
    try:
        client.admin.command("ping")
        db = client[db_name]
        existing = set(db.list_collection_names())
        for name, validator in VALIDATORS.items():
            try:
                if name not in existing:
                    db.create_collection(
                        name,
                        validator=validator,
                        validationLevel="strict",
                        validationAction="error",
                    )
                    print(f"CREATED: {name}")
                else:
                    db.command({
                        "collMod": name,
                        "validator": validator,
                        "validationLevel": "strict",
                        "validationAction": "error",
                    })
                    print(f"UPDATED: {name}")
            except Exception as exc:
                raise RuntimeError(f"Failed to configure collection '{name}'") from exc
    finally:
        client.close()


if __name__ == "__main__":
    apply_validators()