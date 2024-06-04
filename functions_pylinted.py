""" Program służy do wyświetlenia prostego wykresu liniowego
przedstawiającego ceny 1 jednostki danej waluty
w przeliczeniu na złotówki
v3 - program nie jest ograniczony do przedziału 367 dat ( ograniczenie API ),
jednocześnie nie wywołuje zapytania dla każdej daty.
Zastosowano paging po 365 dat wiec program wywołuje zapytanie
dla każdej podlisty 365 dat z listy wszystkich dat. """

import math
from datetime import timedelta, datetime
import numpy as np
from dateutil.parser import parse, ParserError
import httpx
import pandas as pd
import matplotlib.pyplot as plt

""" currency_list_function - funkcja służąca do wyświetlenia par wartości Currency Code - Currency
    oraz zwracająca listę list z parami powyższych.
1. Utworzona zostaje pusta lista currency_list.
2. Pobieramy odpowiedź z NBP używając httpx.get. Link jest w tym przypadku statyczny.
3. Konwertujemy odpowiedź na jsona. Odpowiedź przypisujemy do zmiennej currency_dicts. 
W rezultacie otrzymujemy listę, której każdy element 
jest słownikiem którego kluczami są: Currency, Code i Mid.
4. Iterujemy po każdym elemencie (walucie) tej listy. 
Dla kazdej iteracji wywołujemy wartości wg kluczy "Currency" oraz "Code".
Pary tych wartości przypisujemy do listy currency_list.
5. Funkcja drukuje tą listę w formie ładnej pandasowej tabelki. 
Funkcja wywołuje się przy wpisywaniu waluty przez usera, 
więc user dostaje ładną listę dostępnych walut wraz z jej kodem.
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
    return currency_list

""" user_currency_input - funkcja pytająca usera o walutę, której wykres chce zobaczyć.
    is_currency_valid - funkcja sprawdzająca czy waluta wpisana przez usera jest dostępna na liście walut.
1. Funkcja pyta usera o walutę. User może podać kod małymi literami - używana jest funkcja .upper, aby zwrócić wielkie litery.
2. Wywoływana jest funkcja is_currency_valid - jeżeli wpisany przez usera kod jest na pierwszym miejscu, 
któregokolwiek elementu z listy currency_list to funkcja zwraca True. W przeciwnym razie False.
3. Jeżeli is_currency_valid zwraca False, to funkcja user_currency_input rekurencyjnie wywoła samą siebie.
Jeżeli zwraca True to input usera przekazywany jest do wyniku funkcji."""

def user_currency_input(currency_list):
    user_currency = str(input("Jaka waluta wariacie?")).upper()
    if is_currency_valid(user_currency, currency_list):
        return user_currency
    return user_currency_input(currency_list)

def is_currency_valid(x, currency_list):
    is_ok = any(pair[0] == x for pair in currency_list)
    if is_ok:
        print("Waluta przyjęta")
        return True
    print("Podaj prawidłowy kod waluty")
    return False

""" dates_input - funkcja pytająca usera o daty, wg których ma być wyświetlony wykres
    oraz zmieniająca datę początkową wg dat dostępnych w API NBP.
    are_dates_valid - funkcja sprawdzająca czy daty podane przez użytkownika są okej.
    is_valid_date - funkcja sprawdzająca czy input użytkownika jest datą.
    next_day - funkcja, która na podstawie podanej daty, zwraca datę następnego dnia.
1. User podaje datę początkową i datę końcową w formacie YYYY-MM-DD.
2. Funkcja sprawdza od jakiej daty dostępne są kursy w API NBP za pomocą kontrukcji case-match (daty sprawdzone manualnie dla każdej daty).
Następnie, jeżeli start_date usera jest wcześniej niż początkowa data z API, to jest ona podmieniana a user otrzymuje komunikat.
Ponadto, jeżeli data końcowa wypada wcześniej niż nowa data początkowa, 
user otrzymuje komunikat a funkcja dates_input wywołuje się od nowa.
3. Wywołujemy ifa - jeżeli funkcja are_dates_valid zwraca False, znaczy to, że coś jest nie tak z datą. 
W takim przypadku user zostanie poproszony o wpisanie innych dat rekurencyjnie wywołąną funkcją dates_input . 
Funkcja are_dates_valid sprawdza czy:
a. input usera jest w ogóle datami - (sprawdzająca funkcja is_valid_date, używająca funkcji parse z dateutil.parser).
b. czy data końcowa jest później niż data początkowa. 
Każdy warunek w osobnym ifie aby otrzymać stosowny komentarz. Gdy wszystki warunki są spełnione, funkcja zwraca True i daty zostają przyjęte.
4. Następnie, za pomocą funkcji next_day budujemy listę dat w przedziale podanym przez użytkownika.
5. Funkcja dates_input zwraca liste dat. Daty są zwalidowane."""

def dates_input(currency_code):
    start_date = input("Podaj datę startową w formacie YYYY-MM-DD")
    end_date = input("Podaj datę końcową w formacie YYYY-MM-DD")

    currency = currency_code
    match currency:
        case "USD" | "AUD" | "CAD" | "EUR" | "HUF" | "CHF" | \
             "GBP" | "JPY" | "CZK" | "DKK" | "NOK" | "SEK" | \
             "XDR":
            api_start_date = "2002-01-02"
        case "HKD" | "UAH" | "ZAR":
            api_start_date = "2003-01-07"
        case "RON" | "BGN":
            api_start_date = "2007-04-04"
        case "THB" | "NZD" | "SGD" | "ISK" | "TRY" | "PHP" | \
             "MXN" | "BRL" | "MYR" | "IDR" | "KRW" | "CNY":
            api_start_date = "2008-01-02"
        case "ILS" | "INR":
            api_start_date = "2011-07-27"
        case "CLP":
            api_start_date = "2011-08-31"

    if are_dates_valid(start_date, end_date):
        if parse(start_date) < parse(api_start_date):
            start_date = api_start_date
            print(f"Kursy dostępne od {api_start_date}! "
                  f"Data początkowa zmieniona na {api_start_date}")
            if parse(end_date) < parse(start_date):
                print("Kursy niedostępne, spróbuj innych dat")
                return dates_input(currency_code)
        dates_range = []
        while start_date <= end_date:
            dates_range.append(start_date)
            start_date = next_day(start_date)
        return dates_range
    return dates_input(currency_code)

def are_dates_valid(start_date, end_date):
    if is_valid_date(start_date) and is_valid_date(end_date):
        if datetime.now() >= parse(end_date):
            return True
        print("Data końcowa nie może być w przyszłości!")
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

def next_day(date_str):
    date = parse(date_str)
    next_date = date + timedelta(days=1)
    return next_date.strftime('%Y-%m-%d')

""" paging - funkcja dzieląca listę dat na podlisty po 365 elementów.
    get_rate - funkcja zwracająca listę słowników dla każdej dat z podanego przez usera przedziału.
1. Dzielimy naszą listę dat na podlisty (strony po 365 elementów) używając pętli for.
Iterujemy po każdym zbiorze 365 elementów listy i dodajemy te listy do listy pages_list. Funkcja zwraca tą listę
2. Tworzymy pustą listę all_rates.
3. Iterujemy po każdej podliście listy pages_list zwracanej przez funkcję paging. 
4. Definiujemy elementy linku - pierwszy element każdej podlisty to start_date a ostatni to end_date.
5. Wywołujemy zapytanie do NBP używając httpx.get. Tym razem adres jest dynamiczny. 
Zapytanie wywoływane jest na podstawie zdefiniowanych zmiennych  - start_date, end_date i currency.
6. Jeżeli odpowiedź na stronie jest różna od "404 NotFound - Not Found - Brak danych" (bardzo konkretny scenariusz, ale może się zdarzyć)
Konwertujemy odpowiedź na jsona. Przypisujemy ją do zmiennej rate_dict oraz dołączamy rate_dict do listy all_rate.
7. Funkcja zwraca listę, której każdy element to słownik 
odpowiadający za daną datę i posiadający kurs danej waluty."""

def paging(dates_list, page_size):
    pages_list = []
    for date in range(0, len(dates_list), page_size):
        pages_list.append(dates_list[date:date + page_size])
    return pages_list

def get_rate(dates_list, currency):
    all_rates = []
    for page in dates_list:
        start_date = page[0]
        end_date = page[-1]
        response = httpx.get(
            f"https://api.nbp.pl/api/exchangerates/rates/A/{currency}/{start_date}/{end_date}/")
        if not response.text == "404 NotFound - Not Found - Brak danych":
            rate_dict = response.json()["rates"]
            all_rates.extend(rate_dict)
    return all_rates

""" print_chart - funkcja przygotowujaca dane i rysująca wykres.
1. Przypisujemy wynik funkcji currency_list_function do zmiennej currency_list.
Przypisujemy wynik funkcji user_currency_input do zmiennej user_currency_input_CODE.
Przypisujemy wynik funkcji dates_input do zmiennej dates_list.
Tworzymy zmienne z listami x_axis_date oraz y_axis_rate.
Przypisujemy wynik funkcji get_rate do zmiennej rate_dict.
2. Iterujemy po każdym elemencie w liście rate_dict. 
Z każdego elementu tej listy wrzucamy datę do listy x_axis_date oraz kurs do listy y_axis_rate.
Przerabiamy x_axis_date oraz y_axis_rate na pandasowy Dataframe.
3. Sprawdzamy czy lista rate_dict zawiera jakiekolwiek elementy. Jeżeli nie, to znaczy, że api zwróciło błąd i funkcja print_chart zostanie wywołana od nowa.
4. W przeciwnym razie definiujemy wykres:
- dodajemy etykietę osi x - "Daty",
- definiujemy elementy osi x - mają być przedstawione pod kątem 45 stopni ( parametr rotation = 45 ) i rozmiar 8 ( fontsize = 8 ),
- definujemy ilość labelek dla których wykres pozostaje czytelny w wymuszonym trybie fullscreen, przymujemy 60 labelek,
- jeżeli ilość dat w df.x przekracza 60, to obliczamy parametr skoku - co która labelka ma się wyświetlić. Liczba ta ma być zaokrąglona w górę ( funkcja ceil z biblioteki math ),
- ustawiamy parametr ticks aby przeskakiwał po indeksach oraz labels aby labelkami byly wszystkie daty od pierwszej do ostatniej, ale z określonym skokiem,
- jeżeli liczba dat nie wynosi 60 to skok nie występuje,
- dodajemy etykietę osi y - generowana dynamicznie, używamy f-stringa i zmiennej user_currency_input_CODE,
- dodajemy wykres właściwy gdzie x to daty ( df.x ) a y to kursy ( df.y ) a sam wykres ma etykietę "Kursy" ( label = "Kurs" ),
- definiujemy także zmienną marker, która ma określać parametr marker - jeżeli df.x zawiera tylko jeden element to wykres liniowy nie będzie wygenerowany, 
więc aby zobaczyć kurs dla jednej daty, będzie on oznaczony kwadratem ("s"). Jeżeli jest więcej elementów to marker jest niepotrzebny bo wykres się pojawia.
- jeżeli minimalny i maksymalny kurs nie jest taki sam, to pokazujemy dodatkowo średni, minimalny i maksymalny kurs ( jeżeli są takie same to ich wyświetlanie nie ma sensu ),
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
wyświetlany tekst to fstring z max/min kursem danej waluty, dodatkową dołączona jest data w której występuje min/max kurs,
- wymuszamy otwarcie wykresu w trybie pełnoekranowym,
- dodajemy prostą legendę,
- pokazujemy wykres funkcją plt.show ."""

def print_chart():
    currency_list = currency_list_function()
    user_currency_input_code = user_currency_input(currency_list)
    dates_list = dates_input(user_currency_input_code)
    x_axis_date = []
    y_axis_rate = []
    rate_dict = get_rate(paging(dates_list, 365), user_currency_input_code)
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
        max_x_labels = 60
        if len(df.x) > max_x_labels:
            step = math.ceil(len(df.x) / max_x_labels)
            plt.xticks(ticks = df.index[::step], labels = df.x[::step], rotation = 45, fontsize = 8)
        else:
            plt.xticks(ticks = df.index[::], labels = df.x[::], rotation= 45, fontsize=8)
        plt.ylabel(f"Cena 1 {user_currency_input_code} w PLN")
        if len(df.x) == 1:
            marker = "s"
        else:
            marker = ""
        plt.plot(df.x, df.y, label="Kurs", marker=marker)
        average = float(np.nanmean(df.y))
        max_rate = max(df.y)
        min_rate = min(df.y)
        if not max_rate == min_rate:
            plt.axhline(y = average, color="g", linestyle="--", label="Średnia")
            plt.text(x = df.x.iloc[-1], y = average, ha = "right", va="bottom", s=f"{average}")
            max_index = df.y.idxmax()
            min_index = df.y.idxmin()
            plt.text(x = df.x.iloc[max_index], y = max_rate,
                     s = f"MAX {max_rate} - {df.x[max_index]}")
            plt.text(x = df.x.iloc[min_index], y = min_rate,
                     s = f"MIN {min_rate} - {df.x[min_index]}")
        plt.get_current_fig_manager().full_screen_toggle()
        plt.legend()
        plt.show()

""" Known Issues:
"""