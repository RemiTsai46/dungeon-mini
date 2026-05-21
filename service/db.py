from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
 
app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///playerdata.db'
				# create playerdata.db in current dir
#URI = universal resource identifier
db = SQLAlchemy(app) # create db object

class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    guild = db.Column(db.BigInteger,primary_key=True)
    elynn = db.Column(db.Integer, nullable=False)
    azure_dust = db.Column(db.Integer, nullable=False)
    azure_stone = db.Column(db.Integer, nullable=False)
    bsc_element_shard = db.Column(db.Integer, nullable=False)
    adv_element_shard = db.Column(db.Integer, nullable=False)
    mst_element_shard = db.Column(db.Integer, nullable=False)

    # description = db.Column(db.String(length=100), nullable=False)

    # primary_key -> 用來定義每筆資料的 id
    # length -> 該欄位長度上限
    # nullable = False -> 該欄位不能留空
    # unique = True -> 不同筆資料間該欄位的內容不能重複（例如：name 必須是獨一無二的）