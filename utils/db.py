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
    __tablename__ = 'users'
    # primary_key -> defines row id
    # length -> str length max limit
    # nullable = False -> can't be null
    # unique = True -> values are different among all rows

    guild_id: int = db.Column(db.BigInteger,primary_key=True)
    user_id: int = db.Column(db.BigInteger, primary_key=True)

    # currencies
    elynn: int = db.Column(db.Integer, nullable=False, default=0)
    azure_dust: int = db.Column(db.Integer, nullable=False, default=0)
    azure_stone:int = db.Column(db.Integer, nullable=False, default=0)
    bsc_element_shard: int = db.Column(db.Integer, nullable=False, default=0)
    adv_element_shard: int = db.Column(db.Integer, nullable=False, default=0)
    mst_element_shard: int = db.Column(db.Integer, nullable=False, default=0)
    spirit_crystal: int = db.Column(db.Integer, nullable=False, default=0)

    # States can be: 'idle', 'dungeon', 'raid', 'pvp'
    curr_state: str = db.Column(db.String, nullable=False, default="idle")
    curr_room: int = db.Column(db.Integer, nullable=False, default=1)
    curr_level: int = db.Column(db.Integer, nullable=False, default=1) # the level the user will be in when start

    # equipped characters stored as list, example [1, 2, 3, 4]
    equipped_souls = db.Column(
        MutableList.as_mutable(db.JSON),
        default=lambda: [None, None, None, None]
    )

    # owned characters/relics and its properties, stored as dict:
    # {
    #   301: {"level": 55, "grade": 4},
    #   304: {"level": 1, "grade": 1}
    # }
    # "level" = character level = relic mastery
    owned_souls = db.Column(MutableDict.as_mutable(db.JSON), default=dict)
    # owned_relics = db.Column(MutableDict.as_mutable(db.JSON), default=dict)

    def __repr__(self):
        return f'<User {self.user_id} in Guild {self.guild_id}>' # output when printed
    
CURRENCY_EMOJIS = {
    "elynn": "<:elynn:1487375063996170283>",              # Standard emoji fallback
    "azure_dust": "<:azure_dust:1487824468662419506>",  # Custom emoji format: <:name:id>
    "azure_stone": "<:azure_stone:1487825302196453516>",
    "spirit_crystal": "<spirit_crystal:1490707913814048929>"
}

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
                    equipped_souls = [1],
                    owned_souls={
                        "1": {"level": 1, "grade": 1},
                    }
                )
                db.session.add(player)
                db.session.commit()
            # let session know the new user to return normally
            db.session.refresh(player)
            return player
    except Exception as e:
        print("[DB ERROR] Something went wrong inside get_player_data!")
        traceback.print_exc() 
        return None

def is_player_idle(guild_id: int, user_id: int) -> bool:
    """Returns True if the player is free to start an activity, False if busy."""
    player = get_player_data(guild_id,user_id)
    if player is None:
        return False
    return player.status == "idle"

def set_player_status(guild_id: int, user_id: int, new_status: str):
    """Updates the player's current activity state in the database."""
    player = get_player_data(guild_id, user_id)
    if player:
        player.status = new_status
        db.session.commit()  # Commits the status change to the DB immediately
        return True
    return False

# def update_character_level(guild_id: int, user_id: int, char_id: str, new_level: int):
#     """Safely upgrades a character's level inside the JSON dictionary."""
#     with app.app_context():
#         user = User.query.filter_by(guild_id=guild_id, user_id=user_id).first()
#         if user and char_id in user.owned_characters:
#             user.owned_characters[char_id]["level"] = new_level
#             db.session.commit()
#             return True
#         return False

# +----------------+
# |   ADMIN ZONE   |
# +----------------+
def admin_modify_material(guild_id: int, user_id: int, material:str, operation: str, amount: int):
    """
    Strictly for admin commands to force-change a balance.

    :param guild_id: Guild ID of which guild the message is in.
    :param user_id: User ID of the message sender.
    :param material: The material you want to modify.
    :param operation: Operation of the modification, should only be `add`, `remove`, or `set`.
    :param amount: Amount to modify.
    """
    user = get_player_data(guild_id,user_id)
    if user is None:
        return False, "[DB ERROR] Something went wrong inside get_player_data!"
        
    # Get the current balance of the selected material dynamically
    cur_bal = getattr(user, material, 0)
    emoji = CURRENCY_EMOJIS.get(material, "🪙") # Fallback to a generic coin

    if operation == "add":
        setattr(user, material, cur_bal + amount)
    elif operation == "remove":
        if user.elynn < amount:
            return False, f"Player only has {emoji} {cur_bal} {material.replace('_', ' ').title()}."
        setattr(user, material, cur_bal - amount)
    else: # "set"
        setattr(user, material, amount)

    db.session.commit()

    new_bal_str = f"{emoji} {getattr(user, material)}"

    return True, new_bal_str
