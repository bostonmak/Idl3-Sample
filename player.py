from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from google.protobuf.json_format import MessageToJson, Parse
import json

from . import app, db, hero_data
from .utils import *
from .migrations import PlayerModel, PlayerHeroesModel
from .action import create_server_response
from .proto.gen.action_pb2 import *
from .proto.gen.player_pb2 import *

@app.route("/player/get", methods = ["GET", "POST"])
def get_player():
    if request.method == "GET":
        users = PlayerModel.query.order_by(PlayerModel.id).all()
        json_users = []
        ret = ""
        for user in users:
            json_users.append(MessageToJson(user.as_proto()))
            ret += str(user.as_proto()) + "\n\n"
        return ret
    else:
        #user_id = request.args.get("id", default=-1, type=int)
        # For now, search by username
        print("begin get")
        username = request.args.get("username", default="test", type=str)
        email = request.args.get("email", default="test@idl3.com", type=str)
        player = db.session.execute(db.select(PlayerModel).filter_by(username=username)).scalar_one_or_none()
        does_exist = True
        resp = GetPlayerActionResponse()
        resp.does_exist = player is not None
        resp.player.CopyFrom(player.as_proto())
        ret = create_server_response(ResponseStatus.SUCCESS, ServerActions.GET_PLAYER, resp)
        return ret

# This will stay a get/create until we have a login flow to properly call these separately
@app.route("/player/create", methods = ["POST"])
def get_or_create_player():
    resp = CreatePlayerActionResponse()
    if request.method != "POST":
        ret = MessageToJson(
            create_server_response(ResponseStatus.BAD_METHOD, ServerActions.CREATE_PLAYER, resp))
    #user_id = request.args.get("id", default=-1, type=int)
    # For now, search by username
    print("begin create")
    username = request.args.get("username", default="test", type=str)
    email = request.args.get("email", default="test@idl3.com", type=str)
    player = db.session.execute(db.select(PlayerModel).filter_by(username=username)).scalar_one_or_none()
    if player is None:
        # New user needs to be created
        player = PlayerModel(username, email)
        new_hero = generate_hero_proto(1)
        new_hero.final_stats.attack = 123
        new_hero.final_stats.defense = 456
        new_hero.final_stats.max_hp = 789
        new_hero.final_stats.attack_speed = 0.5
        hero = PlayerHeroesModel(player.id, new_hero)
        player.heroes.append(hero)
        db.session.add(hero)
        db.session.add(player)
        db.session.commit()
        print("User " + email + " created")
        resp.player.CopyFrom(player.as_proto())
    else:
        #db_hero = db.session.execute(db.select(PlayerHeroesModel).filter_by(player_id=player.id)).scalar_one_or_none()
        player_proto = player.as_proto()
        #player_proto.heroes.append(db_hero.as_proto())
        resp.player.CopyFrom(player_proto)
        print("User " + email + " found")

    ret = create_server_response(ResponseStatus.SUCCESS, ServerActions.CREATE_PLAYER, resp)
    return ret

@app.route("/player/update_hero", methods = ["POST"])
def update_hero():
    resp = UpdateHeroActionResponse()
    if request.method != "POST":
        return MessageToJson(
            create_server_response(ResponseStatus.BAD_METHOD, ServerActions.UPDATE_HERO, resp))

    player_id = request.args.get("player_id")
    player = PlayerModel.query.filter_by(id=id).first()
    if player is None:
        return create_server_response(ResponseStatus.USER_NOT_FOUND, ServerActions.UPDATE_HERO, resp)

    player_proto = player.as_proto()
    hero_id = int(request.args.get("hero_id"))
    updated_hero = Parse(json.dumps(request.args.get("hero")), PlayerHeroProto())
    hero = hero_data.get(hero_id)
    if hero is None:
        return create_server_response(ResponseStatus.INVALID_ID, ServerActions.UPDATE_HERO, resp)

    player_proto.heroes[hero_id] = updated_hero
    resp.hero = updated_hero
    return create_server_response(ResponseStatus.SUCCESS, ServerActions.UPDATE_HERO, resp)
