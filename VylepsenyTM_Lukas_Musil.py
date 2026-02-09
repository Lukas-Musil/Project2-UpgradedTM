import mysql.connector

db_host = "localhost"
db_user = "root"
db_password = "1111"
db_name = "db_ukoly"

def pripojeni_db():
    """Vytvoří připojení k databázi"""
    try:
        conn = mysql.connector.connect(
            host = db_host,
            user = db_user,
            password = db_password,
            database = db_name
        )
        cursor = conn.cursor()
        print("\nPřipojení k databázi bylo úspěšné.\n")
        return conn,cursor
    except mysql.connector.Error as err:
        print(f"Chyba při připojování: {err}\n")
        return None,None

def vytvoreni_tabulky(cursor):
    """Vytvoří tabulku pokud již neexistuje"""
    try:
        cursor.execute('''
            create table if not exists ukoly (
                id INT auto_increment primary key,
                nazev varchar(100) NOT NULL,
                popis TEXT NOT NULL,
                stav varchar(50) DEFAULT "Nezahájeno" NOT NULL,
                datum DATE DEFAULT (CURRENT_DATE)
            )
        ''')
        print("Tabulka byla vytvořena, nebo již existuje.\n")
    except mysql.connector.Error as err:
        print(f"Chyba při vytváření tabulky: {err}\n")

def hlavni_menu(cursor,conn):
    """Vytvoří hlavní menu"""
    while True:
        print("\nSprávce úkolů - Hlavní menu")
        print("1. Přidat nový úkol")
        print("2. Zobrazit všechny úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program\n")
        moznost = input("Vyberte možnost 1-5: ")
        print("\n")

        if moznost == "1":
            nazev_ukolu, popis_ukolu = vstup_pridat()
            pridat_ukol(nazev_ukolu,popis_ukolu,cursor,conn)
        elif moznost == "2":
            zobrazit_ukoly(cursor)
        elif moznost == "3":
            ukol_id, ukol_stav = vstup_aktualizovat(cursor)
            if ukol_id is None:
                continue
            aktualizovat_ukol(ukol_id,ukol_stav,cursor,conn)
        elif moznost == "4":
            ukol_id = vstup_odstranit(cursor)
            if ukol_id is None:
                continue
            odstranit_ukol(ukol_id,cursor,conn)
        elif moznost == "5":
            cursor.close()
            conn.close()
            print("\nPřipojení k databázi bylo ukončeno.\n")
            print("Program byl ukončen.\n")
            exit()
        else:
            print("\nNeplatná volba, zkuste to znovu.\n")

def vstup_pridat():
    """Vyžádá nazev a popis úkolu a vrátí jej"""
    while True:
        nazev_ukolu = input("\nZadejte název úkolu: ")
        popis_ukolu = input("Zadejte popis úkolu: ")
        if nazev_ukolu == "":
            print("\nMusíte vyplnit všechna pole.")
        elif popis_ukolu == "":
            print("\nMusíte vyplnit všechna pole.")
        else:   
            return nazev_ukolu, popis_ukolu

def pridat_ukol(nazev_ukolu,popis_ukolu,cursor,conn,tabulka="ukoly"):
    """Vyžádá vstup od uživatele a uloží záznam do tabulky"""
    try:
        cursor.execute(f"INSERT INTO {tabulka}(nazev,popis) values(%s,%s)",(nazev_ukolu,popis_ukolu))
        conn.commit()
        print("\nÚkol vložen.\n")
        return True
    except mysql.connector.Error as err:
        print(f"\nChyba při přidávání úkolu: {err}\n") 
        return False

def zobrazit_ukoly(cursor):
    """Zobrazí úkoly v tabulce"""
    try:
        cursor.execute("SELECT id,nazev,popis,stav FROM ukoly WHERE stav = 'Nezahájeno' or stav = 'Probíhá'")
        radky = cursor.fetchall()
        if not radky:
            print("\nTabulka je prázdná.\n")
            return False
        else:
            for radek in radky: 
                print(f"ID: {radek[0]} Název: {radek[1]} Popis: {radek[2]} Stav: {radek[3]}")
            return True   
    except mysql.connector.Error as err:
        print(f"Chyba při načítání dat: {err}") 
        return False      

def vstup_aktualizovat(cursor):
    """Zobrazí úkoly a zeptá se uživatele který záznam a jak chce upravit"""
    if not zobrazit_ukoly(cursor):
        return None,None

    while True:
        ukol_stav = ""
        ukol_id = input("\nZadejte ID úkolu, který chcete aktualizovat: ")

        try:
            ukol_id = int(ukol_id)
        except ValueError:
            print("Musíte zadat číslo")
            continue

        cursor.execute("SELECT id FROM ukoly WHERE id = %s",(ukol_id,))
        overeni = cursor.fetchone()

        if overeni is None:
            print("Tento úkol neexistuje")
            continue
        else:
            while True:
                ukol_stav_vstup = input("Změna stavu: 1 pro Probíhá 2 pro Hotovo: ")
                if ukol_stav_vstup == "1":
                    ukol_stav = "Probíhá"
                    return ukol_id,ukol_stav
                elif ukol_stav_vstup == "2":
                    ukol_stav = "Hotovo"
                    return ukol_id,ukol_stav
                else:
                    print("Neplatná volba")
                    

def aktualizovat_ukol(ukol_id,ukol_stav,cursor,conn,tabulka="ukoly"):
    """Aktualizuje vybraný úkol v tabulce"""
    try:
        cursor.execute(f"UPDATE {tabulka} SET stav = %s WHERE id = %s",(ukol_stav,ukol_id))
        conn.commit()
        print("\nÚkol aktualizován.\n")
        return True
    except mysql.connector.Error as err:
        print(f"\nChyba při aktualizování úkolu: {err}\n")
        return False

def zobrazit_celou_tabulku(cursor):
    """Zobrazí všechny úkoly a jejich záznamy. Pro přehlednost během odstranění"""
    try:
        cursor.execute("SELECT * FROM ukoly")
        radky = cursor.fetchall()
        if not radky:
            print("\nTabulka je prázdná.\n")
            return False
        else:
            for radek in radky: 
                print(f"ID: {radek[0]} Název: {radek[1]} Popis: {radek[2]} Stav: {radek[3]} Datum: {radek[4]}")
            return True
    except mysql.connector.Error as err:
        print(f"Chyba při načítání dat: {err}")
        return False

def vstup_odstranit(cursor):
    """Ptá se uživatele který záznam chce odstranit"""
    if not zobrazit_celou_tabulku(cursor):
        return None
    while True:
        ukol_id = input("\nZadejte ID úkolu, který chcete odstranit: ")

        try:
            ukol_id = int(ukol_id)
        except:
            print("Musíte zadat číslo")
            continue

        cursor.execute("SELECT id FROM ukoly WHERE id = %s",(ukol_id,))
        overeni = cursor.fetchone()

        if overeni is None:
            print("Tento úkol neexistuje")
            continue
        else:
            return ukol_id

def odstranit_ukol(ukol_id,cursor,conn,tabulka="ukoly"):
    """Odstraní vybraný úkol"""
    try:
        cursor.execute(f"DELETE FROM {tabulka} WHERE id = %s",(ukol_id,))
        conn.commit()
        print("\nÚkol byl odstraněn.\n")
        return True
    except mysql.connector.Error as err:
        print(f"\nChyba při odstraňování úkolu: {err}\n")
        return False


if __name__ == "__main__":
    conn, cursor = pripojeni_db()
    vytvoreni_tabulky(cursor)
    hlavni_menu(cursor, conn)