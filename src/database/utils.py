from .database_manager import DatabaseManager
from src.data_acquisition import FACEITBot, DataMuncher, scrap_championship

def save_championship(championship_id, database_path = "data/overwatch_data.db"):
    bot = FACEITBot()
    muncher = DataMuncher()
    db_manager = DatabaseManager(database_path)
    match_ids = scrap_championship('3976270f-6138-4289-81d9-998927cce41e', bot)

    counter = 0
    last_match_stats = []
    for match_id in match_ids:
        print(match_id)
        bot.query('matches', f'{match_id}')
        raw_details = bot.data
        bot.query('matches', f'{match_id}/stats')
        raw_stats = bot.data

        if raw_stats == last_match_stats:
            counter += 1
            print("match stats unavailable, skipping match")
            continue

        last_match_stats = raw_stats

        muncher.add_data(raw_details, raw_stats)
        muncher.extract_all()
        muncher.prepare_data()

        counter += 1
        print(f"{counter} out of {len(match_ids)} processed.")

    muncher.rename_validate()

    db_manager.setup_connection()

    db_manager.upload_match_details(muncher.matches_df)

    db_manager.upload_player_data(muncher.player_dfs)

    return muncher, db_manager