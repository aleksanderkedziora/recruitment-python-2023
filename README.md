#### **Autor: ...**

- `example_currency_rates.json`: Lokalne źródło danych z kursami walut.
- `database.json`: Baza danych z zapisanymi kursami walut.

#### **Aleksander Kędziora: ...**

- Program realizuje założenia przesłane w załączniku.
- Program domyślnie działa w trybie produkcyjnym z wykorzystaniem zewnętrznego źródła kursów.
- Przed uruchomieniem należy zainstalować biblioteki wylistowane w pliku `requirements.txt`.
- Po zainstalowaniu wymaganych paczek program uruchamiamy z CLI (terminala) następującymi komendami:

1. **Przykładowe uruchomienie:**
    
    ```bash
    # Te komendy są przeznaczone do użytku programistycznego i nie powinny być uruchamiane bezpośrednio z poziomu README.
    # Proszę sprawdzić dokumentację lub przesłane załączniki w celu uzyskania pełnej listy dostępnych komend i ich konfiguracji.

    # Ogólna postać komendy startowej:
    python -m task "ISO waluty" "kwota do przeliczenia na PLN" \
    -s "źródło danych [API, LOCAL]" --prod/--dev
    
    # Tryb domyślny z wykorzystaniem trybu produkcyjnego z API NBP:   
    python -m task "ISO waluty" "kwota do przeliczenia na PLN" \
    -s API --prod
    
    # ... którego można uruchomić w wersji skróconej:
    python -m task "ISO waluty" "kwota do przeliczenia na PLN" \

    # Tryb produkcyjny z wykorzystaniem danych lokalnych:   
    python -m task "ISO waluty" "kwota do przeliczenia na PLN" \
    -s LOCAL --prod
   
    # Alternatywnie, tryb deweloperski z API NBP:
    python -m task "ISO waluty" "kwota do przeliczenia na PLN" \
    -s API --dev
   
    # ..., w skróconej wersji:
    python -m task "ISO waluty" "kwota do przeliczenia na PLN" \
    --dev

    # W przypadku gdy chcemy skorzystać z danych lokalnych:
    python -m task "ISO waluty" "kwota do przeliczenia na PLN" \
    -s LOCAL --dev
    ```

2. **Przykład przeliczenia 100 euro na złotówki z użyciem API NBP i zapisu do bazy SQLite:**

    ```bash
    python -m task eur 100.00 --prod -s API
    ```

    Aby skorzystać z domyślnych ustawień, pomiń ostatnie dwie flagi:

    ```bash
    python -m task eur 100.00
    ```

3. **Uruchamianie testów przy użyciu pytest:**

    Przed uruchomieniem testów, upewnij się, że masz zainstalowanego pytest. Możesz to zrobić za pomocą poniższej komendy:

    ```bash
    pip install -r requirements.txt
    ```

    Następnie uruchom testy za pomocą komendy:

    ```bash
    pytest
    ```

**Uwaga:** API jest aktualizowane w dni powszednie, odpalenie skryptu w dni wolne od pracy będzie skutkować przerwaniem wykonywania programu, co będzie objawiać się w postaci otrzymania błędu 404.
