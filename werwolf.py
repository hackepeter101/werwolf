try:
    from pyfiglet import Figlet
except ImportError:
    Figlet = None


# ... other code ...

def role_art_text(role_name):
    if Figlet:
        try:
            role_art = Figlet(font='dos_rebel').renderText(role_name)
            return blueText(role_art)
        except Exception:
            pass
    return role_name.upper()  

# ... other code ...