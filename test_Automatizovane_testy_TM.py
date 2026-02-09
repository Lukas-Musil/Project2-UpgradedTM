import pytest
import mysql.connector
from VylepsenyTM_Lukas_Musil import aktualizovat_ukol,pridat_ukol,odstranit_ukol

db_host = "localhost"
db_user = "root"
db_password = "1111"
db_name = "db_ukoly"

@pytest.fixture(scope="session")
def db_setup():
    """
    Fixture pro připojení k databázi a nastavení testovacího prostředí.
    """
    try:
        conn = mysql.connector.connect(
            host = db_host,
            user = db_user,
            password = db_password,
            database = db_name
        )
        cursor = conn.cursor(buffered=True)
        print("\nPřipojení k databázi bylo úspěšné.\n")
        
    except mysql.connector.Error as err:
        print(f"Chyba při připojování: {err}\n")
        
    cursor.execute("""
        create table if not exists test_ukoly (
                id INT auto_increment primary key,
                nazev varchar(100) NOT NULL,
                popis TEXT NOT NULL,
                stav varchar(50) DEFAULT "Nezahájeno" NOT NULL,
                datum DATE DEFAULT (CURRENT_DATE)
        )
    """)
    conn.commit()
    
    yield conn, cursor
    
    cursor.execute("DROP TABLE IF EXISTS test_ukoly")
    conn.commit()

    cursor.close()
    conn.close()

def test_pozitivni_pridani(db_setup):
    """Test pozitivních vstupů"""    
    conn,cursor = db_setup
    tabulka = "test_ukoly"

    pridat_ukol("Test úkol","Test popis",cursor,conn,tabulka)
    
    cursor.execute(f"SELECT * FROM {tabulka} WHERE nazev = 'Test úkol'")
    result = cursor.fetchone()
    assert result is not None, "Záznam nebyl vložen do tabulky."
    assert result[1] == "Test úkol", "Název není správný."
    assert result[2] == 'Test popis', "Popis není správný."


def test_negativni_pridani(db_setup):
    """Testuje vložení příliš dlouhého text"""
    conn, cursor = db_setup
    tabulka = "test_ukoly"

    vysledek = pridat_ukol("u" * 101, "Test popis", cursor, conn, tabulka)
    assert vysledek is False, "Vložení s příliš dlouhým názvem by mělo selhat."


def test_pozitivni_aktualizace(db_setup):
    """Pozitivní test aktualizace"""
    conn, cursor = db_setup
    tabulka = "test_ukoly"

    cursor.execute(f"INSERT INTO {tabulka} (nazev,popis) VALUES ('Test úkol', 'Test popis')")
    conn.commit()

    aktualizovat_ukol(1,"Probíhá",cursor,conn,tabulka)
    
    cursor.execute(f"SELECT stav FROM {tabulka} WHERE nazev='Test úkol'")
    vysledek = cursor.fetchone()
    assert vysledek[0] == "Probíhá", "Stav nebyl aktualizován"

def test_negativni_aktualizace(db_setup):
    """Negativní test aktualizace"""
    conn, cursor = db_setup
    tabulka = "test_ukoly"

    cursor.execute("INSERT INTO test_ukoly (nazev,popis) VALUES ('Test úkol', 'Test popis')")
    conn.commit()

    vysledek = aktualizovat_ukol("Neexistující ID","Probíhá",cursor,conn,tabulka)
    assert vysledek is False, "Aktualizace by měla selhat pokud se v id místo čísla zadá text"

    
def test_pozitivni_odstraneni(db_setup):
    """Test správného smazání úkolu"""
    conn, cursor = db_setup
    tabulka = "test_ukoly"  

    cursor.execute("INSERT INTO test_ukoly (nazev,popis) VALUES ('Test úkol', 'Test popis')")
    conn.commit()

    vysledek = odstranit_ukol(1,cursor,conn,tabulka)
    assert vysledek is True, "Odstranění úkolu by mělo proběhnout úspěšně"

    

def test_negativni_odstraneni(db_setup):
    """Test smazání neexistujícího úkolu"""
    conn, cursor = db_setup

    cursor.execute("INSERT INTO test_ukoly (nazev,popis) VALUES ('Test úkol', 'Test popis')")
    conn.commit()

    cursor.execute("SELECT COUNT(*) from test_ukoly")
    puvodni_pocet = cursor.fetchone()[0]

    odstranit_ukol(-1,cursor,conn,"test_ukoly")

    cursor.execute("SELECT COUNT(*) from test_ukoly")
    konecny_pocet = cursor.fetchone()[0]
    
    assert puvodni_pocet == konecny_pocet , "Smazání neexistujícího úkolu provedlo změnu v databázi"


