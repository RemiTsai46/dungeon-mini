from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableDict, MutableList
import traceback
 
app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/playerdata.db' # create playerdata.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Turns off heavy overhead tracking
#URI = universal resource identifier
db = SQLAlchemy(app) # create db object

class User(db.Model):
    # primary_key -> defines row id
    # length -> str length max limit
    # nullable = False -> can't be null
    # unique = True -> values are different among all rows

    guild_id: int = db.Column(db.BigInteger,primary_key=True)
    user_id: int = db.Column(db.BigInteger, primary_key=True)
    elynn: int = db.Column(db.Integer, nullable=False, default=0)
    azure_dust: int = db.Column(db.Integer, nullable=False, default=0)
    azure_stone:int = db.Column(db.Integer, nullable=False, default=0)
    bsc_element_shard: int = db.Column(db.Integer, nullable=False, default=0)
    adv_element_shard: int = db.Column(db.Integer, nullable=False, default=0)
    mst_element_shard: int = db.Column(db.Integer, nullable=False, default=0)
    spirit_crystal: int = db.Column(db.Integer, nullable=False, default=0)
    curr_room: int = db.Column(db.Integer, nullable=False, default=1)
    curr_level: int = db.Column(db.Integer, nullable=False, default=1) # the level the user will be in when start
    # description = db.Column(db.String(length=100), nullable=False)

    # 4 Equipped characters. Stores a flat array: [1, 2, 3, 4]
    equipped_characters = db.Column(MutableList.as_mutable(db.JSON), default=list)

    # All owned characters. Stores a dictionary mapping ID -> stats:
    # {
    #   "1": {"level": 55, "grade": 4},
    #   "4": {"level": 1, "grade": 1}
    # }
    owned_characters = db.Column(MutableDict.as_mutable(db.JSON), default=dict)

    def __repr__(self):
        return f'<User {self.user_id} in Guild {self.guild_id}>' # output when printed
    


# --- STARTUP CHECK ---
def init_database():
    """Checks if the DB file exists, creates it if missing. Run this in main.py"""
    with app.app_context():
        db.create_all()
        print("Database structure checked/initialized.")

# --- PROFILE MANAGEMENT FUNCTIONS ---
def get_player_data(guild_id: int, user_id: int):
    try:
        with app.app_context():
            player = User.query.filter_by(guild_id=guild_id, user_id=user_id).one_or_none()
            if player is None:
                player = User(
                    guild_id=guild_id,
                    user_id=user_id,
                    equipped_characters = [1],
                    owned_characters={
                        "1": {"level": 1, "grade": 1},
                    }
                )
                db.session.add(player)
                db.session.commit()
                # Merge back into session to safely return the object state
            db.session.refresh(player)
            return player
    except Exception as e:
        print("[DB ERROR] Something went wrong inside get_player_data!")
        # This forces the full error stack trace to print in your console
        traceback.print_exc() 
        return None

# # --- PROFILE MANAGEMENT FUNCTIONS ---
# def get_or_create_user(guild_id: int, user_id: int):
#     """Fetches a user profile or creates a default one if they are new."""
#     with app.app_context():
#         user = User.query.filter_by(guild_id=guild_id, user_id=user_id).first()
#         if not user:
#             user = User(
#                 guild_id=guild_id,
#                 user_id=user_id,
#                 equipped_characters=[101],
#                 owned_characters={"101": {"level": 1, "grade": 1}}
#             )
#             db.session.add(user)
#             db.session.commit()
#             # Merge back into session to safely return the object state
#             db.session.refresh(user) 
#         return user

# def update_character_level(guild_id: int, user_id: int, char_id: str, new_level: int):
#     """Safely upgrades a character's level inside the JSON dictionary."""
#     with app.app_context():
#         user = User.query.filter_by(guild_id=guild_id, user_id=user_id).first()
#         if user and char_id in user.owned_characters:
#             user.owned_characters[char_id]["level"] = new_level
#             db.session.commit()
#             return True
#         return False