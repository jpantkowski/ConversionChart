import numpy as np
from dateutil.parser import parse, ParserError
import httpx
import pandas as pd
import matplotlib.pyplot as plt

""" Program służy do wyświetlenia prostego wykresu liniowego przedstawiającego ceny 1 jednostki danej waluty 
w przeliczeniu na złotówki 
v2 - program nie wywołuje osobnej odpowiedzi httpx dla każdej daty, zamiast tego wywołuje zapytanie raz i zwraca odpowiedź jako JSONa ."""

""" currency_list_function - funkcja służąca do wyświetlenia par wartości Currency Code - Currency
 oraz zwracająca listę list z parami powyższych.
1. Utworzona zostaje pusta lista currency_list.
2. Pobieramy odpowiedź z NBP używając httpx.get. Link jest w tym przypadku statyczny.
3. Konwertujemy odpowiedź na jsona. Odpowiedź przypisujemy do zmiennej currency_dicts. 
W rezultacie otrzymujemy lisę, której każdy element jest słownikiem którego kluczami są: Currency, Code i Mid.
4. Iterujemy po każdym elemencie (walucie) tej listy. 
Dla kazdej iteracji wywołujemy wartości wg kluczy "Currency" oraz "Code".
Pary tych wartości przypisujemy do listy currency_list.
5. Funkcja drukuje tą listę w formie ładnej pandasowej tabelki. 
Funkcja wywołuje się przy wpisywaniu waluty przez usera, więc user dostaje ładną listę dostępnych walut wraz z jej kodem.
6. Funkcja zwraca tą listę abyśmy mogli po niej iterować w innych funkcjach."""

def currency_list_function():
    currency_list = []
    response = httpx.get("https://api.nbp.pl/api/exchangerates/tables/A")
    currency_dicts = response.json()[0]['rates'][0:]
    for currency in currency_dicts:
        currency_name = currency["currency"]
        codename = currency["code"]
        currency_pair = []
        currency_pair.append(codename)
        currency_pair.append(currency_name)
        currency_list.append(currency_pair)
    print(pd.DataFrame(currency_list, columns=["Currency Code", "Currency"]).to_string(index=False))
    return(currency_list)

""" user_currency_input - funkcja pytająca usera o walutę, której wykres chce zobaczyć.
    is_currency_valid - funkcja sprawdzająca czy waluta wpisana przez usera jest dostępna na liście walut.
1. Funkcja pyta usera o walutę. User może podać kod małymi literami - używana jest funkcja .upper, aby zwrócić wielkie litery.
2. Wywoływana jest funkcja is_currency_valid - jeżeli wpisany przez usera kod jest na pierwszym miejscu, 
którego kolwiek elementu z listy currency_list to funkcja zwraca True. W przeciwnym razie False.
3. Jeżeli is_currency_valid zwraca False, to funkcja user_currency_input rekurencyjnie wywoła samą siebie.
Jeżeli zwraca True to input usera przekazywany jest do wyniku funkcji."""

def user_currency_input(currency_list):
    user_currency = str(input("Jaka waluta wariacie?")).upper()
    while is_currency_valid(user_currency, currency_list) == False:
        return user_currency_input(currency_list)
    return user_currency

def is_currency_valid(x, currency_list):
    is_ok = any(pair[0] == x for pair in currency_list)
    if is_ok == True:
        print("Waluta przyjęta")
        return True
    else:
        print("Podaj prawidłowy kod waluty")
        return False

""" dates_input - funkcja pytająca usera o daty, wg których ma być wyświetlony wykres.
    are_dates_valid - funkcja sprawdzająca czy daty podane przez użytkownika są okej.
    is_valid_date - funkcja sprawdzająca czy input użytkownika jest datą.
1. User podaje datę początkową i datę końcową w formacie YYYY-MM-DD.
2. Wywołujemy pętlę - jeżeli funkcja are_dates_valid zwraca False, znaczy to, że coś jest nie tak z datą. 
W takim przypadku user zostanie poproszony o wpisanie innych dat rekurencyjnie wywołąną funkcją dates_input . 
Funkcja are_dates_valid sprawdza czy input usera jest w ogóle datami - 
( sprawdzająca funkcja is_valid_date, używająca funkcji parse z dateutil.parser ).
Następnie - dopiero, gdy obie daty są datami, sprawdzamy czy data końcowa jest później niż data początkowa. 
W tej werji programu, maksymalny przedział jaki przyjmuje API NBP to 367 dni. Program sprawdza więc czy daty nie przekraczają tego limitu.
Gdy wszystki warunki są spełnione, funkcja zwraca True i daty zostają przyjęte.
4. Funkcja dates_input zwraca dwie zmienne - start_date i end_date. Są one zwalidowane i gotowe do podstawienia pod URLa.
W każdej iteracji data doadje się do listy dates_range. Następnie wywoływany jest następny dzień. """

def dates_input():
    start_date = input("Podaj datę startową w formacie YYYY-MM-DD")
    end_date = input("Podaj datę końcową w formacie YYYY-MM-DD")
    while are_dates_valid(start_date, end_date) != True:
        return dates_input()
    return start_date, end_date

def are_dates_valid(start_date, end_date):
    if is_valid_date(start_date) and is_valid_date(end_date):
        if (parse(end_date) - parse(start_date)).days > 0:
            if (parse(end_date) - parse(start_date)).days <= 367:
                return True
            print("Podane daty przekraczają dozwolony zakres 367 dni!")
            return False
        print("Data końcowa musi być późniejsza od początkowej!")
    else:
        print("Podaj poprawne daty w formacie YYYY-MM-DD!")
        return False

def is_valid_date(date):
    if not date:
        return False
    try:
        parse(date)
        return True
    except ParserError:
        return False

""" get_rate - funkcja zwracająca listę słowników dla każdej dat z podanego przez usera przedziału.
1. Wywołujemy zapytanie do NBP używając httpx.get. Tym razem adres jest dynamiczny. 
Zapytanie wywoływane jest na podstawie zdefiniowanych zmiennych  - start_date, end_date i currency.
2. Konwertujemy odpowiedź na jsona. Przypisujemy ją do zmiennej rate_dict.
3. Jeżeli user poda daty, które faktycznie są datami, ale nie znajdują się w API (np. odległa przeszłość albo przyszłość) to zapytanie wywoła błąd.
Używamy więc bloku try/except . Wywołany błąd nie skutuje niczym - zdefiniowana pusta lista rate_dict pozostanie pusta.
4. Funkcja zwraca listę, której każdy element to słownik odpowiadający za daną datę i posiadający kurs danej waluty.
Lista ta może być pusta w przypadku wystąpienia błędu."""

def get_rate(start_date, end_date, currency):
    rate_dict = []
    try:
        response = httpx.get(f"https://api.nbp.pl/api/exchangerates/rates/A/{currency}/{start_date}/{end_date}/")
    except:
        pass
    else:
        rate_dict = response.json()["rates"]
    finally:
        return rate_dict

""" print_chart - funkcja przygotowujaca dane i rysująca wykres.
1. Przypisujemy wynik funkcji currency_list_function do zmiennej currency_list.
Przypisujemy wynik funkcji user_currency_input do zmiennej user_currency_input_CODE.
Przypisujemy wyniki funkcji dates_input do zmiennych start_date i end_date.
Tworzymy zmienne z listami x_axis_date oraz y_axis_rate.
Przypisujemy wynik funkcji get_rate do zmiennej rate_dict.
2. Iterujemy po każdym elemencie w liście rate_dict. 
Z każdego elementu tej listy wrzucamy datę do listy x_axis_date oraz kurs do listy y_axis_rate.
Przerabiamy x_axis_date oraz y_axis_rate na pandasowy Dataframe.
3. Sprawdzamy czy lista rate_dict zawiera jakiekolwiek elementy. Jeżeli nie, to znaczy, że api zwróciło błąd i funkcja print_chart zostanie wywołana od nowa.
4. W przeciwnym razie definiujemy wykres:
- dodajemy etykietę osi x - "Daty",
- definiujemy elementy osi x - mają być przedstawione pionowo ( parametr rotation = "vertical" ) i rozmiar 6 ( fontsize = 6 ),
- dodajemy etykietę osi y - generowana dynamicznie, używamy f-stringa i zmiennej user_currency_input_CODE,
- dodajemy wykres właściwy gdzie x to daty ( df.x ) a y to kursy ( df.y ) a sam wykres ma etykietę "Kursy" ( label = "Kurs" ),
- dodajemy linię, ze średnim kursem dla podanego przedziału dat. Zmienna average to średnia z df.y .
Średnią tą pokazujemy na wykresie jako poziomą linię ( plt.axhline ) na pozomie średniego kursu,
linia ma być zielona ( color = "g" ), przerywana ( linestyle = "--" ) i opisana jako średnia ( label = "Średnia" ),
- dodajemy napis z podanym średnim kursem ( average ), który ma się wyświetlać po prawej stronie tuż nad linią średniego kursu,
określamy pozycję napisu na osi: x to ostatni element listy df.x ( index [-1] ) a y to właśnie średnia.
napis wyrównany do prawej ( ha = "right" ) i do dołu ( va = "bottom" ),
dynamicznie wyświetlający fstringa ze średnim kursem ( s = f"average" ),
- definiujemy jeszcze maksymalne i minimalne kursy dla danego przedziału,
przypisujemy te wartości do zmienncyh max_rate i min_rate wywołując funkcje max i min na df.y,
sprawdzamy jaki index mają te wartości na df.y używając funkcji .idxmax() i .idxmin(),
wartości max i min przedstawiamy na wykresie jako dodatkowy tekst, których współrzędnymi są odpowiedznio:
x = max/min_index zastosowany na df.x ( zbiory df.x i df.y mają tyle samo elementów i są to pary wartości,
więc wywołanie indeksu maksymalnen/minimalnej wartości na liście df.x zdefiniuje nam położenie tego napisu na osi x,
y = max/min_rate,
wyświetlany tekst to fstring z max/min kursem danej waluty,
- dodajemy prostą legendę,
- pokazujemy wykres funkcją plt.show .
"""

def print_chart():
    currency_list = currency_list_function()
    user_currency_input_CODE = user_currency_input(currency_list)
    start_date, end_date = dates_input()
    x_axis_date = []
    y_axis_rate = []
    rate_dict = get_rate(start_date, end_date, user_currency_input_CODE)
    for date in rate_dict:
        x_axis_date.append(date["effectiveDate"])
        y_axis_rate.append(date["mid"])
    df = pd.DataFrame({"x": x_axis_date,
                       "y": y_axis_rate})
    if len(rate_dict)==0:
        print("Brak dostępnych kursów w podanym przedziale dat! Spróbuj innych dat.")
        print_chart()
    else:
        plt.xlabel("Daty")
        plt.xticks(rotation= "vertical", fontsize=6)
        plt.ylabel(f"Cena 1 {user_currency_input_CODE} w PLN")
        plt.plot(df.x, df.y, label="Kurs")
        average = float(np.nanmean(df.y))
        plt.axhline(y = average, color="g", linestyle="--", label="Średnia")
        plt.text(x = df.x.iloc[-1], y = average, ha = "right", va="bottom", s=f"{average}")
        max_rate = max(df.y)
        min_rate = min(df.y)
        max_index = df.y.idxmax()
        min_index = df.y.idxmin()
        plt.text(x = df.x.iloc[max_index], y = max_rate, s = f"MAX {max_rate}")
        plt.text(x = df.x.iloc[min_index], y = min_rate, s = f"MIN {min_rate}")
        plt.legend()
        plt.show()

""" Known Issues:
- przy dużej ilości dat, wykres może stać się nieczytelny,
- jeżeli maksymalny i minimalny kurs są tą samą wartością, to napis wyświetli się w tym samym miejscu przez co nie będzie czytelny. """
