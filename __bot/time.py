time_dict = {"s": 1, "m": 60, "h": 3600,
             "d": 86400, "w": 604800, "y": 31556952}


class TimeConverter(object):
    """
    Useful time converter for this bot.
    """

    @staticmethod
    def _to_seconds(time):
        """
        Convert time values like 1d or 12h into seconds.
        Can take s, m, h, d, w
        """
        try:
            return int(time[:-1]) * time_dict[time[-1]]
        except:
            raise ValueError('Can not convert "{}" into seconds'.format(time))