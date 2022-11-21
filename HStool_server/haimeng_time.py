import time


def changelocaltimeToSqldatetime():
    pytime = time.localtime()
    tm_year,tm_mon,tm_mday, tm_hour, tm_min, tm_sec = pytime[0], pytime[1], pytime[2], pytime[3], pytime[4], pytime[5]
    return f'{tm_year}-{tm_mon:02}-{tm_mday:02} {tm_hour:02}:{tm_min:02}:{tm_sec:02}'


def change_local_time_to_str():
    local_time = time.localtime()
    tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec = local_time[0], local_time[1], local_time[2], local_time[3], local_time[4], local_time[5]
    return f'{tm_year}-{tm_mon}-{tm_mday}_{tm_hour}-{tm_min}-{tm_sec}'


def get_china_time():
    local_time = time.localtime()
    tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec = local_time[0], local_time[1], local_time[2], local_time[3], local_time[4], local_time[5]
    return f"{tm_year:02}年{tm_mon:02}月{tm_mday:02}日 {tm_hour:02}:{tm_min:02}:{tm_sec:02}"