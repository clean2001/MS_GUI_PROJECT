def add_direction_to_table(origin_table : list, is_ascending: list) -> list:
    direction_table = []
    for i in range(len(origin_table)):
        direction_emoji = "🔼" if is_ascending[i] else "🔽"
        direction_table.append(origin_table[i] + direction_emoji)
    
    return direction_table