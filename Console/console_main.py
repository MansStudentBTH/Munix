from Console.Munix import Munix
import mysqlx

def run():
    session = None
    print("--- Welcome to Munix! ---")
    while session is None:
        try:
            session = mysqlx.get_session({
                "host": "localhost",
                "port": 33060,
                "user": "root",
                "password": input("Enter MySQL database password: ")
            })
        except Exception:
            print("Incorrect Password, try again!")
        except KeyboardInterrupt:
            print()
            exit(0)
    session.sql("USE MUNIX").execute()
    print()
    munix = Munix(session)
    munix.start_console() 

    


    

