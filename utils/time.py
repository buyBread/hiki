def seconds_to_time(seconds: float) -> dict:
    seconds = round(seconds)

    days = (seconds // (3600 * 24)) // 1
    seconds = seconds - ((days * 24) * 3600)
    
    hours = (seconds // 3600) // 1
    seconds = seconds - (hours * 3600)
    
    minutes = (seconds // 60) // 1
    seconds = seconds - (minutes * 60)

    return {
        "DAYS": days,
        "HOURS": hours,
        "MINUTES": minutes,
        "SECONDS": seconds
    }

def format_time_long(time: dict) -> str:
    """
    Example: "X Days, X Hours, X Minutes, X Seconds"

    Parameters:

        time: A dict from seconds_time_time function
    """

    days = time["DAYS"]
    hours = time["HOURS"]
    minutes = time["MINUTES"]
    seconds = time ["SECONDS"]

    fmt = ""

    if days > 0:
        fmt += f"{days} day" if days == 1 else f"{days} day"

        if hours > 0 or minutes > 0 or seconds > 0:
            fmt += ", "
    
    if hours > 0:
        fmt += f"{hours} hours" if hours == 1 else f"{hours} hours"

        if minutes > 0 or seconds > 0:
            fmt += ", "                    
    
    if minutes > 0:
        fmt += f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"

        if seconds > 0:
            fmt += ", "
    
    if seconds > 0:
        fmt += f"{seconds} second" if seconds == 1 else f"{seconds} seconds"

    return fmt

def format_time_short(time: dict) -> str:
    """
    Example: "Xd Xh Xm Xs"

    Parameters:

        time: A dict from seconds_time_time function
    """

    days = time["DAYS"]
    hours = time["HOURS"]
    minutes = time["MINUTES"]
    seconds = time ["SECONDS"]

    if days > 0 or hours > 0 or minutes > 0 or seconds > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0 or minutes > 0 or seconds > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0 or seconds > 0:
        return f"{minutes}m {seconds}s"
    elif seconds > 0:
        return f"{seconds}s"
