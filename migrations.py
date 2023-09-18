
from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from google.protobuf.json_format import MessageToDict

from . import config
from . import app, db
from .utils import *
from .proto.gen.player_pb2 import *

class PlayerModel(db.Model):
    __tablename__ = "player"

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String())
    email = db.Column(db.String())
    heroes = db.relationship("PlayerHeroesModel", backref="player")
    inventory = db.Column(db.ARRAY(db.LargeBinary()))

    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.inventory = []

    def __repr__(self):
        return f"Player {self.username}, {self.id}"

    def as_proto(self):
        proto = PlayerProto()
        proto.id = self.id
        proto.username = self.username
        proto.email = self.email
        for hero in self.heroes:
            hero_proto = PlayerHeroProto()
            hero_proto = generate_hero_proto(hero.hero_id, MessageToDict(self.heroes[0].as_proto(), preserving_proto_field_name=True))
            proto.heroes.append(hero_proto)
        return proto


class PlayerHeroesModel(db.Model):
    __tablename__ = "player_heroes"

    id = db.Column(db.Integer(), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(PlayerModel.id))
    hero_id = db.Column(db.Integer())
    level = db.Column(db.Integer())
    attack = db.Column(db.Integer())
    defense = db.Column(db.Integer())
    max_hp = db.Column(db.Integer())
    attack_speed = db.Column(db.Float())
    gear = inventory = db.Column(db.ARRAY(db.LargeBinary()))

    def __init__(self, player_id, hero_proto):
        self.player_id = player_id
        self.hero_id = hero_proto.id
        self.level = hero_proto.level
        self.attack = hero_proto.final_stats.attack
        self.defense = hero_proto.final_stats.defense
        self.max_hp = hero_proto.final_stats.max_hp
        self.attack_speed = hero_proto.final_stats.attack_speed
        self.gear = []

    def __repr__(self):
        return f"Player {self.username}"

    def as_proto(self):
        proto = PlayerHeroProto()
        proto.id = self.hero_id
        proto.level = self.level
        proto.final_stats.attack = self.attack
        proto.final_stats.defense = self.defense
        proto.final_stats.max_hp = self.max_hp
        proto.final_stats.attack_speed = self.attack_speed
        return proto
