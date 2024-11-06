from collections import defaultdict

map_types_open_NA_3 = {
    "0x08000000000007E2": "Control",
    "0x0800000000000662": "Control",
    "0x08000000000004B7": "Control",
    "0x0800000000000EC0": "Control",
    "0x080000000000075E": "Hybrid",
    "0x080000000000068D": "Hybrid",
    "0x08000000000000D4": "Hybrid",
    "0x0800000000000938": "Hybrid",
    "0x0800000000000827": "Escort",
    "0x08000000000002C3": "Escort",
    "0x0800000000000756": "Escort",
    "0x0800000000000C85": "Escort",
    "0x0800000000000871": "Escort",
    '0x0800000000000184': 'Escort',
    '0x0800000000000B4C': 'Hybrid',
    '0x080000000000066D': 'Control'

}

map_type_dict = defaultdict(lambda: "Unknown", map_types_open_NA_3)

map_names_open_NA_3 = {
    "0x08000000000007E2": "Busan",
    "0x0800000000000662": "Lijang Tower",
    "0x08000000000004B7": "Nepal",
    "0x0800000000000EC0": "Samoa",
    "0x080000000000075E": "Blizzard World",
    "0x080000000000068D": "Eichenwalde",
    "0x08000000000000D4": "King's Row",
    "0x0800000000000938": "Paraiso",
    "0x0800000000000827": "Circuit Royal",
    "0x08000000000002C3": "Dorado",
    "0x0800000000000756": "Junkertown",
    "0x0800000000000C85": "Shambali Monastery",
    '0x0800000000000871': 'Rialto',
    '0x0800000000000184': 'Watchpoint Gibraltar',
    '0x0800000000000B4C': 'Midtown',
    '0x080000000000066D': 'Ilios'

}
map_name_dict = defaultdict(lambda: "Unknown", map_names_open_NA_3)
