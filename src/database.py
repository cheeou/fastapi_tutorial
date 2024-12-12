from services import UserService

user_service = UserService()

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": user_service.hash_password("password123"),
        "disabled": False,
    },
}