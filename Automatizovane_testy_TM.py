import pytest
import mysql.connector

@pytest.fixture(scope="function")
def db_setup():
    """
    Fixture pro připojení k databázi a nastavení testovacího prostředí.
    """
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="db_ukoly"
    )
    cursor = conn.cursor()

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
    conn, cursor = db_setup

    cursor.execute("INSERT INTO test_ukoly (nazev,popis) VALUES ('Test úkol', 'Test popis')")
    conn.commit()

    cursor.execute("SELECT * FROM test_ukoly WHERE nazev = 'Test úkol'")
    result = cursor.fetchone()
    assert result is not None, "Záznam nebyl vložen do tabulky."
    assert result[1] == "Test úkol", "Název není správný."
    assert result[2] == 'Test popis', "Popis není správný."

def test_negativni_pridani(db_setup):
    """Testuje vložení příliš dlouhého text"""
    conn, cursor = db_setup

    with pytest.raises(mysql.connector.Error, match="Data too long for column"):
        cursor.execute("INSERT INTO test_ukoly (nazev, popis) VALUES (%s, 'Test popis')", ('u' * 101,))
        conn.commit()

def test_pozitivni_aktualizace(db_setup):
    """Pozitivní test aktualizace"""
    conn, cursor = db_setup

    cursor.execute("INSERT INTO test_ukoly (nazev,popis) VALUES ('Test úkol', 'Test popis')")
    conn.commit()

    cursor.execute("UPDATE test_ukoly SET stav = 'Probíhá' WHERE nazev = 'Test úkol'")
    conn.commit()
    
    cursor.execute("SELECT stav FROM test_ukoly WHERE nazev='Test úkol'")
    vysledek = cursor.fetchone()
    assert vysledek[0] == "Probíhá", "Stav nebyl aktualizován"

def test_negativni_aktualizace(db_setup):
    """Negativní test aktualizace"""
    conn, cursor = db_setup

    cursor.execute("INSERT INTO test_ukoly (nazev,popis) VALUES ('Test úkol', 'Test popis')")
    conn.commit()

    with pytest.raises(mysql.connector.errors.DataError):
        cursor.execute("UPDATE test_ukoly SET datum = 'TEXT' WHERE nazev = 'Test úkol'")
        conn.commit()


def test_pozitivni_odstraneni(db_setup):
    """Test správného smazání úkolu"""
    conn, cursor = db_setup

    cursor.execute("INSERT INTO test_ukoly (nazev,popis) VALUES ('Test úkol', 'Test popis')")
    conn.commit()

    cursor.execute("DELETE FROM test_ukoly WHERE nazev = 'Test úkol'")
    conn.commit()
    
    cursor.execute("SELECT * FROM test_ukoly WHERE nazev='Test úkol'")
    vysledek = cursor.fetchone()
    assert vysledek is None, "Úkol nebyl smazán"

def test_negativni_odstraneni(db_setup):
    """Test smazání neexistujícího úkolu"""
    conn, cursor = db_setup

    cursor.execute("INSERT INTO test_ukoly (nazev,popis) VALUES ('Test úkol', 'Test popis')")
    conn.commit()

    cursor.execute("SELECT COUNT(*) from test_ukoly")
    puvodni_pocet = cursor.fetchone()[0]

    cursor.execute("DELETE FROM test_ukoly WHERE nazev = 'Neexistující úkol'")
    conn.commit()

    cursor.execute("SELECT COUNT(*) from test_ukoly")
    konecny_pocet = cursor.fetchone()[0]
    
    assert puvodni_pocet == konecny_pocet , "Smazání neexistujícího úkolu provedlo změnu v databázi"


