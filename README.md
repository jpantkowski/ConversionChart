# ConversionChart
Study project which will display a chart of exchange rate between PLN and chosen currency

Wersje pliku:
- Conversion Chart - używa URLa https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{date}/ i wysyła zapytanie do niego tyle razy, ile dni jest w przedziale dat zdefiniowanym przez użytkownika. Każde zapytanie jest przerabiane na JSona i operujemy na tym JSonie. Program teoretycznie działa, ale przy większym przedziale dat, trwa bardzo długo.
- Conversion Chart v2 - używa URLa https://api.nbp.pl/api/exchangerates/rates/A/{currency}/{start_date}/{end_date}/ i wysyła tylko jedno zapytanie. Przerabimy tylko jedną odpowiedź na JSona i operujemy na niej. Program działa zdecydowanie szybciej. Minusem jest, że link ten przyjmuje tylko 367 dni różnicy w dacie. Wyjątek ten jest jednak obsłużony.
- Conversion Chart v3 - program nie jest ograniczony do przedziału 367 dat ( ograniczenie API ), jednocześnie nie wywołuje zapytania dla każdej daty. Zastosowano paging po 365 dat wiec program wywołuje zapytanie
dla każdej podlisty 365 dat z listy wszystkich dat.
- Conversion Chart final - uporządkowany kod za pomocą pylint."""

Known issues:

