import time


def scrap_championship(championship_id, faceit_bot):
    '''
    Finds all game ids in a championship.
    Accesses FaceIT API to find game ids for later use.

    Args:
    championship_id (str): id of the championship to scrap
    FaceIT_Bot (FACEITBot()): Bot to access database with

    Returns:
    list of game ids
    '''
    game_ids = set()
    offset = 0
    while (True):
        # query championship data
        faceit_bot.query("championships", f"{championship_id}/matches", offset=offset, limit=100)
        # get data from downloaded dict
        game_ids_temp = {game.get("match_id") for game in faceit_bot.data.get("items")}
        # only include ids that are in the new list, but not in the complete list
        new_ids = game_ids_temp - game_ids
        game_ids.update(new_ids)
        # if new_ids is empty --> True
        if not new_ids:
            break
        # add amount of recorded ids this cycle to offset
        offset += len(new_ids)
        time.sleep(2)
        print(f"Cycle completed. {len(game_ids)} ids recorded.")
    return game_ids
