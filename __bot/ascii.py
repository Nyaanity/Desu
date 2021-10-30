import pyfiglet

class Ascii(object):
    """
    Convert strings to ascii art.
    """
    @staticmethod
    def str_to_ascii(text):
        """
        The default string-to-ascii conversion method.
        """
        c = 0
        cm = 6
        result = ''
        for i in text.lower():  # if text longer than 7 characters: place newline. Prevents bugs in sent discord message
            c += 1
            result += i
            if c >= cm:
                result += '\n'
                c = 0
        return pyfiglet.figlet_format(result)