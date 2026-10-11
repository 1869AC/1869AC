import re
import sys
from supabaseclient import supabase
supabaseUsernameRegex = re.compile(
    r"^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*$"
)


def cool_title():
    print("                                                            (   ) ") 
    print("  .---.    .--.      .--.      .--.    ___  ___   ___ .-.    | |_  ")
    print(" / .-, \  /    \    /    \    /    \  (   )(   ) (   )   \  (   __) ") 
    print("(__) ; | |  .-. ;  |  .-. ;  |  .-. ;  | |  | |   |  .-. .   | | ")
    print( " .'`  | |  |(___) |  |(___) | |  | |  | |  | |   | |  | |   | |")
    print(" / .'| | |  |      |  |      | |  | |  | |  | |   | |  | |   | |(   ) ") 
    print("| /  | | |  | ___  |  | ___  | |  | |  | |  | |   | |  | |   | | | | ")     
    print("; |  ; | |  '(   ) |  '(   ) | '  | |  | |  ; '   | |  | |   | ' | |")          
    print("' `-'  | '  `-' |  '  `-' |  '  `-' /  ' `-'  /   | |  | |   ' `-' ; ")      
    print("`.__.'_.  `.__,'    `.__,'    `.__.'    '.__.'   (___)(___)   `.__.")    

def account():   
    cool_title()                                                                                                             
    while True:
        print("login, signup, or continue as a guest?")
        print("(l/s/g): ")
        yor = input("").strip()
        if yor.lower() == "l":
            while True:
                print("\033[1;39;43m Login \033[0m")
                print("+====================================================+")
                print("\033[1;34m Username: \033[0m")
                username = input("").strip()
                print("\033[1;34m Password: \033[0m")
                password = input("").strip()
                real_username = username + "@gmail.com"
                try:
                    response = supabase.auth.sign_in_with_password(
                        {"email": real_username, 
                        "password": password,}
                    )
                    print("\033[1;35m Welcome back... \033[0m" + username)
                    return response.user.id
                except Exception as e:
                    print("Login failed:", e)
        elif yor.lower() == "s":
            print("\033[1;39;43m Sign Up \033[0m")
            print("+====================================================+")
            while True:
                print("\033[1;34m Username: \033[0m")
                username = input("").strip()
                real_username = username + "@gmail.com"
                if not supabaseUsernameRegex.match(username):
                    print("Sorry. No spaces, '@' or leading/trailing periods allowed")
                    continue
                ##check for duplicates
                valid = supabase.rpc("check_username", {
                    "user_name":username
                }).execute()
                if valid.data is True:
                    print("sorry. that username is already taken!")
                    continue
                else:
                    break

            while True:
                print("+====================================================+")
                print("\033[1;34m Password: \033[0m")
                password = input("").strip()
                if len(password) < 6:
                    print("Passwords must be atleast 6 characters long!")
                    continue
                try:
                    response = supabase.auth.sign_up(
                    {
                        "email": real_username, 
                        "password": password
                    }
                    )
                    print("\033[1;35m Account created! Logging you in... \033[0m")
                    return response.user.id
                except Exception as e:
                    print("\033[1;31m Signup error: \033[0m", e)

        elif yor.lower() == "g":
            print("\033[1;35m Continuing as a guest! \033[0m")
            return "guest"
        else:
            print("\033[1;35m Invalid option. \033[0m")
