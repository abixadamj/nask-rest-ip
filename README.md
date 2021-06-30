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

Dodatkowo dostępny jest API Endpoint `/status` dla celów sprawdzenia, oddaje różne informacje, np.:
```
{
  "system":["Linux","bf13737490dc","5.8.0-59-generic","#66~20.04.1-Ubuntu SMP Thu Jun 17 11:14:10 UTC 2021","x86_64"],
  "python":"3.9.5 (default, May 12 2021, 15:26:36) \n[GCC 8.3.0] - sys.version_info(major=3, minor=9, micro=5, releaselevel='final', serial=0)",
  "logfile":"nask.log",
  "knowledgebase":"baza_wiedzy.json",
  "total_entries":9,
  "__DEBUG__":true,
  "__ALLOW_DUPLICATE_TAGS__":false
}
```

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

## Docker
Polecenie `docker-compose up` uruchamia  kontener z ustawieniami domyślnymi:
- bazą `baza_wiedzy.json` z 9 pozycjami
- logowaniem w trybie `DEBUG` do pliku `nask.log`
- dozwolone duplikaty w liście tagów

Przykłady logów z uruchomionej aplikacji:

```
adasiek@devel ~/python_projekty/nask-rest-ip                                                                             [21:21:54] 
> $ docker exec bf13737490dc tail -f nask.log                                                                           [±task ●●●]
DEBUG:root:2021-06-30 19:13:56.188043 -> VIRT mem: svmem(total=24643485696, available=19829370880, percent=19.5, used=3922280448, free=16254357504, active=4763475968, inactive=2627391488, buffers=111607808, cached=4355239936, shared=522637312, slab=356974592)
DEBUG:asyncio:Using selector: EpollSelector
INFO:uvicorn.error:Started server process [1]
INFO:uvicorn.error:Waiting for application startup.
INFO:uvicorn.error:Application startup complete.
INFO:uvicorn.error:Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:root:2021-06-30 19:18:31.101099 -> Binary search: found index 1 in 0:00:00.000163.
DEBUG:root:2021-06-30 19:18:31.101403 -> first/last for build_tags_for search: 0 / 9
INFO:root:2021-06-30 19:18:31.101838 -> /ip-tags built for ipv4 10.20.30.40 - time: 0:00:00.000941
DEBUG:root:2021-06-30 19:18:31.102031 -> tags = ['bar', '123 & abc & XYZ!', 'SPAM']
INFO:root:2021-06-30 19:22:48.511631 -> Binary search: found index 1 in 0:00:00.000057.
DEBUG:root:2021-06-30 19:22:48.511788 -> first/last for build_tags_for search: 0 / 9
INFO:root:2021-06-30 19:22:48.511943 -> /ip-tags built for ipv4 10.20.30.44 - time: 0:00:00.000385
DEBUG:root:2021-06-30 19:22:48.512035 -> tags = ['bar', '123 & abc & XYZ!']
INFO:root:2021-06-30 19:23:08.868411 -> /ip-tags-report built for ipv4 10.20.30.44 - time: 0:00:00.000024
DEBUG:root:2021-06-30 19:23:08.868530 -> tags = ['bar', '123 & abc & XYZ!']
```




TODO:
- testy
 

