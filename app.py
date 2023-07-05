#!/usr/bin/env python

import asyncio
import itertools
import json

import websockets

from connect4 import PLAYER1, PLAYER2, Connect4


import secrets


JOIN = {}

# event_error
async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


# event_play
async def play(websocket,player,row,column):
    event={
        "type":"play",
        "player":player,
        "row":row,
        "column":column
    }
    await websocket.send(json.dumps(event))


# event_win
async def win(websocket,winner):
    event = {
        "type": "win",
        "player": winner
    }
    await websocket.send(json.dumps(event))


#operation_move
async def move(websocket,game,player,connected):
    async for message in websocket:
        print(message)
        event = json.loads(message)
        assert event["type"] == "play"
        column = event["column"] 
        try:
            # Play the move.
            row = game.play(player, column)
        except RuntimeError as exc:
            # Send an "error" event if the move was illegal.
            await error(websocket,str(exc))
            continue

        # Send a "play" event to update the UI.
        await play(websocket,player,row,column)

        # If move is winning, send a "win" event.
        if game.winner is not None:
            await win(websocket,game.winner)


async def start(websocket):
    # Initialize a Connect Four game, the set of WebSocket connections
    # receiving moves from this game, and secret access token.
    game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    # join_key=1022
    JOIN[join_key] = game, connected

    try:
        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        # Temporary - for testing.
        print("first player started game", id(game))
        print(JOIN)
        await move(websocket,game,PLAYER1,connected)

    finally:
        del JOIN[join_key]


async def join(websocket, join_key):
    # Find the Connect Four game.
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)
    try:

        # Temporary - for testing.
        print("second player joined game", id(game))
        await move(websocket,game,PLAYER2,connected)


    finally:
        connected.remove(websocket)


async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # Second player joins an existing game.
        await join(websocket, event["join"])
    else:
        # First player starts a new game.
        await start(websocket)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())