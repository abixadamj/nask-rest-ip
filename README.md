# nask-rest-ip
### Zadanie rekrutacyjne - REST dla ip

**Adam Jurkiewicz**, *adam (at) jurkiewicz.tech*

## Opis działania programu - zastosowane podejście:

Program wykonuje następujące kroki główne:
- Wczytanie danych z pliku JSON do listy tymczasowej
- sortowanie bazy wg klucza `"ip_network"` dla celów późniejszego wyszukiwania binarnego
  (*dla przykładowego zbioru `4 000 001` elementów zajmuje ok. `3,5 GB RAM`*)
- uruchomienie `FastAPI`, usługa dostępna pod adresem http://localhost:8000/, automatyczna dokumentacja pod adresem http://localhost:8000/docs

Program do wyszukiwania używa funkcji bazującej na algorytmie wyszukiwania binarnego, co umożliwia nawet przy maksymalnej 
bazie uzyskanie czasu rzędu setnej części sekundy. Za odnaleziony uznaję taki rekord, któru jest siecią, w której 
zawiera się szukany `IP`. Wykonywane jest to za pomocą metody `ip_net.subnet_of(database[mid]["ip_network"])`.

Dla błędnie podanych adresów IP (np. `192.o.1.1 lub 300.280.10.20`), API zwraca kod błędu `status code 400 Bad Request` z opisem, np.:
- `INFO:     127.0.0.1:52468 - "GET /ip-tags/192.o.1.1 HTTP/1.1" 400 Bad Request`

  `{"detail":"Oops! '192.o.1.1' does not appear to be an IPv4 or IPv6 network"}`
  

- `INFO:     127.0.0.1:52470 - "GET /ip-tags/300.280.10.20 HTTP/1.1" 400 Bad Request` 

  `{"detail":"Oops! '300.280.10.20' does not appear to be an IPv4 or IPv6 network"}`

Dla poprawnie podanych adresów IP nie odnalezionych w bazie (np. `193.39.22.1 lub 100.140.10.20`), API zwraca kod błędu `status code 404 Not found` z opisem, np.:
- `INFO:     127.0.0.1:52462 - "GET /ip-tags/193.39.22.1 HTTP/1.1" 404 Not Found`
  
  `{"detail":"IP not found in database."}`


- `INFO:     127.0.0.1:52478 - "GET /ip-tags/100.140.10.20 HTTP/1.1" 404 Not Found`
  
  `{"detail":"IP not found in database."}`

----
## Dane testowe przygotowane z opisu:

```
[
  {"tag": "foo", "ip_network": "192.0.2.0/24"},
  {"tag": "{$(\n a-tag\n)$}", "ip_network": "192.168.7.0/24"},
  {"tag": "za\u017c\u00f3\u0142\u0107 \u2665", "ip_network": "192.168.7.0/24"},
  {"tag": "bar", "ip_network": "192.0.2.8/29"},
  {"tag": "bar", "ip_network": "10.20.0.0/16"},
  {"tag": "just a TAG", "ip_network": "192.168.7.0/24"},
  {"tag": "SPAM", "ip_network": "10.20.30.40/32"},
  {"tag": "bar", "ip_network": "10.20.0.0/16"},
  {"tag": "123 & abc & XYZ!", "ip_network": "10.20.0.0/16"}
]
```

Dodatkowo skryptem `create_test_knowledgebase.py` wygenerowałem `4 000 001` rekordów z ustawionym ziarnem dla modułu `random` - dane te są w pliku `test_knowledgebase.json.bz2` (należy go rozpakować `bzip2 -d test_knowledgebase.json.bz2` po pobraniu repozytorium). 

----
## Zmienne środowiskowe:
* `JSON_DEBUG`, domyślna wartość False, możliwe: False | True
* `JSON_LOGFILE`, domyślna wartość `nask.log`
* `JSON_DATABASE`, domyślna wartość `baza_wiedzy.json` (*zawiera kilka przykładowych wpisów stworzonych na podstawie dokumentacji zadania*)
* `ALLOW_DUPLICATE_TAGS`, domyślna wartość True, możliwe: False | True (*czy dozwalamy w liście tagów na duplikaty, jeśli podczas wyszukiwania natrafimy na różne definicje CIDR pasujące dla danego IP*)


TODO:
- testy
- Dane dostępowe - zadanie dostępne po uruchomieniu dockera  `docker-compose up` pod adresem: http://localhost:8000/ 

