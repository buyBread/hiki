from discord import ActivityType

embed_color = {
    "DEFAULT": 0x2F3136,
    "RED": 0xff4040,
    "DARK_RED": 0xa30d0d,
    "CHERRY": 0xb33b3b,
    "TANGERINE": 0xff9940,
    "ORANGE": 0xff7940,
    "YELLOW": 0xffe75e,
    "ACID": 0xd1ff29,
    "LIME": 0x95ff14,
    "GREEN": 0x93ff61,
    "DARK_GREEN": 0x53b33b,
    "CYAN": 0x70ffc1,
    "LIGHT_BLUE": 0x80fdff,
    "INK": 0x5b5df0,
    "BLUE": 0x5ba8f0,
    "DARK_BLUE": 0x2527b8,
    "PURPLE": 0x7a3ce6,
    "DARK_PURPLE": 0x582ba6,
    "MAGENTA": 0xe136ff,
    "PINK": 0xec80ff,
    "LIGHT_PINK": 0xffabe9
}

member_data = {
    "EXP": 0,
    "LEVEL": 1,
    "WARNINGS": 2,
    "EMOJI": 3,
    "COLOR": 4,
    "DESCRIPTION": 5,
    "DJ_STATUS": 6
}

activity_type = {
    "PLAYING": ActivityType.playing,
    "WATCHING": ActivityType.watching,
    "STREAMING": ActivityType.streaming,
    "LISTENING": ActivityType.listening,
    "COMPETING": ActivityType.competing,
    "CUSTOM": ActivityType.custom,
    "UNKNOWN": ActivityType.unknown
}
