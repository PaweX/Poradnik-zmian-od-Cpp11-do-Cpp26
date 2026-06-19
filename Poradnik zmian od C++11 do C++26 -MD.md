# C++11
## Cele projektowe C++11:

**Komitet projektowy starał się trzymać kilku kluczowych założeń:**

* Zachowanie stabilności i kompatybilności ze starszym kodem
* Wprowadzanie nowych możliwości przede wszystkim przez bibliotekę standardową, a nie przez rozszerzanie samego języka
* Usprawnianie C++ tak, by lepiej nadawał się do projektowania systemów i bibliotek, a nie tylko do konkretnych aplikacji
* Zwiększenie bezpieczeństwa typów poprzez bezpieczniejsze alternatywy dla wcześniejszych niebezpiecznych idiomów
* Zwiększenie wydajności i możliwości bezpośredniej pracy z hardware’em
* Dostarczanie właściwych rozwiązań dla realnych problemów
* Ułatwienie nauczania i nauki C++ bez odbierania zaawansowanym programistom potrzebnych im mechanizmów

Duża uwaga poświęcona została początkującym, ponieważ większość programistów zawsze będzie na poziomie „średnio-zaawansowanym / początkującym”, a wielu nigdy nie poszerza swojej wiedzy poza wąski wycinek języka, w którym się specjalizują.

## Rozszerzenia rdzenia języka C++ (core language)

Jednym z głównych zadań komitetu standaryzacyjnego C++ jest rozwój **rdzenia języka**. W standardach od C++11 wzwyż znacząco ulepszono m.in.:

* wsparcie dla **wielowątkowości**,
* wsparcie dla **programowania generycznego**,
* **jednolitą inicjalizację**,
* oraz **wydajność wykonania**.

***

### Poprawki wydajności w czasie wykonywania (runtime)

Poniższe funkcje językowe powstały głównie po to, aby poprawić **wydajność czasu wykonania** — zarówno pod względem zużycia pamięci, jak i szybkości obliczeń.

***

#### Referencje do r‑wartości (rvalue references) i konstruktory przenoszące (move constructors)

##### Tło: jak było w C++03

W C++03 (i wcześniejszych standardach) obiekty tymczasowe — czyli tzw. **r‑wartości** (_rvalues_, bo zwykle pojawiają się po prawej stronie przypisania) — były traktowane tak, jakby miały typ `const T&`.

W praktyce oznaczało to:

* **nie można było ich modyfikować** (przynajmniej w założeniach języka),
* kompilator **nie rozróżniał** ich od zwykłych referencji do stałych (`const T&`),
* w pewnych sytuacjach **dało się je jednak modyfikować** — co było niezamierzoną, ale czasem wykorzystywaną „furtką” językową.

Największy problem: **kosztowne i niepotrzebne głębokie kopiowanie**, które mogło zdarzyć się automatycznie przy przekazywaniu obiektów przez wartość.

***

##### Dlaczego kopiowanie było problemem?

Weźmy `std::vector<T>`. Wewnątrz przechowuje on:

* wskaźnik do tablicy dynamicznej,
* rozmiar,
* pojemność.

W C++03, jeśli funkcja zwracała `std::vector<T>` **przez wartość**, to wyglądało to tak:

1. tworzony był obiekt tymczasowy (r‑wartość),
2. następnie tworzono nowy `std::vector<T>` w miejscu docelowym,
3. **kopiowano wszystkie elementy** z tymczasowego wektora,
4. niszczono obiekt tymczasowy i jego pamięć.

To oznaczało:

* **dużo alokacji**,
* **dużo kopiowania**,
* **dużo czasu straconego na operacje, które nie były potrzebne**.

> **Uwaga:** w C++03 istniała optymalizacja RVO/NRVO (Return Value Optimization), która czasem usuwała to kopiowanie — ale **nie zawsze działała** i nie można było na niej polegać.

***

##### C++11: referencja do r-wartości (`T&&`) i semantyka przenoszenia (move semantics)

C++11 wprowadza nowy typ referencji: **rvalue reference**, zapisywany jako `T&&`.

Pozwala on:

* rozpoznać obiekty tymczasowe,
* **przenosić** zasoby zamiast je kopiować.

##### Jak działa przenoszenie?

Dla `std::vector<T>` konstruktor przenoszący:

* przejmuje wskaźnik do tablicy z obiektu tymczasowego,

* ustawia wskaźnik w obiekcie źródłowym na `nullptr`,

* dzięki temu:

  * nie ma kopiowania elementów,
  * tymczasowy obiekt nie zwolni pamięci (bo ma `nullptr`),
  * operacja jest szybka i bezpieczna.

***

##### Automatyczne użycie move

Jeśli funkcja zwraca `std::vector<T>` przez wartość:

```cpp
std::vector<int> makeVec()
{
    return {1, 2, 3};
}
```

to:

* obiekt tymczasowy jest **rvalue**,
* kompilator automatycznie użyje **konstruktora przenoszącego**,
* nie trzeba zmieniać sygnatury funkcji na `std::vector<T>&&` ani pisać dodatkowego kodu.

**Co dokładnie robi konstruktor przenoszący?**
Konstruktor przenoszący `std::vector<T>` może **przenieść** wskaźnik do wewnętrznej tablicy (C‑style array) z obiektu tymczasowego do nowego obiektu docelowego, a następnie ustawić wskaźnik w obiekcie tymczasowym na `nullptr`. Ponieważ obiekt tymczasowy nie będzie już używany, nikt nie spróbuje odczytać tego `nullptr`, a pamięć nie zostanie zwolniona przy jego zniszczeniu. Dzięki temu operacja **omija kosztowne głębokie kopiowanie** i jest bezpieczna oraz niewidoczna dla użytkownika.

> **Uwaga praktyczna:** jeśli używasz starej wersji biblioteki (implementacji zgodnej tylko z C++03), która nie ma konstruktorów przenoszących, wtedy zamiast przeniesienia nastąpi **kopiowanie** (wywołanie konstruktora kopiującego na `const std::vector<T>`), co wiąże się z alokacją pamięci i kopiowaniem elementów.

***

##### `std::move`

* **Nazwane zmienne nigdy nie są rvalue**, nawet jeśli zadeklarowano je jako `T&&`.
* Aby wymusić traktowanie nazwanej zmiennej jak rvalue (czyli umożliwić przeniesienie jej zasobów), używamy:

```cpp
std::move(x);
```

* `std::move` **nie wykonuje przeniesienia** — ono tylko **konwertuje** (poprzez `static_cast`) obiekt do rvalue, co pozwala wywołać konstruktor przenoszący lub operator przenoszący.

**Dodatkowe uwagi o bezpieczeństwie:**

* Po przeniesieniu obiekt źródłowy pozostaje w stanie **określonym, ale nieokreślonym co do wartości** (ang. _valid but unspecified_). Oznacza to, że można go bezpiecznie zniszczyć lub przypisać do niego nową wartość, ale nie należy polegać na jego zawartości.
* Rvalue references są projektowane głównie do obsługi konstruktorów i operatorów przenoszących; modyfikowanie obiektu po przeniesieniu wymaga ostrożności.

Przykład praktyczny:
```cpp
std::string s = "Hello";
std::string t = std::move(s);

// Co jest w s?
// Nie wiadomo. Może być "", może być "Hello", może być coś innego.
// Ale s musi być valid — możesz zrobić:
s = "Nowa wartość";  // OK
```
Najkrótsza możliwa definicja:

> **Obiekt po przeniesieniu jest w stanie poprawnym, ale jego wartości nie wolno używać do żadnych założeń. Możesz go zniszczyć lub nadpisać, ale nie polegać na tym, co w nim zostało.**

***

##### Podsumowanie

###### Po co w ogóle przenosić?

Żeby **uniknąć kosztownego kopiowania dużych zasobów**.

Kopiowanie:

* alokuje nową pamięć,
* kopiuje dane bajt po bajcie,
* jest wolne.

Przenoszenie:

* **zabiera** zasób z obiektu źródłowego,
* **nie kopiuje** danych,
* jest ekstremalnie szybkie (często tylko kilka instrukcji).

To jest różnica między:

* kopiowaniem 1 GB danych,
* a przestawieniem jednego wskaźnika.

###### Skąd dokąd się przenosi?

Z **obiektu źródłowego** → do **obiektu docelowego**, zwykle:

* z tymczasowego obiektu (rvalue)

np. `std::string("duży tekst")`

* z obiektu, którego już nie potrzebujesz

np. `std::move(x)`

* z elementu kontenera do innego miejsca

np. podczas `std::vector::push_back`, `emplace_back`, `resize`, `reserve`

**Najprostszy przykład:**
```cpp
std::string s = "bardzo duży tekst...";
std::string t = std::move(s);
```

Co się dzieje?

* `t` **przejmuje** wskaźnik do bufora `s`.
* `s` zostaje w stanie „valid but unspecified”.
* **Nie skopiowano ani jednego znaku**.

To jest powód, dla którego przenoszenie istnieje.

###### Dlaczego nie kopiować?

Wyobraź sobie kontener:

```cpp
std::vector<std::string> v;
v.push_back("bardzo duży tekst...");
```

Gdy `vector` się powiększa, musi przenieść wszystkie elementy do nowej pamięci.

Gdyby robił to kopiowaniem:

* każdy element byłby kopiowany,
* każda kopia to alokacja + kopiowanie danych,
* byłoby to _koszmarnie wolne_.

Dzięki przenoszeniu:

* `vector` tylko **przesuwa wskaźniki**,
* operacje są szybkie,
* nie ma zbędnych kopii.

###### Przenoszenie jest fundamentem nowoczesnego C++

Bez przenoszenia:

* `std::vector` byłby wolny,
* `std::string` byłby wolny,
* `std::unique_ptr` nie mógłby istnieć,
* `std::optional`, `std::variant`, `std::function` byłyby niepraktyczne,
* biblioteka standardowa byłaby 10× wolniejsza.

Przenoszenie umożliwia:

* RAII,
* zero-cost abstractions,
* nowoczesne API,
* bezpieczne zarządzanie zasobami.

**Najkrótsza odpowiedź**:

> **Przenoszenie pozwala przekazać zasoby z jednego obiektu do drugiego bez kopiowania.
> Jest używane wszędzie tam, gdzie kopiowanie byłoby zbyt wolne lub niemożliwe.

***
_Zobacz też:_
* **`std::move` - czy mogę przenieść obiekt lokalny do globalnego?**
***

##### Perfect forwarding

Połączenie **referencji do r‑wartości** z pewnymi zmianami w semantyce referencji w kontekście szablonów umożliwiło tzw. **perfect forwarding** (**doskonałe przekierowywanie**).

* W praktyce oznacza to, że funkcja szablonowa może **przekazać dalej** otrzymane argumenty do innej funkcji **bez utraty ich kategorii wartości** (czyli bez „zgniecenia” R-value do L-value lub odwrotnie).

* Mechanizm ten wykorzystuje:

  * **forwarding references** (dawniej nazywane _universal references_): parametry szablonowe zadeklarowane jako `T&&` w kontekście dedukcji typu,
  * `std::forward<T>(arg)` do zachowania oryginalnej kategorii wartości przy przekazywaniu.

**Dlaczego to jest przydatne?**
Umożliwia tworzenie funkcji fabrycznych i konstruktorów pomocniczych, które wywołują właściwy konstruktor docelowego typu bez niepotrzebnych kopii. Przykłady w bibliotece standardowej: `emplace_back`, `std::make_unique`, `std::make_shared` — wszystkie korzystają z perfect forwarding, aby przekazać argumenty bezpośrednio do odpowiedniego konstruktora elementu.

***

##### Podsumowanie techniczne (ważne fakty)

* **Temporaries (tymczasowe obiekty)** są automatycznie rvalue — nie trzeba zmieniać typu zwracanego funkcji na `&&`, aby wywołać konstruktor przenoszący.
* **Konstruktor przenoszący** może „ukraść” zasoby (np. wskaźnik do bufora) i ustawić źródło w stanie bezpiecznym (np. `nullptr`), co eliminuje kosztowną alokację i kopiowanie.
* **`std::move`** to narzędzie do konwersji nazwanej zmiennej na rvalue; samo w sobie nie przenosi zasobów.
* **Perfect forwarding** (w połączeniu z szablonami wariadycznymi) pozwala pisać ogólne funkcje, które przekazują argumenty dalej bez strat wydajnościowych.

***

#### `constexpr` – uogólnione wyrażenia stałe

C++ od zawsze rozróżniał **wyrażenia stałe** — wyrażenia, których wartość jest znana i może być obliczona w czasie kompilacji i w czasie wykonywania, np. `3 + 4`. Wyrażenia stałe są okazją do optymalizacji: kompilatory często **wykonują je podczas kompilacji** i **wstawiają wynik na stałe** do wygenerowanego kodu. Ponadto specyfikacja C++ wymaga użycia wyrażeń stałych w niektórych kontekstach (np. przy określaniu rozmiaru tablicy statycznej czy przy wartościach enumeratorów).

***

##### Problem w C++03

W C++03 nie można było używać wywołań funkcji ani konstruktorów w wyrażeniach stałych, ponieważ kompilator nie miał gwarancji, że funkcja jest rzeczywiście stała:

```cpp
int pobierzTrzy() { return 3; }

int jakasTablica[pobierzTrzy() + 7]; // Utwórz tablicę 10 elementów typu int. Niepoprawny C++ (ill-formed)
```

To nie było poprawne w C++03, ponieważ `pobierzTrzy() + 7` nie jest wyrażeniem stałym. Kompilator C++03 nie miał sposobu, by stwierdzić, czy `pobierzTrzy()` jest rzeczywiście stałe w czasie kompilacji — w teorii taka funkcja mogłaby modyfikować zmienną globalną, wywoływać inne funkcje zależne od stanu programu lub wykonywać operacje niedozwolone w kontekście kompilacyjnym.

***

##### C++11: słowo kluczowe `constexpr`

C++11 wprowadził `constexpr`, które pozwala oznaczyć funkcję, konstruktor lub zmienną jako **możliwą do ewaluacji w czasie kompilacji**:

```cpp
constexpr int pobierzTrzy() { return 3; }

int jakasTablica[pobierzTrzy() + 7]; // Utwórz tablicę 10 elementów typu int. Poprawny C++11
```

Dzięki `constexpr` kompilator może zrozumieć i zweryfikować, że `pobierzTrzy()` jest stałą w czasie kompilacji, i obliczyć jej wynik wtedy, gdy kontekst tego wymaga.

***

##### Co narzuca `constexpr` (wersja C++11) i jak to się rozwinęło

**C++11** — ograniczenia dla funkcji `constexpr`:

* Funkcja `constexpr` **musi** mieć typ zwracany inny niż `void`.
* Ciało funkcji `constexpr` **nie może** deklarować zmiennych lokalnych ani definiować nowych typów; może zawierać tylko deklaracje, puste instrukcje i **jedną** instrukcję `return`.
* Musi istnieć zestaw argumentów, dla których po podstawieniu argumentów wyrażenie w instrukcji `return` daje wyrażenie stałe.

**Przed C++11** wartości zmiennych mogły być używane w wyrażeniach stałych tylko wtedy, gdy były zadeklarowane jako `const`, miały inicjalizator będący wyrażeniem stałym i były typu całkowitego lub wyliczeniowego. **C++11** usunął ograniczenie dotyczące typu — jeśli zmienna jest zadeklarowana jako `constexpr`, nie musi być typu całkowitego ani wyliczeniowego.

**Ewolucja w kolejnych standardach:**

* **C++14** — reguły zostały znacznie poluzowane: `constexpr` może zawierać zmienne lokalne, pętle i instrukcje warunkowe, co pozwala pisać bardziej „normalne” funkcje, które nadal mogą być ewaluowane w czasie kompilacji.
* **C++17** — dodano `if constexpr`, ułatwiające warunkowe generowanie kodu w szablonach (kompilacyjny branching).
* **C++20** — `constexpr` stało się jeszcze bardziej elastyczne; wprowadzono dodatkowo **`consteval`** (funkcja, która **musi** być wykonana w czasie kompilacji) oraz **`constinit`** (zapewnia inicjalizację statyczną bez ukrytej dynamicznej inicjalizacji).

***

##### (C++14): poluzowane ograniczenia `constexpr`

W C++11 funkcje oznaczone jako `constexpr` mogły zawierać jedynie pojedyncze wyrażenie zwracane (`return expression;`), a także `static_assert` i kilka prostych deklaracji.  
C++14 znacząco rozszerza możliwości funkcji `constexpr`, pozwalając wykonywać w czasie kompilacji znacznie bardziej złożone operacje.

Od C++14 funkcje `constexpr` mogą zawierać:

* **Dowolne deklaracje**, z wyjątkiem:
  * zmiennych `static` lub `thread_local`,
  * deklaracji zmiennych bez inicjalizatora.

* **Instrukcje warunkowe**: `if`, `switch`.

* **Pętle**, w tym pętle `for`, `while`, a także pętlę po zakresie (`range‑based for`).

* **Instrukcje modyfikujące obiekty**, pod warunkiem że:
  * obiekt powstał w trakcie ewaluacji stałej (`constexpr`),
  * oraz jego czas życia rozpoczął się w obrębie funkcji `constexpr`.

  Obejmuje to również wywołania nie‑`const` metod oznaczonych jako `constexpr`.

Instrukcja `goto` pozostaje zabroniona w funkcjach `constexpr`.

W C++11 wszystkie niestatyczne metody oznaczone jako `constexpr` były **implicitnie `const`** względem `this`.  
C++14 usuwa to ograniczenie — metody `constexpr` mogą być nie‑`const`.  
Jednak zgodnie z powyższymi zasadami, mogą modyfikować tylko te obiekty, których czas życia rozpoczął się w trakcie ewaluacji stałej.

Poluzowanie ograniczeń `constexpr` w C++14 umożliwia tworzenie bardziej złożonych algorytmów wykonywanych w czasie kompilacji, co stanowi fundament dla dalszych rozszerzeń w C++17 i C++20.

***

##### Różnica między `constexpr` i `consteval` oraz `constinit`

* **`constexpr`** — funkcja, konstruktor lub zmienna **może** być ewaluowana w czasie kompilacji, ale nie jest to obowiązkowe. Jeśli wywołanie ma nie‑stałe argumenty lub kontekst nie wymaga ewaluacji w czasie kompilacji, zachowuje się jak zwykła funkcja wykonywana w czasie działania programu (runtime).  
* **`consteval`** — wywołanie **zawsze** musi być obliczone w czasie kompilacji; wywołanie w kontekście runtime powoduje błąd kompilacji. 
* **`constinit`** — specyfikator dla zmiennych statycznych/plikowych, który **gwarantuje** inicjalizację w czasie kompilacji (statyczną) i zapobiega ukrytej, późnej inicjalizacji dynamicznej; `constinit` nie czyni zmiennej `const`.

Przykład `consteval`:
```cpp
// funkcja musi być ewaluowana w czasie kompilacji
consteval int kwadrat(int x) { return x * x; }

constexpr int a = kwadrat(3); // OK — wywołanie wykonane w czasie kompilacji
int b = kwadrat(4); // Błąd kompilacji: kwadrat() musi być wywołane w czasie kompilacji
```

Przykład `constexpr`:
```cpp
// może być ewaluowane w czasie kompilacji, ale nie musi
constexpr int dodaj(int x, int y) { return x + y; }

int main()
{
    constexpr int c = dodaj(2, 3); // ewaluacja w czasie kompilacji — c == 5
    int p = 10, q = 20;
    int d = dodaj(p, q); // wywołanie w czasie wykonywania — d obliczone w runtime
}
```

Przykład `constinit`:
```cpp
// gwarantuje inicjalizację statyczną, ale nie czyni zmiennej const
constinit int licznik_globalny = 0; // musi być zainicjalizowane statycznie
licznik_globalny = 5; // dozwolone — constinit nie oznacza const
```

**Dodatkowe uwagi praktyczne**

- `constexpr` jest elastyczne i przydatne, gdy chcemy, aby funkcja lub wartość była użyteczna zarówno w kontekstach kompilacyjnych, jak i w runtime.  
- `consteval` stosujemy, gdy wynik **zawsze** musi być znany na etapie kompilacji (np. generowanie stałych parametrów szablonów, walidacje kompilacyjne).  
- `constinit` używamy dla zmiennych statycznych, które muszą być zainicjalizowane w fazie inicjalizacji statycznej programu (bardzo wczesny etap uruchamiania programu w C++, zanim jeszcze zacznie się wykonywanie funkcji main() ), aby uniknąć problemów z kolejnością inicjalizacji (static initialization order fiasco), ale gdy chcemy móc je modyfikować później.  
- `constinit` nie zastępuje `constexpr` — można użyć obu razem tylko wtedy, gdy sens ma jednoczesna statyczna inicjalizacja i stałość (choć `constexpr` zmienna jest już `const`, więc `constinit` z `constexpr` zwykle nie ma sensu).

**Kiedy kompilator wykona ewaluację w czasie kompilacji?**

- Kontekst wymuszający ewaluację: inicjalizacja `constexpr`, rozmiar tablicy wymagający wyrażenia stałego, wartość parametru szablonu nie‑typowego (non-type template parameter), lub inne miejsca, gdzie specyfikacja wymaga wyrażenia stałego.  
- Jeśli kontekst nie wymaga ewaluacji, `constexpr` funkcja może zostać wykonana w runtime; `consteval` nigdy nie — każde wywołanie musi być skompilowane.

**Błędy i diagnostyka**

- Wywołanie `consteval` poza kontekstem kompilacyjnym generuje błąd kompilacji.  
- Wywołanie `constexpr` z argumentami, które nie dają wyrażenia stałego, nie jest błędem — po prostu wynik nie będzie wyrażeniem stałym i obliczenie nastąpi w runtime.  
- `constinit` spowoduje błąd, jeśli inicjalizacja nie jest statyczna (tj. nie może być wykonana w fazie inicjalizacji statycznej).
  
***

##### Zmienne constexpr

Przed C++11 tylko stałe integralne mogły być używane w stałych wyrażeniach.

C++11 pozwala:

```cpp
constexpr double PRZYSPIESZENIE_GRAWITACYJNE_ZIEMI = 9.8;
constexpr double PRZYSPIESZENIE_GRAWITACYJNE_KSIEZYCA = PRZYSPIESZENIE_GRAWITACYJNE_ZIEMI / 6.0;
```

Zmienne `constexpr`:

* Zmienne oznaczone `constexpr` są **zawsze `const`** i muszą mieć inicjalizator będący stałym wyrażeniem.
* Dzięki C++11 można definiować `constexpr` zmienne nie tylko całkowite.

***

##### `constexpr` dla typów użytkownika i dodatkowe wymagania

* Konstruktory mogą być oznaczone jako `constexpr`, co pozwala tworzyć obiekty typu użytkownika w czasie kompilacji — pod warunkiem, że spełniają wszystkie wymagania `constexpr` obowiązujące w danym standardzie.
* W C11 ciało konstruktora `constexpr` mogło zawierać **wyłącznie deklaracje i puste instrukcje** (czyli nie mogło zawierać instrukcji wykonawczych, deklaracji zmiennych lokalnych ani definicji typów). Od C14/C++20 ograniczenia te zostały znacząco poluzowane.
* Destruktory typów, które mają być używane w kontekście wyrażeń stałych, **muszą być trywialne** — czyli takie, które **nie mają własnego ciała**, **nie wykonują żadnego kodu**, **nie zwalniają zasobów**, **nie są zdefiniowane przez użytkownika**, a ich implementację generuje automatycznie kompilator. Trywialny destruktor jest „pusty” i może zostać całkowicie pominięty podczas ewaluacji kompilacyjnej.
* **Konstruktor kopiujący**, a także inne funkcje członkowskie (np. operatory), w typie posiadającym konstruktory `constexpr` **zwykle również powinny być oznaczone jako `constexpr`**, aby umożliwić zwracanie obiektów przez wartość z funkcji `constexpr` oraz wykonywanie operacji na tych obiektach w czasie kompilacji. Bez tego obiekt mógłby „stracić constexpr‑owość” podczas kopiowania lub operacji.

Przykład:

```cpp
struct Wektor2
{
    double x, y;

    // Konstruktor constexpr — może być używany w czasie kompilacji
    constexpr Wektor2(double x, double y)
        : x(x), y(y)
    {
        // W C++11 ciało konstruktora constexpr nie mogło zawierać
        // żadnych instrukcji wykonawczych — tylko inicjalizator i puste instrukcje.
    }

    // Funkcja członkowska constexpr — może być ewaluowana w czasie kompilacji
    constexpr double norma2() const
    {
        return x * x + y * y;
    }
};
```

**Ograniczenia (C++11):**

* ciało konstruktora `constexpr` może zawierać tylko deklaracje i puste instrukcje,
* destruktor musi być trywialny (czyli generowany automatycznie, bez kodu wykonywalnego).

> Od C14 i C20 zasady są znacznie luźniejsze — można używać zmiennych lokalnych, pętli, instrukcji warunkowych, a destruktory nie muszą już być trywialne, o ile spełniają wymagania ewaluacji kompilacyjnej.

**Zachowanie wywołań `constexpr` z nie‑stałymi argumentami**

Jeżeli funkcja lub konstruktor `constexpr` zostanie wywołany z argumentami, które **nie są** wyrażeniami stałymi, to wywołanie zachowuje się tak, jakby funkcja nie była `constexpr` — jest wykonywane w czasie wykonywania programu, a wynik **nie** jest wyrażeniem stałym. Podobnie, jeśli po podstawieniu argumentów wyrażenie w instrukcji `return` nie daje wyrażenia stałego, wynik nie jest stały.

**Praktyczne przykłady:**

**C++14 pętla w `constexpr`:**
```cpp
constexpr int factorial(int n)
{
    int r = 1;
    for (int i = 2; i <= n; ++i) r *= i;
    return r;
}
constexpr int f6 = factorial(6); // OK w C++14+
```

**C++17 if constexpr:**
```cpp
template<typename T>
constexpr auto id(T x)
{
    if constexpr (std::is_integral_v<T>) return x + 1;
    else return x;
}
```

**C++20 consteval:**
```cpp
consteval int sq(int x) { return x * x; }
constexpr int a = sq(3); // OK
// int b = sq(4); // błąd: sq musi być wywołane w czasie kompilacji
```

**Uwaga o rzeczywistej ewaluacji**

Nawet jeśli funkcja jest oznaczona `constexpr`, kompilator wykona jej obliczenie w czasie kompilacji **tylko wtedy, gdy kontekst tego wymaga** (np. inicjalizacja `constexpr`, rozmiar tablicy, wartość non-type template parameter). `consteval` natomiast wymusza kompilacyjną ewaluację.

**Krótkie podsumowanie**

* **`constexpr`** umożliwia definiowanie funkcji, konstruktorów i zmiennych, które **mogą** być obliczane w czasie kompilacji; reguły były stopniowo poluzowywane od C11 do C20.
* **`consteval`** (C++20) wymusza kompilacyjną ewaluację.
* Mechanizmy `constexpr` i pokrewne są fundamentem wydajnego metaprogramowania, bezpiecznej inicjalizacji statycznej i optymalizacji w nowoczesnym C++.

***

#### Modyfikacja definicji typu POD (plain old data)

W C++03 klasa, struktura lub `union` musiały spełniać wiele sztywnych zasad, aby zostać uznane za **POD** (plain old data).

Typy POD:

* **miały układ pamięci zgodny z językiem C**,
* mogły być **statycznie inicjalizowane**,
* mogły być bezpiecznie kopiowane za pomocą `memcpy`.

Problem polegał na tym, że zasady były **zbyt restrykcyjne**.
Przykład:

Jeśli ktoś miał poprawny typ POD w C++03 i dodał do niego **jedną funkcję wirtualną**, to:

* typ przestawał być POD,
* nie mógł być statycznie inicjalizowany,
* tracił zgodność z C,

mimo że **układ pamięci wcale się nie zmieniał**.

***

C++11 rozwiązał ten problem, dzieląc pojęcie POD na dwa osobne pojęcia:

* **trivial** (typ trywialny),
* **standard-layout** (typ o standardowym układzie pamięci).

Dzięki temu można mieć typ zgodny z C, ale niekoniecznie trywialny — albo odwrotnie.

***

##### Typ _trivial_ (trywialny)

Typ trywialny:

* może być **statycznie inicjalizowany**,
* można go kopiować przez `memcpy`,
* jego „czas życia” zaczyna się, gdy tylko pamięć zostanie przydzielona (nie czeka na wykonanie konstruktora).

Aby klasa/struct/union była **trivial**, musi:

1. Mieć trywialny konstruktor domyślny (może być `= default;`).
2. Mieć trywialne konstruktory kopiujące i przenoszące.
3. Mieć trywialne operatory przypisania (kopiujące i przenoszące).
4. Mieć trywialny destruktor (nie może być wirtualny).

Dodatkowe zasady:

* konstruktor jest trywialny tylko wtedy, gdy klasa **nie ma funkcji wirtualnych** i **nie ma wirtualnych klas bazowych**,
* operacje kopiowania/przenoszenia są trywialne tylko wtedy, gdy **wszystkie pola niestatyczne** są trywialne.

***

##### Typ _standard-layout_ (standardowy układ pamięci)

Typ standard-layout ma układ pamięci zgodny z językiem C.
Klasa/struct/union jest standard-layout, jeśli:

1. Nie ma funkcji wirtualnych.
2. Nie ma wirtualnych klas bazowych.
3. Wszystkie jej pola niestatyczne mają **ten sam poziom dostępu** (wszystkie publiczne, albo wszystkie prywatne itd.).
4. Wszystkie pola niestatyczne, włącznie z odziedziczonymi, znajdują się w **tej samej klasie** w hierarchii (tzn. nie są rozproszone po różnych poziomach w sposób łamiący regułę).
5. Te zasady muszą być spełnione również przez wszystkie klasy bazowe.
6. Nie ma klasy bazowej tego samego typu, co pierwsze zdefiniowane pole niestatyczne.

***

##### Kiedy typ jest POD?

W C++11 typ (class/struct/union) jest POD, jeśli:

* jest **trivial**,
* jest **standard-layout**,
* wszystkie jego pola niestatyczne i klasy bazowe również są POD.

***

##### Dlaczego to rozdzielono?

Dzięki temu można mieć:

* typ **standard-layout**, ale nie trywialny
  (np. ma skomplikowany konstruktor, ale układ pamięci zgodny z C),

* typ **trivial**, ale nie standard-layout
  (np. ma pola publiczne i prywatne, ale nadal można go kopiować `memcpy`).

To daje programiście dużo większą elastyczność niż w C++03.

***

##### Krótkie przykłady: różnica między typem _trivial_ a _standard-layout_

Poniższe przykłady pokazują, że:

* typ może być **trywialny**, ale **nie** mieć standardowego układu pamięci,
* typ może mieć **standardowy układ pamięci**, ale **nie** być trywialny.

**Przykład 1 — typ trywialny **i** standard-layout**
```cpp
struct Punkt
{
    int wspolrzednaX;
    int wspolrzednaY;
};
// Konstruktor domyślny, kopiujący, przenoszący i destruktor są generowane
// automatycznie i są trywialne. Układ pamięci jest zgodny z C.
```

**Przykład 2 — typ standard-layout, ale _nietrywialny_**
```cpp
struct TypStandardLayoutAleNietrywialny
{
    int poleA;
    int poleB;

    ~TypStandardLayoutAleNietrywialny()
    {
        // Użytkownik zdefiniował destruktor → destruktor nie jest trywialny.
    }
};
// Układ pamięci nadal jest zgodny z C, ale typ nie jest trywialny.
```

**Przykład 3 — typ trywialny, ale **nie** standard-layout**
```cpp
struct TypTrywialnyAleNieStandardLayout
{
public:
    int polePubliczne;

private:
    int polePrywatne;
};
// Wszystkie specjalne funkcje są trywialne, ale różne poziomy dostępu pól
// łamią zasady standard-layout.
```

***

### Ulepszenia wydajności kompilacji w rdzeniu języka

#### `extern template`

W C++03 kompilator **musi** instancjonować szablon za każdym razem, gdy w danej jednostce kompilacji pojawia się jego pełna specjalizacja.
Jeśli ten sam szablon jest używany w wielu plikach `.cpp`, to:

> kompilator generuje jego kod **w każdym pliku osobno**, co może **drastycznie wydłużyć czas kompilacji**.

W C++03 nie dało się temu zapobiec.

C++11 wprowadził rozwiązanie: **`extern template`**, działające podobnie jak `extern` przy zmiennych.

W C++03 wymuszenie instancjonowania wyglądało tak:

```cpp
template class std::vector<MyClass>;
```

W C++11 można napisać:

```cpp
extern template class std::vector<MyClass>;
```

co mówi kompilatorowi:

> „Nie instancjonuj tego szablonu w tym pliku — instancjonacja będzie gdzie indziej”.

To pozwala znacząco skrócić czas kompilacji dużych projektów.

***

### Ulepszenia użyteczności rdzenia języka

Te funkcje mają przede wszystkim **ułatwić korzystanie z języka** — poprawić czytelność, bezpieczeństwo typów i zmniejszyć powtarzalność kodu.

#### Listy inicjalizacyjne

##### Listy inicjalizacyjne w C++03

C++03 odziedziczył listy inicjalizacyjne z języka C.
Struktura lub tablica otrzymuje listę wartości w nawiasach klamrowych `{}`, w kolejności zgodnej z definicją pól w strukturze.
Listy inicjalizacyjne są rekurencyjne — więc tablica struktur lub struktura zawierająca inne struktury może z nich korzystać.

Przykład:

```cpp
struct FloatOrazInt
{
    float pierwsza;
    int druga;
};

FloatOrazInt skalar = { 0.43f, 10 }; // Jeden obiekt, z pierwsza = 0.43f i druga = 10

FloatOrazInt tablicaObiektow[] =
{
    { 13.4f, 3 }, { 43.28f, 29 }, { 5.934f, 17 } // Tablica trzech obiektów
};
```

To jest bardzo przydatne do statycznych list lub inicjalizacji struktury do pewnej wartości.
C++ oferuje też konstruktory do inicjalizacji obiektów, ale często nie są one tak wygodne jak listy inicjalizacyjne.

Jednak w C++03 listy inicjalizacyjne działały **tylko** dla struktur/klas zgodnych z definicją POD (plain old data).

***

##### C++11: listy inicjalizacyjne dla wszystkich klas

W C++11 listy inicjalizacyjne zostały rozszerzone i mogą być używane dla **wszystkich typów**, w tym:

* klas z konstruktorami,
* kontenerów standardowej biblioteki (`std::vector`, `std::map`, …),
* typów użytkownika.

Mechanizm opiera się na szablonie:

```cpp
std::initializer_list<T>
```

Można go użyć w konstruktorze:

```cpp
using std::initializer_list;

class KlasaSekwencji
{
public:
    KlasaSekwencji(initializer_list<int> lista);
};
```

Dzięki temu można tworzyć obiekty w prosty sposób:

```cpp
KlasaSekwencji jakasSekwencja = { 1, 4, 5, 6 };
```

Taki konstruktor nazywa się **konstruktorem listy inicjalizacyjnej** (initializer-list constructor)
i ma specjalne znaczenie podczas tzw. **jednolitej inicjalizacji** (uniform initialization).

***

##### Czym jest `std::initializer_list`?

`std::initializer_list` to pełnoprawny typ biblioteczny w C++11.

Cechy:

* kompilator potrafi tworzyć go automatycznie z `{}` bez podawania typu,
* można go tworzyć jawnie:

```cpp
std::initializer_list<int> lista { 1, 2, 3 };
```

* kopiowanie jest tanie — zwykle implementacja to para wskaźników (`begin`, `end`),
* elementy są **stałe** — nie można ich modyfikować ani przenosić.

***

##### Użycie w zwykłych funkcjach

Nie tylko konstruktory mogą przyjmować `initializer_list`.
Zwykłe funkcje również:

```cpp
using std::initializer_list;

void nazwaFunkcji(initializer_list<float> lista); // Kopiowanie jest tanie; patrz wyżej

nazwaFunkcji({ 1.0f, -3.45f, -0.4f });
```

Standardowe funkcje `std::min` i `std::max` mają wersje przyjmujące `initializer_list`.

***

##### Inicjalizacja kontenerów STL

Od C++11 można wygodnie inicjalizować kontenery standardowe:

```cpp
using std::string;
using std::vector;

vector<string> wektor1 = { "xyzzy", "blabla", "abrakadabra" };
vector<string> wektor2 = vector<string>({ "xyzzy", "blabla", "abrakadabra" });
vector<string> wektor3{ "xyzzy", "blabla", "abrakadabra" }; // zobacz „Ujednolicona inicjalizacja”
```

To ogromne ułatwienie w porównaniu z C++03, gdzie trzeba było ręcznie wywoływać `push_back`.

***

#### Ujednolicona inicjalizacja (Uniform initialization)

C++03 miał wiele problemów związanych z inicjalizacją typów. Istnieje kilka sposobów, aby to zrobić, a niektóre z nich dają różne rezultaty, jeśli zamieni się je miejscami. Tradycyjna składnia konstruktora, na przykład, może wyglądać jak deklaracja funkcji, i trzeba podejmować dodatkowe kroki, aby kompilator — zgodnie z zasadą **most vexing parse** — nie pomylił jej z taką deklaracją.

W C++03 tylko typy \*\*POD\*\* i agregaty mogły być inicjalizowane listami `{ ... }`:
```cpp
JakisTyp zmienna = { /* wartości */ };
```

C++11 wprowadza **ujednoliconą inicjalizację**, która działa dla każdego typu — zarówno struktur, jak i klas z konstruktorami. Rozszerza ona składnię list inicjalizacyjnych i eliminuje wiele niejednoznaczności związanych z wcześniejszymi formami inicjalizacji.

Przykład:
```cpp
struct FloatOrazInt1
{
    int x;
    double y;
};

struct FloatOrazInt2
{
private:
    int x;
    double y;

public:
    FloatOrazInt2(int xParam, double yParam)
        : x{ xParam }, y{ yParam } // inicjalizacja pól za pomocą list inicjalizacyjnych
    {
    }
};

FloatOrazInt1 var1{ 5, 3.2 }; // inicjalizacja jak agregat — każde pole dostaje wartość z listy
FloatOrazInt2 var2{ 2, 4.3 }; // wywołanie konstruktora klasy
```

Inicjalizacja `var1` zachowuje się dokładnie tak, jak gdyby była to inicjalizacja agregatu. Oznacza to, że każdy element danych obiektu będzie po kolei inicjalizowany przez kopiowanie z odpowiadającej mu wartości z listy inicjalizacyjnej. Tam, gdzie to potrzebne, zostanie użyta niejawna konwersja typów. Jeśli taka konwersja nie istnieje albo istnieje tylko konwersja zawężająca, program jest niepoprawny. Inicjalizacja `var2` wywołuje konstruktor.

Jeśli potrzebna jest konwersja typu, kompilator ją wykona — ale **niedozwolone są konwersje zawężające** (np. `double → int` bez jawnego rzutowania).

***

Można też zwracać obiekty za pomocą `{}` bez podawania typu:
```cpp
using std::string;

struct IdString
{
    string nazwa;
    int identyfikator;
};

IdString pobierzString()
{
    return { "foo", 42 }; // kompilator sam dopasowuje typ i tworzy tymczasowy IdString
}
```

***

##### Uwaga o konstruktorach list inicjalizacyjnych

Jeśli klasa ma konstruktor:

```cpp
TypeName(initializer_list<T>);
```

to **ma on pierwszeństwo** przed innymi konstruktorami, jeśli tylko lista `{}` pasuje typem. Przykład:

```cpp
std::vector<int> vec{ 4 };
```

To **nie** tworzy wektora o rozmiarze 4. Zamiast tego wywoływany jest konstruktor:

```cpp
vector(initializer_list<int>); // tworzy wektor z jednym elementem: 4
```

Aby utworzyć wektor o rozmiarze 4, trzeba użyć klasycznej składni:

```cpp
std::vector<int> vec(4); // poprawnie: wektor o rozmiarze 4
```

***

##### Dodatkowe uwagi i doprecyzowania (ważne dla początkującego)

* **Uniform initialization** ujednolica składnię i pomaga uniknąć „most vexing parse”, ponieważ zapis z nawiasami klamrowymi `{}` nie jest interpretowany jako deklaracja funkcji.
* **Konstruktor listy inicjalizacyjnej** (`initializer_list` constructor) ma priorytet przy dopasowaniu przeciążeń, co może czasem prowadzić do zaskakających wyborów przeciążeń — warto o tym pamiętać przy projektowaniu klas.
* **Narrowing conversions** są zabronione w kontekście list inicjalizacyjnych (np. `double` → `int` bez jawnego rzutowania), co pomaga wykrywać potencjalne błędy utraty informacji już na etapie kompilacji.
* Zwracanie `{ ... }` bez jawnego typu (jak w `return { "foo", 42 };`) działa, ponieważ kompilator wie, jaki typ ma zostać zwrócony i dopasowuje listę do konstruktora docelowego typu.

***

#### Wnioskowanie typów (Type inference)

W C++03 (i w języku C) każda zmienna musiała mieć **jawnie zapisany typ**.
Bywało to problematyczne, szczególnie gdy:

* typ był bardzo złożony (np. tworzony przez szablony),
* typ zwracany przez funkcję był trudny do zapisania,
* używano metaprogramowania szablonowego.

C++11 łagodzi ten problem na dwa sposoby:

* poprzez słowo kluczowe **`auto`**,
* poprzez słowo kluczowe **`decltype`**.

***

##### `auto`

`auto` pozwala kompilatorowi **wywnioskować typ zmiennej z inicjalizatora**:

```cpp
auto jakisWywolywalnyTyp = std::bind(&jakasFunkcja, _2, _1, jakisObiekt);
// typ jest bardzo złożony — kompilator go zna, ale człowiek nie musi

auto innaZmienna = 5; // typ to int
```

Typ `jakisWywolywalnyTyp` jest dokładnie tym, co zwraca odpowiednia instancja `std::bind` dla podanych argumentów. Kompilator zna ten typ bez problemu, ale użytkownik nie musi.

**Uwaga dla początkującego**

> `auto` **nie oznacza „dowolnego typu”**,
> oznacza: **„kompilator sam wpisze właściwy typ”**.

**Uwaga historyczna**

> W języku **B** (poprzedniku C) słowo `auto` oznaczało _zmienną automatyczną_ (lokalną).
> C++11 **zmienia jego znaczenie** — teraz służy do _wnioskowania typu_.

***

##### `decltype`

`decltype(expr)` zwraca **dokładny typ wyrażenia**:

```cpp
int jakasLiczba;
decltype(jakasLiczba) innaLiczba = 5; // typ to int
```

`decltype` jest szczególnie przydatne, gdy:

* typ jest trudny do zapisania,
* używamy przeciążonych operatorów,
* pracujemy z typami specjalizowanymi,
* pracujemy z szablonami,
* chcemy pobrać typ zmiennej, pola lub wyrażenia bez zgadywania.

***

##### `auto` i `decltype` mogą dawać różne typy

Poniższy przykład pokazuje różnicę między typem wywnioskowanym przez `auto`, a typem zwróconym przez `decltype`:

```cpp
#include <vector>

using std::vector;

int main()
{
    const vector<int> wektor(1);

    auto a = wektor[0];        // a ma typ int (kopiowanie wartości)
    decltype(wektor[0]) b = 1; // b ma typ const int& (operator[] zwraca referencję)

    auto c = 0;                // c ma typ int
    auto d = c;                // d ma typ int

    decltype(c) e;             // e ma typ int (typ zmiennej c)
    decltype((c)) f = c;       // f ma typ int& (nawiasy → lvalue → referencja)

    decltype(0) g;             // g ma typ int (0 to rvalue)
}
```

**Dodatkowa uwaga**

Im bardziej zagnieżdżone są kontenery (`vector<map<string, vector<...>>>`), tym większą różnicę robi `auto`.
W C++03 często stosowano `typedef`, aby skrócić kod — `auto` eliminuje tę potrzebę.

Komentarz dla początkującego:

* `decltype(x)` → typ zmiennej `x`
* `decltype((x))` → **zawsze referencja**, bo `(x)` jest lvalue (to jedna z najczęstszych pułapek!)

***
Zobacz też:
* **Czy `decltype` zastąpiło `typeof`?**
***

##### `auto` w pętlach

Zamiast długiego:
```cpp
for (std::vector<int>::const_iterator iterator = mojWektor.cbegin();
     iterator != mojWektor.cend();
     ++iterator)
{
}
```

można napisać:
```cpp
for (auto iterator = mojWektor.cbegin(); iterator != mojWektor.cend(); ++iterator)
{
}
```

A najczęściej stosowana i najczytelniejsza forma (od C++11):
```cpp
for (const auto& element : mojWektor) // pętla po zakresie (range-based for)
{
    // element jest referencją do elementu kontenera
}
```

***

##### (C++14): dedukcja typu zwracanego funkcji

C++11 pozwalał na dedukcję typu zwracanego jedynie w **funkcjach lambda**, i to tylko wtedy, gdy ciało lambdy składało się z pojedynczego wyrażenia `return expression;`.
C++14 rozszerza tę możliwość na **wszystkie funkcje**, niezależnie od tego, czy są to lambdy, funkcje wolnostojące, metody klas czy funkcje szablonowe.

Aby włączyć dedukcję typu zwracanego, funkcja musi być zadeklarowana z użyciem `auto` jako typu zwracanego, **bez trailing return type**:

```cpp
auto policz(); // typ zwracany zostanie wywnioskowany z definicji
```

Typ zwracany jest określany na podstawie wszystkich instrukcji `return` w definicji funkcji.
Jeśli funkcja zawiera wiele instrukcji `return`, **wszystkie muszą zwracać ten sam typ** — w przeciwnym razie kompilacja zakończy się błędem.

Funkcje z dedukcją typu zwracanego mogą mieć deklaracje wstępne, ale **nie mogą być używane przed definicją**, ponieważ kompilator musi znać wszystkie instrukcje `return`, aby ustalić typ.

Dedukcja działa również w funkcjach rekurencyjnych, ale z ograniczeniem:
**pierwsze wywołanie rekurencyjne musi nastąpić po instrukcji `return`, która pozwala ustalić typ zwracany.**

Przykład poprawny:

```cpp
auto poprawna(int i)
{
    if (i == 1)
        return i; // typ zwracany: int

    return poprawna(i - 1) + i; // dopiero teraz można wywołać rekurencyjnie
}
```

Przykład błędny:

```cpp
auto bledna(int i)
{
    if (i != 1)
        return bledna(i - 1) + i; // za wcześnie — typ zwracany nie został jeszcze ustalony

    return i;
}
```

Dedukcja typu zwracanego funkcji w C++14 stanowi fundament późniejszych rozszerzeń, takich jak `decltype(auto)` oraz dedukcja typu zwracanego w kontekstach constexpr.

***

##### **(C++14): `decltype(auto)` i alternatywna dedukcja typu**

C++11 wprowadził dwa mechanizmy dedukcji typu:

* `auto` — tworzy zmienną o typie wywnioskowanym z wyrażenia, ale **zawsze usuwa referencje** (zachowuje się jak `std::decay`).
* `decltype` — oblicza typ wyrażenia zgodnie z jego kategorią wartości (l‑wartość, r‑wartość), dzięki czemu może zwrócić typ referencyjny.

Przykład różnic:

```cpp
int i;
int&& f();

auto x3a = i;            // typ: int
decltype(i) x3d = i;     // typ: int

auto x4a = (i);          // typ: int
decltype((i)) x4d = (i); // typ: int&

auto x5a = f();          // typ: int
decltype(f()) x5d = f(); // typ: int&&
```

C++14 dodaje nową konstrukcję:

**`decltype(auto)`**

Pozwala ona użyć reguł `decltype` w deklaracjach `auto`.
Oznacza to, że typ jest dedukowany **dokładnie tak**, jak zrobiłby to `decltype(expr)`.

Przykłady:

```cpp
int i = 10;
int& ref = i;

auto a = ref;           // typ: int  (kopiowanie)
decltype(auto) b = ref; // typ: int& (zachowanie referencji)
```

`decltype(auto)` może być również użyte jako **typ zwracany funkcji**, co pozwala zachować referencje i kwalifikatory:

```cpp
decltype(auto) zwroc(int& x)
{
    return (x); // zwraca int&
}
```

W przeciwieństwie do zwykłego `auto`, które zawsze zwraca typ niererefencyjny, `decltype(auto)` umożliwia precyzyjne odwzorowanie typu wyrażenia, w tym:

* referencji l‑wartości (`T&`),
* referencji r‑wartości (`T&&`),
* kwalifikatorów `const` i `volatile`.

Mechanizm ten jest szczególnie przydatny w szablonach oraz funkcjach przekazujących argumenty dalej (perfect forwarding).

***

#### Pętla po zakresie (range-based `for`)

C++11 rozszerza składnię instrukcji `for`, aby umożliwić łatwe iterowanie po zakresie elementów.

```cpp
int a[5] = { 1, 2, 3, 4, 5 };

// podwajamy wartość każdego elementu tablicy
for (int& x : a)
{
    x *= 2;
}

// to samo, ale z użyciem auto (wnioskowanie typu)
for (auto& x : a)
{
    x *= 2;
}
```

Ta forma `for`, nazywana **range-based for** (**pętla po zakresie**), iteruje po każdym elemencie:

* tablic C‑stylowych (o znanym rozmiarze w czasie kompilacji),
* list inicjalizacyjnych,
* dowolnego typu, który ma funkcje `begin()` i `end()` zwracające iteratory.

Wszystkie kontenery standardowej biblioteki (`std::vector`, `std::array`, `std::list`, itd.) działają z tą pętlą.

***

#### Funkcje lambda

C++11 wprowadza możliwość tworzenia **funkcji anonimowych** (_lambda functions_ — funkcje lambda).

Przykład:

```cpp
[](int x, int y) -> int
{
    return x + y;
};
```

* `-> int` określa typ zwracany (można go pominąć, jeśli wszystkie `return` zwracają ten sam typ).
* Lambda może być **domknięciem** (_closure_ — funkcja zapamiętująca zmienne z otoczenia).

To bardzo przydatne w programowaniu funkcyjnym, algorytmach STL i callbackach.

***

##### (C++14): lambdy generyczne (generic lambdas)

W C++11 parametry funkcji lambda musiały mieć **konkretne typy** — nie można było używać `auto`.
C++14 wprowadza **lambdy generyczne**, pozwalając deklarować parametry lambdy z użyciem `auto`, co czyni lambdę funkcjonalnie odpowiednikiem szablonu.

Przykład:
```cpp
auto lambda = [](auto x, auto y) -> auto
{
    return x + y;
};
```

Taka lambda może być wywoływana z argumentami różnych typów:

```cpp
auto a = lambda(2, 3);                 // int
auto b = lambda(1.5, 2.5);             // double
auto c = lambda(std::string("a"), "b"); // std::string
```

Lambdy generyczne stosują **reguły dedukcji szablonów**, co oznacza, że ich działanie jest równoważne funktorowi z szablonowym `operator()`:

```cpp
struct
{
    template <typename T, typename U>
    auto operator()(T x, U y) const
    {
        return x + y;
    }
} lambda {};
```

Lambdy generyczne są więc w praktyce **szablonowymi funktorami zapisanymi w postaci lambdy**, co znacząco zwiększa ich elastyczność i przydatność w kodzie generycznym.

***

##### (C++14): wyrażenia przechwytywania (lambda capture expressions)

W C++11 lambda może przechwytywać zmienne z otaczającego zakresu **przez wartość** lub **przez referencję**.
Powoduje to jednak ograniczenie:
**przechwytywanie przez wartość nie pozwala na przechwytywanie typów przenoszalnych (move‑only), takich jak `std::unique_ptr`.**

C++14 wprowadza **wyrażenia przechwytywania**, które pozwalają inicjalizować przechwycone pola lambdy **dowolnym wyrażeniem**, a nie tylko nazwą zmiennej z zewnętrznego zakresu.

Przykład prostego przechwytywania z inicjalizatorem:

```cpp
auto lambda = [wartosc = 1] -> int
{
    return wartosc;
};
```

Lambda zwraca `1`, ponieważ `wartosc` została zainicjalizowana wartością `1`.
Typ `wartosc` jest dedukowany tak, jak przy użyciu `auto`.

Wyrażenia przechwytywania umożliwiają również **przechwytywanie przez przeniesienie**:

```cpp
using std::unique_ptr;

unique_ptr<int> wskaznik(new int(10));

auto lambda = [wartosc = std::move(wskaznik)] -> int
{
    return *wartosc;
};
```

Dzięki temu:

* można przechwytywać obiekty **move‑only**,
* można tworzyć **własne pola lambdy**, nawet jeśli nie istnieją w zewnętrznym zakresie,
* przechwytywanie staje się bardziej elastyczne i przypomina inicjalizację pól w konstruktorze.

Mechanizm ten jest kluczowy dla nowoczesnego stylu programowania funkcyjnego w C++ i stanowi fundament dla późniejszych rozszerzeń (np. init‑captures w structured bindings).

***

#### Alternatywna składnia funkcji (trailing return type — typ zwracany po parametrze)

Składnia deklaracji funkcji odziedziczona z języka C była wystarczająca dla C, ale w C++ zaczęła być problematyczna — szczególnie przy szablonach.

W C++03 taki kod jest niepoprawny:
```cpp
template <class L, class R>
Ret dodaj(const L& lhs, const R& rhs)
{
    return lhs + rhs; // Ret powinien być typem wyniku lhs + rhs
}
```

Nawet z `decltype` w C++11 nie da się tego zapisać w klasycznej formie:
```cpp
// Niepoprawne w C++11
template <class L, class R>
decltype(lhs + rhs) dodaj(const L& lhs, const R& rhs)
{
    return lhs + rhs;
}
```

Dlaczego?
Bo `lhs` i `rhs` **nie istnieją jeszcze** w momencie, gdy parser czyta nagłówek funkcji.

***

##### Trailing return type (typ zwracany po parametrze)

C++11 wprowadza nową składnię:
```cpp
template <class L, class R>
auto add(const L& lhs, const R& rhs) -> decltype(lhs + rhs)
{
    return lhs + rhs;
}
```

Tutaj:

* `auto` jest tylko częścią składni (nie oznacza wnioskowania typu),
* `decltype(lhs + rhs)` może używać parametrów, bo są już znane parserowi.

***

##### Zwykłe funkcje też mogą używać tej składni
```cpp
struct JakasStruktura
{
    auto dodaj(int x, int y) -> int
    {
        return x + y;
    }
};
```

***

##### C++14 upraszcza to jeszcze bardziej

Od C++14 można pominąć trailing return type:
```cpp
auto add(const L& lhs, const R& rhs)
{
    return lhs + rhs; // kompilator sam wywnioskuje typ
}
```

To działa, jeśli typ zwracany można jednoznacznie ustalić.

***

#### Ulepszenia konstrukcji obiektów

W C++03 konstruktor klasy **nie mógł wywołać innego konstruktora tej samej klasy**.
Każdy konstruktor musiał samodzielnie inicjalizować wszystkie pola albo wywoływać wspólną funkcję składową:
```cpp
class LiczbaCalkowita
{
private:
    int wartosc;

    // Wspólna funkcja pomocnicza używana przez oba konstruktory.
    // W C++03 konstruktor NIE mógł wywołać innego konstruktora tej samej klasy,
    // więc wszystkie wspólne operacje inicjalizacyjne trzeba było umieszczać
    // w osobnej funkcji składowej.
    void ustawWartosc(int liczba)
    {
        wartosc = liczba;
    }

public:
    // Konstruktor przyjmujący wartość początkową.
    // Musi samodzielnie wywołać funkcję ustawWartosc(),
    // ponieważ w C++03 nie można było delegować do innego konstruktora.
    LiczbaCalkowita(int liczba)
    {
        ustawWartosc(liczba);
    }

    // Konstruktor domyślny.
    // Również musi samodzielnie wywołać funkcję ustawWartosc(),
    // mimo że logika jest taka sama jak w konstruktorze powyżej.
    // W C++11 można by napisać: LiczbaCalkowita() : LiczbaCalkowita(42) {}
    // ale w C++03 było to niedozwolone.
    LiczbaCalkowita()
    {
        ustawWartosc(42);
    }
};
```

Dodatkowe ograniczenia C++03:

* konstruktory klas bazowych **nie były dziedziczone**,
* każda klasa pochodna musiała pisać własne konstruktory, nawet jeśli konstruktor bazowy był idealny,
* **pól niestatycznych nie można było inicjalizować przy deklaracji**, tylko w konstruktorze.

C++11 rozwiązuje wszystkie te problemy.

***

##### Delegowanie konstruktorów (konstruktor wywołujący inny konstruktor)

C++11 pozwala, aby konstruktor wywołał inny konstruktor tej samej klasy.
Nazywa się to **delegowaniem konstruktora** (constructor delegation).

Delegowanie było wcześniej stosowane w innych językach, takich jak **Java** czy **Objective‑C**.

Przykład:
```cpp
class LiczbaCalkowita
{
private:
    int wartosc;

public:
    LiczbaCalkowita(int liczba)
        : wartosc(liczba)
    {
    }

    LiczbaCalkowita()
        : LiczbaCalkowita(42) // delegowanie do innego konstruktora
    {
    }
};
```

W tym przypadku ten sam efekt można by osiągnąć, używając parametru domyślnego.
Jednak delegowanie ma ważną zaletę: **domyślna wartość (np. 42) znajduje się w implementacji, a nie w interfejsie**.
To ułatwia utrzymanie bibliotek — zmiana wartości domyślnej nie wymaga rekompilacji kodu użytkownika.

**Uwaga dla początkującego:**
W C03 obiekt uznawano za skonstruowany dopiero po zakończeniu działania konstruktora.
W C11 obiekt uznaje się za skonstruowany, gdy **jakikolwiek konstruktor** zakończy działanie.
Ponieważ delegowanie pozwala wykonać kilka konstruktorów po kolei, oznacza to, że konstruktor delegujący działa już na **w pełni skonstruowanym obiekcie**.

Konstruktory klas pochodnych wykonują się **dopiero po zakończeniu całego delegowania** w klasach bazowych.

***

##### Dziedziczenie konstruktorów

C++11 pozwala klasie pochodnej **odziedziczyć wszystkie konstruktory** klasy bazowej.
```cpp
class KlasaBazowa
{
public:
    KlasaBazowa(int wartosc);
};

class KlasaPochodna : public KlasaBazowa
{
public:
    using KlasaBazowa::KlasaBazowa; // dziedziczenie konstruktorów
};
```

Ograniczenia:

* to mechanizm **„wszystko albo nic”** — dziedziczymy wszystkie konstruktory bazowe,
* jeśli konstruktor klasy pochodnej ma taką samą sygnaturę, to **zacienia** konstruktor bazowy,
* przy wielodziedziczeniu nie można dziedziczyć konstruktorów z dwóch klas, jeśli mają identyczne sygnatury (problem diamentu).

***

##### Inicjalizacja pól przy deklaracji (in‑class member initializers)

C++11 pozwala inicjalizować pola **bezpośrednio w miejscu deklaracji**:
```cpp
class LiczbaCalkowita
{
private:
    int wartosc = 5; // inicjalizacja domyślna

public:
    LiczbaCalkowita()
    {
    }

    // konstruktor jawny 'explicit'
    explicit LiczbaCalkowita(int wartoscParam)
        : wartosc(wartoscParam) // nadpisanie wartości domyślnej
    {
    }
};
```

Zasady:

* jeśli konstruktor **nie** inicjalizuje pola, używana jest wartość domyślna,
* jeśli konstruktor inicjalizuje pole, wartość domyślna jest ignorowana.

Można używać:

* przypisania (`= 5`),
* list inicjalizacyjnych (`{5}`),
* konstruktorów (`int wartosc(5)`),
* jednolitej inicjalizacji (`int wartosc{5}`).

***

##### (C++14): inicjalizacja agregatów z polami posiadającymi wartości domyślne

C++11 wprowadził możliwość nadawania polom wartości domyślnych bezpośrednio w klasie (tzw. _in‑class member initializers_).
Jednocześnie zmieniono definicję agregatu tak, aby **każda klasa posiadająca takie inicjalizatory przestawała być agregatem**.
W efekcie nie można było używać inicjalizacji agregatowej (`{ ... }`) dla takich typów.

C++14 **luzuje to ograniczenie**:
klasy posiadające domyślne inicjalizatory pól **mogą ponownie być agregatami**, o ile spełniają pozostałe warunki agregatu.

Jeśli lista inicjalizacyjna nie dostarcza wartości dla danego pola, używany jest jego inicjalizator domyślny:

```cpp
struct Punkt
{
    int x = 1;
    int y = 2;
};

// Od C++14: dozwolone
Punkt p1{ };      // p1.x = 1, p1.y = 2
Punkt p2{ 10 };   // p2.x = 10, p2.y = 2
Punkt p3{ 10, 20 }; // p3.x = 10, p3.y = 20
```

Zasady szablonów i specjalizacji pozostają bez zmian — agregatowość zależy wyłącznie od cech typu, nie od tego, czy jest szablonem.

Mechanizm ten przywraca spójność między inicjalizacją agregatową a inicjalizatorami pól, czyniąc kod bardziej przewidywalnym i wygodnym.

***

#### Jawne nadpisania (`override`) i ostateczne (`final`)

W C++03 łatwo było **przez pomyłkę stworzyć nową funkcję wirtualną**, zamiast nadpisać istniejącą.

Przykład błędu:

```cpp
struct KlasaBazowa
{
    virtual void wykonajOperacje(float wartosc);
};

struct KlasaPochodna : public KlasaBazowa
{
    virtual void wykonajOperacje(int wartosc); // to NIE jest nadpisanie!
};
```

Ponieważ sygnatura jest inna, powstaje **nowa** funkcja wirtualna.
To częsty błąd, szczególnie gdy ktoś modyfikuje klasę bazową i nie zauważa zmiany sygnatury.

***

##### `override` — wymuszenie poprawnego nadpisania

C++11 wprowadza słowo kluczowe (a właściwie _atrybut deklaratora_) `override`:

```cpp
struct KlasaBazowa
{
    virtual void wykonajOperacje(float wartosc);
};

struct KlasaPochodna : public KlasaBazowa
{
    virtual void wykonajOperacje(int wartosc) override; // błąd — nie nadpisuje funkcji bazowej
};
```

Jeśli metoda **nie nadpisuje** żadnej metody z klasy bazowej, kompilator zgłosi błąd.

To chroni przed literówkami, pomyłkami w typach parametrów i przypadkowym tworzeniem nowych funkcji wirtualnych.

***

##### `final` — zakaz dziedziczenia lub nadpisywania

C++11 pozwala:

* oznaczyć klasę jako **niedziedziczącą** (`final`),
* oznaczyć metodę jako **nienadpisywalną** (`final`).

Przykład klasy `final`:

```cpp
struct KlasaBazowa final
{
    // ...
};

// błąd — nie można dziedziczyć po klasie oznaczonej final
struct KlasaPochodna : public KlasaBazowa
{
};
```

Przykład metody `final`:

```cpp
struct KlasaBazowa
{
    virtual void wykonajOperacje() final; // metoda wirtualna oznaczona jako final — nie wolno jej nadpisywać
};

struct KlasaPochodna : public KlasaBazowa
{
    void wykonajOperacje(); // błąd: metoda KlasaBazowa::wykonajOperacje została oznaczona jako final
};
```

W tym przykładzie deklaracja:

```cpp
virtual void wykonajOperacje() final;
```

tworzy nową metodę wirtualną, ale jednocześnie **zabrania klasom pochodnym jej nadpisywania**.
Dodatkowo oznaczenie `final` sprawia, że **żadna klasa pochodna nie może zdefiniować metody o tej samej nazwie i tej samej liście parametrów** — nawet jeśli nie próbowałaby jej „tylko” ukryć lub zdefiniować jako nowej metody.
Dzieje się tak dlatego, że taka deklaracja byłaby traktowana jako próba nadpisania — a to jest zabronione.

***

##### `override` i `final` — ważna uwaga

Ani `override`, ani `final` **nie są słowami kluczowymi języka C++**.
Technicznie są to **identyfikatory używane jako atrybuty deklaratora** (_declarator attributes_).

Oznacza to, że:

* zyskują specjalne znaczenie **tylko w konkretnym miejscu**, czyli:

  * po wszystkich specyfikatorach typu,
  * po specyfikatorach dostępu (`public`, `private`, `protected`),
  * po słowach takich jak `virtual`,
  * ale **przed** inicjalizacją lub implementacją funkcji;

* **nie zmieniają typu funkcji**,

* **nie tworzą nowych identyfikatorów**,

* **nie wpływają na przeciążanie funkcji** — jedynie informują kompilator o zamiarze programisty.

***

##### Rozszerzalność atrybutów deklaratora

Standard C++ dopuszcza możliwość dodawania nowych atrybutów deklaratora w przyszłych wersjach języka.
Już dziś niektóre kompilatory mają własne rozszerzenia, które:

* podpowiadają optymalizacje,
* dodają metadane dla debuggera lub linkera,
* wprowadzają atrybuty bezpieczeństwa,
* wspierają _reflection_ (programowanie refleksyjne),
* dodają informacje potrzebne do współpracy z innymi językami.

Takie rozszerzenia mogą przyjmować parametry w nawiasach, np.:

```cpp
[[gnu::hot]]
[[clang::annotate("info")]]
```

Zgodnie z konwencją ANSI, rozszerzenia specyficzne dla kompilatora powinny używać prefiksu `__` (podwójny podkreślnik).

***

##### Ostatnia ważna rzecz

Poza kontekstem deklaracji funkcji `override` i `final` **mogą być używane jako zwykłe identyfikatory**, np.:

```cpp
int final = 10; // poprawne, choć to bardzo zły pomysł
```

Kompilator nada im specjalne znaczenie **tylko wtedy**, gdy pojawią się w miejscu, gdzie mogą pełnić rolę atrybutu deklaratora.

***

#### Stała pustego wskaźnika i jej typ (null pointer constant and type)

W tym fragmencie, gdy pojawia się zapis „`0`”, oznacza on:

> „stałe wyrażenie o wartości `0` i typie `int`”.

W praktyce taka stała może mieć dowolny typ całkowitoliczbowy.

Od początku istnienia języka C (1972) stała `0` pełniła **podwójną rolę**:

* była liczbą całkowitą,

* była **stałą pustego wskaźnika** (null pointer constant — wartość reprezentująca „brak adresu”).

W języku C problem ten łagodzono makrem `NULL`, które zwykle rozwijało się do:

* `((void*)0)` albo

* `0`.

W C++ nie wolno niejawnie konwertować `void*` do innych typów wskaźnikowych, więc rzutowanie `0` na `void*` **nie daje żadnej korzyści**. W efekcie w C++ jedyną poprawną stałą pustego wskaźnika był **sam&#x20;**`0`.

To prowadziło do problemów z przeciążaniem funkcji:

```cpp
void foo(char*);
void foo(int);
```

Jeśli `NULL` jest zdefiniowane jako `0` (co w C++ jest normą), to:

```cpp
foo(NULL); // wywoła foo(int), co jest prawie na pewno błędem
```

##### `nullptr` — nowe, jednoznaczne źródło pustego wskaźnika

C++11 wprowadza nową stałą pustego wskaźnika: `nullptr`.

* ma typ `nullptr_t`,

* konwertuje się niejawnie i porównuje do **dowolnego typu wskaźnikowego**,

* konwertuje się niejawnie i porównuje do **wskaźnika do składowej** (pointer‑to‑member),

* **nie** konwertuje się ani nie porównuje do typów całkowitych (poza `bool`).

Konwersja do `bool` daje `false` — tak samo jak w przypadku zwykłych wskaźników.

**Uwaga historyczna:** Pierwotnie planowano, że r‑value typu `nullptr_t` **nie** będzie konwertowalne do `bool`. Jednak grupa robocza uznała, że taka konwersja jest pożądana dla spójności z zachowaniem zwykłych wskaźników. Zmiana została jednogłośnie przyjęta w czerwcu 2008 roku.

**Uwaga dodatkowa:** Podobna propozycja została przyjęta również do standardu **C23**.

Dla kompatybilności wstecznej `0` nadal jest poprawną stałą pustego wskaźnika.

Przykłady:

```cpp
char* pc = nullptr; // OK
int* pi = nullptr;  // OK
bool b = nullptr;   // OK. b == false
int i = nullptr;    // błąd — nullptr nie konwertuje się do int
```

##### `nullptr` a przeciążanie funkcji

```cpp
foo(nullptr); // wywoła foo(nullptr_t), a nie foo(int)
```

Pełny komentarz (bez uproszczeń):
```cpp
/*
  Uwaga: w praktyce foo(nullptr_t) wywoła foo(char*) w powyższym przykładzie,
  używając niejawnej konwersji do wskaźnika, ale tylko wtedy, gdy w zasięgu
  nie ma innych przeciążeń przyjmujących kompatybilne typy wskaźników.

  Jeśli istnieje wiele przeciążeń przyjmujących różne typy wskaźników,
  rozstrzyganie przeciążeń zakończy się błędem niejednoznaczności,
  chyba że istnieje dokładne przeciążenie foo(nullptr_t).

  W standardowych nagłówkach C++11 typ nullptr_t powinien być zdefiniowany jako:
      typedef decltype(nullptr) nullptr_t;

  A NIE jako:
      typedef int nullptr_t;      // starsze wersje C++, gdzie NULL musiało być równe 0
      typedef void* nullptr_t;    // ANSI C, gdzie NULL definiowano jako ((void*)0)
*/
```
***

#### Silnie typowane wyliczenia (strongly typed enumerations)

W C++03 typy wyliczeniowe (`enum`) **nie były bezpieczne typowo**:

* enum zachowywał się jak liczba całkowita,
* można było porównywać wartości z różnych enumów,
* można było porównywać wartości enum z liczbami całkowitymi,
* typ bazowy (rozmiar) był zależny od implementacji,
* wszystkie nazwy elementów enum trafiały do **tego samego zakresu**,
  co oznaczało, że **nie można było mieć dwóch różnych enumów z tymi samymi nazwami elementów**.

C++11 wprowadza nowy rodzaj wyliczeń: **`enum class`** (również `enum struct`, które jest synonimem).

```cpp
enum class KolorKarty
{
    TREFL = 1,
    KIER = 2,
    KARO = 4,
    PIK = 8
};
```

Zalety:

* wartości **nie konwertują się niejawnie do liczb**,
  więc wyrażenie typu `KolorKarty::PIK == 8` powoduje błąd kompilacji,
* wartości **nie konwertują się** do innych enumów,
* nazwy są umieszczone w zakresie `KolorKarty::`,
* typ bazowy jest zawsze znany (domyślnie `int`).

Można jawnie określić typ bazowy:

```cpp
enum class Kierunek : char
{
    GORA,
    DOL,
    LEWO,
    PRAWO
};
```

***

##### Stare wyliczenia z nowym zakresem

Można użyć starej składni, ale z określonym typem bazowym:

```cpp
enum Kierunek : char
{
    GORA,
    DOL,
    LEWO,
    PRAWO
};
```

W tym przypadku:

* `Kierunek::GORA` jest poprawne,
* ale dla zgodności wstecznej **`GORA` również istnieje w zakresie zewnętrznym**.

Oznacza to, że enumeratory są dostępne **jednocześnie**:

* w zakresie `Kierunek::`,
* oraz w zakresie otaczającym.

***

##### Deklaracje wstępne enumów

W C++03 nie można było deklarować enumów wstępnie, ponieważ kompilator nie znał ich rozmiaru.

W C++11 można to zrobić, jeśli rozmiar jest znany — jawnie lub domyślnie:

```cpp
enum Enum1;
// Niepoprawne w C++03 i C++11: nie można określić typu bazowego,
// więc kompilator nie zna rozmiaru wyliczenia.

enum Enum2 : unsigned int;
// Poprawne w C++11: typ bazowy został jawnie określony jako unsigned int,
// więc kompilator zna rozmiar wyliczenia i może przyjąć deklarację wstępną.

enum class Enum3;
// Poprawne w C++11: dla enum class domyślnym typem bazowym jest int,
// więc rozmiar jest znany i deklaracja wstępna jest dozwolona.

enum class Enum4 : unsigned int;
// Poprawne w C++11: typ bazowy określony jawnie, więc deklaracja wstępna jest poprawna.

enum Enum2 : unsigned short;
// Niepoprawne w C++11: Enum2 zostało wcześniej zadeklarowane z typem bazowym unsigned int,
// więc nie można później zmienić typu bazowego na unsigned short.
```

#### Podwójny nawias ostry

W C++03 parser zawsze interpretował `>>` jako:

* operator przesunięcia bitowego w prawo, albo
* operator ekstrakcji strumienia (`std::cin >> x`).

To powodowało problemy przy zagnieżdżonych szablonach:

```cpp
vector<vector<int>> v; // w C++03 błąd — parser widzi operator >>
```

**C++11 usprawnia specyfikację parsera** w taki sposób, że wielokrotne nawiasy ostre zamykające (`>>`, `>>>`, itd.) są interpretowane jako zamykanie listy argumentów szablonu — tam, gdzie ma to sens.

Można to obejść, stosując nawiasy okrągłe wokół wyrażeń parametrów, które zawierają operatory binarne `>`, `>=` lub `>>`:

```cpp
using std::vector;

template <bool Test>
class JakisTyp;

vector<JakisTyp<1> 2>> x1;
// Interpretacja:
//   Kompilator widzi JakisTyp<1> → wartość 1 jest traktowana jako true,
//   więc jest to JakisTyp<true>.
//   Następnie parser interpretuje "2 >> x1" jako operator przesunięcia bitowego
//   lub operator ekstrakcji strumienia, co NIE jest poprawną składnią deklaratora.
//   W efekcie cały zapis jest niepoprawny. (1 jest true).

vector<JakisTyp<(1>2)>> x1;
// Interpretacja:
//   Nawiasy wymuszają ocenę wyrażenia (1 > 2), które jest false,
//   więc otrzymujemy JakisTyp<false>.
//   Następnie parser widzi poprawny deklarator "x1".
//   Całość jest poprawną deklaracją w C++11.
//   (1 > 2) jest false.
```

***

#### Jawne operatory konwersji (explicit conversion operators)

W C++98 słowo kluczowe `explicit` można było stosować tylko do konstruktorów, aby zapobiec **niejawnym konwersjom typu** wykonywanym przez konstruktory jednoargumentowe.
Nie działało to jednak dla **operatorów konwersji**.

Przykład problemu:

* inteligentny wskaźnik może mieć `operator bool()`,
* dzięki temu można go używać w instrukcjach warunkowych:

```cpp
if (inteligentnyWskaznik) { ... }
```

* ale `bool` w C++ jest **typem arytmetycznym**,
* więc może konwertować się niejawnie do `int`, `double`, itd.,
* co pozwala na niezamierzone operacje matematyczne.

To klasyczny problem znany jako **idiom bezpiecznego boola** (_safe bool idiom_).

***

##### C++11: `explicit` dla operatorów konwersji

C++11 pozwala oznaczać operatory konwersji jako `explicit`, np.:

```cpp
explicit operator bool() const;
```

Efekt:

* operator **nie może być użyty w konwersjach niejawnych**,

* ale **może być użyty w kontekstach wymagających wartości logicznej**, takich jak:

  * warunek `if`,
  * warunek pętli `while` / `for`,
  * operatory logiczne (`&&`, `||`, `!`).

Czyli:

* `if (obj)` → **dozwolone**,
* `int x = obj;` → **błąd**,
* `double y = obj;` → **błąd**.

To elegancko rozwiązuje problem **safe bool**.

***

#### Aliasowanie szablonów (template aliases)

W C++03 można było tworzyć `typedef`, ale tylko jako alias **konkretnego typu**, np.:

* alias typu zwykłego,
* alias konkretnej specjalizacji szablonu.

Nie można było tworzyć aliasów **samych szablonów**.

Przykład niepoprawny w C++03:

```cpp
template <typename Pierwszy, typename Drugi, int Trzeci>
class JakisTyp;

template <typename Drugi>
typedef JakisTyp<InnyTyp, Drugi, 5> NazwaTypedefu; // Niepoprawne w C++03
```

***

##### C++11: aliasy szablonów przez `using`

C++11 wprowadza składnię:

```cpp
template <typename Pierwszy, typename Drugi, int Trzeci>
class JakisTyp;

template <typename Drugi>
using NazwaTypu = JakisTyp<InnyTyp, Drugi, 5>;
```

To jest **pełnoprawny alias szablonu**.

***

##### `using` jako nowoczesny zamiennik `typedef`

```cpp
typedef void (*TypFunkcji)(double); // stary styl
using TypFunkcji = void (*)(double); // nowy styl
```

Zalety `using`:

* czytelniejszy,
* działa z aliasami szablonów,
* lepiej współpracuje z `template <...>`.

***

##### (C++14): zmienne szablonowe (variable templates)

W poprzednich wersjach C++ szablonami mogły być jedynie funkcje, klasy oraz aliasy typów.
C++14 rozszerza ten mechanizm, pozwalając tworzyć **szablonowe zmienne** — czyli zmienne, których typ i wartość zależą od parametru szablonu.

Przykładowo, można zdefiniować stałą `PI` zależną od typu:

```cpp
template <typename T>
constexpr T PI = T(3.141592653589793238462643383);
```

Dzięki temu:

```cpp
double d = PI<double>;       // 3.1415926535897931...
float  f = PI<float>;        // 3.1415927f
int    i = PI<int>;          // 3
```

Zmienne szablonowe podlegają **tym samym zasadom specjalizacji**, co funkcje i klasy szablonowe:

```cpp
template <>
constexpr const char* PI<const char*> = "pi";
```

Mechanizm ten jest szczególnie przydatny do definiowania:

* stałych zależnych od typu (np. `epsilon<T>`, `zero<T>`, `identity<T>`),
* parametrów konfiguracyjnych w metaprogramowaniu,
* wartości używanych w kontekstach `constexpr`.

Zmienne szablonowe stanowią naturalne uzupełnienie aliasów szablonów z C++11 i są ważnym elementem nowoczesnego stylu programowania szablonowego.

***

#### Unia bez ograniczeń (unrestricted unions)

W C++03 unie (`union`) miały poważne ograniczenia:

* nie mogły zawierać obiektów z **nietrywialnym konstruktorem** lub **destruktorem**,
* nie mogły zawierać typów z nietrywialnymi funkcjami specjalnymi.

C++11 **znosi część tych ograniczeń**.

Jeśli unia zawiera typ z nietrywialnymi funkcjami specjalnymi, to:

* kompilator **nie wygeneruje automatycznie** odpowiednich funkcji specjalnych dla unii,
* trzeba je zdefiniować ręcznie.

Przykład unii dozwolonej w C++11:

```cpp
#include <new> // Potrzebne do użycia placement 'new'.

struct Punkt
{
    int a;
    int b;

    Punkt() {}

    Punkt(int x, int y)
        : a(x), b(y) {} // ← "poprawiony błąd 'x(a), y(b)' z przykładu z wikipedii."
};

union MojaUnia
{
    int z;
    double w;
    Punkt p; // Niepoprawne w C++03; poprawne w C++11.

    // Z powodu składowej Punkt, teraz potrzebna jest definicja konstruktora.
    MojaUnia() {}

    MojaUnia(const Punkt& punktParam)
        : p(punktParam) {} // Konstruuje obiekt Punkt z użyciem listy inicjalizacyjnej.

    MojaUnia& operator=(const Punkt& punktParam)
    {
        // Przypisuje obiekt Punkt z użyciem placement 'new'.
        new (&p) Punkt(punktParam);
        return *this;
    }
};
```

Zmiany te **nie psują istniejącego kodu**, ponieważ jedynie **luzują wcześniejsze ograniczenia**.

***

### Ulepszenia funkcjonalności języka

Te funkcje pozwalają językowi robić rzeczy, które wcześniej były niemożliwe, bardzo rozwlekłe lub wymagały nieprzenośnych bibliotek.

***

#### Szablony wariadyczne (Variadic templates)

W C++03 jedynym sposobem na napisanie funkcji przyjmującej dowolną liczbę argumentów były **funkcje wariadyczne w stylu C** (`...` + `va_list`, `va_arg`, `va_start`). Były one bardzo niebezpieczne – brak sprawdzania typów, łatwe błędy, problemy z alignmentem i niezdefiniowane zachowanie przy złym użyciu.

C++11 wprowadza **szablony wariadyczne** – mechanizm, który pozwala szablonom (zarówno klasom, jak i funkcjom) przyjmować **zmienną liczbę parametrów** w sposób **w pełni bezpieczny typowo**.

##### Podstawowa składnia

```cpp
template <typename... Args>        // Args...  – "parameter pack" (paczka parametrów)
void mojaFunkcja(Args... args)     // args...  – paczka argumentów
{
    // ...
}
```

`typename... Args` oznacza „dowolna liczba dowolnych typów”.

##### Prosty przykład – bezpieczna funkcja wypisująca dowolną liczbę argumentów

```cpp
#include <iostream>

void print() 
{
    std::cout << std::endl;                    // przypadek bazowy (0 argumentów)
}

template <typename T, typename... Args>
void print(T first, Args... rest)
{
    std::cout << first << " ";
    print(rest...);                            // rekurencyjne wywołanie z resztą argumentów
}

int main()
{
    print(42, 3.14, "C++11", 'x', "jest super"); // działa z różnymi typami
}
```

**Uwaga:** Funkcja _print_ używa **rekurencji szablonów** (kompilator tworzy kolejne wersje funkcji, za każdym razem z jednym argumentem mniej – aż dojdzie do wersji z zeroma argumentami).

Dzięki temu mechanizmowi kompilator w czasie kompilacji generuje kod dla każdej kombinacji typów i liczby argumentów. Wszystko jest sprawdzane typowo, w czasie kompilacji, a programista nie musi ręcznie wyciągać argumentów za pomocą niebezpiecznych makr (`va_arg`).

To jedna z najważniejszych zmian w C++11, która ogromnie ułatwiła pisanie elastycznych i bezpiecznych bibliotek.

##### Dlaczego to jest duża zmiana?

- **Bezpieczeństwo typów** – kompilator wie dokładnie, jakie typy przekazujesz.
- **Brak rzutowań** i ręcznego wyciągania argumentów przez `va_arg`.
- Umożliwia tworzenie bardzo elastycznych bibliotek (np. `std::tuple`, `std::make_shared`, `std::thread`, formatowanie tekstu itp.).
- Działa zarówno dla funkcji, jak i dla klas szablonowych (`std::tuple<int, double, std::string>` to właśnie szablon wariadyczny).

W praktyce w C++11 najczęściej spotykasz je w formie rekurencyjnej (jak powyżej) – to podstawowy wzorzec, który warto zrozumieć na początku.

***

#### Nowe literały napisowe

W C++03 istniały tylko dwa rodzaje literałów napisowych:

1. `"tekst"` → tablica zakończona znakiem null typu `const char[]`,
2. `L"tekst"` → tablica zakończona znakiem null typu `const wchar_t[]`,
   gdzie `wchar_t` jest znakiem szerokim o **niezdefiniowanym rozmiarze i semantyce**.

Żaden z tych literałów **nie obsługiwał**:

* UTF‑8,
* UTF‑16,
* UTF‑32,
* ani żadnego innego kodowania Unicode.

***

C++11 wprowadza obsługę trzech kodowań Unicode:

* UTF‑8,
* UTF‑16,
* UTF‑32.

Dodatkowo:

* definicja typu `char` została zmieniona tak, aby **gwarantować**, że ma co najmniej rozmiar potrzebny do przechowywania ośmiobitowego kodowania UTF‑8,

* dodano typy:

  * `char16_t` — przeznaczony do przechowywania UTF‑16,
  * `char32_t` — przeznaczony do przechowywania UTF‑32.

***

Tworzenie literałów napisowych dla każdego kodowania:

```cpp
u8"Jestem napisem UTF-8."
u"To jest napis UTF-16."
U"To jest napis UTF-32."
```

Typy:

* `u8"..."` → `const char[]`,
* `u"..."` → `const char16_t[]`,
* `U"..."` → `const char32_t[]`.

***

Wstawianie punktów kodowych Unicode:

```cpp
u8"To jest znak Unicode: \u2018."
u"To jest większy znak Unicode: \u2018."
U"To jest znak Unicode: \U00002018."
```

Zasady:

* liczba po `\u` to **16‑bitowy** punkt kodowy Unicode (hex, bez `0x`),
* liczba po `\U` to **32‑bitowy** punkt kodowy Unicode,
* można wstawiać tylko **poprawne** punkty kodowe,
* zakres U+D800–U+DFFF jest **zabroniony**, ponieważ jest zarezerwowany dla par surogatów UTF‑16.

***

##### Surowe literały napisowe (raw string literals)

C++11 dodaje surowe literały napisowe:

```cpp
R"(Dane napisu \ Różne rzeczy " )"
R"delimiter(Dane napisu \ Różne rzeczy " )delimiter"
```

Zasady:

* wszystko między `"( ... )"` jest częścią napisu,

* znaki `"` i `\` **nie wymagają uciekania**,

* w wersji z delimiterem:

  * napis zaczyna się od `R"delimiter(`,
  * kończy się na `)delimiter"`,
  * `delimiter` może mieć do 16 znaków,
  * nie może zawierać spacji, znaków sterujących, `(`, `)` ani `\`,
  * dzięki delimiterowi można mieć w napisie sekwencję `)"`.

Przykład z oryginału:

```cpp
R"delimiter("(a-z)")delimiter"
```

jest równoważne:

```cpp
"\"(a-z)\""
```
***

Surowe literały można łączyć z Unicode:

```cpp
u8R"XXX(Jestem „surowym UTF-8” napisem.)XXX"
uR"*(To jest „surowy UTF-16” napis.)*"
UR"(To jest „surowy UTF-32” napis.)"
```

***

#### Literały definiowane przez użytkownika (user‑defined literals)

C++03 udostępniał pewną liczbę literałów.
Na przykład zapis `12.5` jest literałem typu `double` o wartości 12.5.
Dodanie sufiksu `f`, jak w `12.5f`, tworzy wartość typu `float` o tej samej wartości.

Sufiksy literałów w C++03 są **sztywno określone przez standard** — programista **nie może** tworzyć własnych modyfikatorów literałów.

C++11 to zmienia: pozwala użytkownikowi definiować **własne sufiksy literałów**, które tworzą obiekty na podstawie znaków występujących w literałach.

***

##### Surowe i przetworzone literały (raw vs cooked literals)

C++11 rozdziela przetwarzanie literałów na dwa etapy:

* **raw literal** — surowa sekwencja znaków określonego typu,
* **cooked literal** — wartość po interpretacji przez kompilator.

Przykłady:

* literał `1234`
  raw → `'1','2','3','4'`
  cooked → liczba całkowita `1234`

* literał `0xA`
  raw → `'0','x','A'`
  cooked → liczba `10`

Literały mogą być rozszerzane zarówno w formie raw, jak i cooked —
**z wyjątkiem literałów napisowych**, które mogą być przetwarzane tylko w formie cooked,
ponieważ prefiksy (`u8`, `u`, `U`, `L`) zmieniają znaczenie i typ znaków.

***

##### Zasady dotyczące sufiksów użytkownika

* wszystkie literały definiowane przez użytkownika są **sufiksami**,
* **nie można** definiować prefiksów,
* wszystkie sufiksy zaczynające się od czegokolwiek poza `_` są **zarezerwowane przez standard**,
* dlatego każdy sufiks użytkownika **musi zaczynać się od `_`**.

***

##### Literały użytkownika w formie raw (`operator""`)

Literały przetwarzające surową formę definiuje się przez `operator""`.

Przykład:

```cpp
OutputType operator""_mysuffix(const char* literal_string)
{
    // zakładamy, że OutputType ma konstruktor przyjmujący const char*
    OutputType ret(literal_string);
    return ret;
}

OutputType some_variable = 1234_mysuffix;
// zakładamy, że OutputType ma metodę get_value() zwracającą double
assert(some_variable.get_value() == 1234.0);
```

Instrukcja:

```cpp
OutputType some_variable = 1234_mysuffix;
```

wywołuje funkcję literału użytkownika.
Przekazywany jest do niej C‑string `"1234"` — czyli z terminatorem `\0`.

***

##### Alternatywny mechanizm: szablony wariadyczne dla raw literals

Można też przetwarzać literały raw za pomocą **szablonów wariadycznych**:

```cpp
template <char...>
OutputType operator""_tuffix();

OutputType some_variable = 1234_tuffix;
OutputType another_variable = 2.17_tuffix;
```

To instancjuje funkcję jako:

```cpp
operator""_tuffix<'1','2','3','4'>()
```

W tej formie:

* **nie ma** znaku `\0` na końcu,

* celem jest umożliwienie użycia `constexpr`,

* dzięki temu kompilator może przetworzyć literał **w całości w czasie kompilacji**,
  pod warunkiem, że:

  * `OutputType` jest `constexpr`‑konstruktywny i kopiowalny,
  * funkcja literału jest `constexpr`.

***

##### Literały cooked dla liczb

Dla literałów liczbowych cooked literal ma typ:

* `unsigned long long` — dla literałów całkowitych,
* `long double` — dla literałów zmiennoprzecinkowych.

Uwaga:
Nie ma potrzeby obsługi typów całkowitych ze znakiem,
bo znak `-` jest operatorem unarnym, a nie częścią literału.

Przykład:

```cpp
OutputType operator""_suffix(unsigned long long);
OutputType operator""_suffix(long double);

OutputType some_variable = 1234_suffix;      // Używa przeciążenia 'unsigned long long'.
OutputType another_variable = 3.1416_suffix; // Używa przeciążenia 'long double'.
```

***

##### Literały użytkownika dla napisów

Dla literałów napisowych używa się przeciążeń:

```cpp
OutputType operator""_ssuffix(const char* string_values, size_t num_chars);
OutputType operator""_ssuffix(const wchar_t* string_values, size_t num_chars);
OutputType operator""_ssuffix(const char16_t* string_values, size_t num_chars);
OutputType operator""_ssuffix(const char32_t* string_values, size_t num_chars);

OutputType some_variable = "1234"_ssuffix;   // const char*
OutputType some_variable = u8"1234"_ssuffix; // const char*
OutputType some_variable = L"1234"_ssuffix;  // const wchar_t*
OutputType some_variable = u"1234"_ssuffix;  // const char16_t*
OutputType some_variable = U"1234"_ssuffix;  // const char32_t*
```

Nie istnieje alternatywna forma szablonowa dla literałów napisowych.
Literały znakowe działają analogicznie.

***

##### (C++14): standardowe literały użytkownika

C++11 zdefiniował mechanizm literałów użytkownika, ale sama biblioteka standardowa nie dostarczała żadnych gotowych sufiksów.
C++14 wprowadza pierwsze **standardowe literały**, dostępne bez dodatkowych definicji:

**1. Literały napisowe (`"s"`)**

Tworzą odpowiednie typy `std::basic_string`:

```cpp
using namespace std::string_literals;

auto napis = "hello world"s; // std::string
```

**2. Literały czasu (`h`, `min`, `s`, `ms`, `us`, `ns`)**

Tworzą obiekty `std::chrono::duration`:

```cpp
using namespace std::chrono_literals;

auto czas = 60s; // std::chrono::seconds
```

**3. Literały liczb zespolonych (`if`, `i`, `il`)**

Tworzą obiekty `std::complex<float>`, `std::complex<double>`, `std::complex<long double>`:

```cpp
using namespace std::complex_literals;

auto z = 1i; // std::complex<double>
```

Literały `"s"` nie kolidują ze sobą, ponieważ:

* `"tekst"s` działa tylko dla **literałów napisowych**,
* `10s` działa tylko dla **liczb**, tworząc `std::chrono::seconds`.

***

#### Model pamięci dla wielowątkowości

C++11 standaryzuje wsparcie dla programowania wielowątkowego.

Składa się to z dwóch części:

* modelu pamięci, który pozwala na współistnienie wielu wątków w programie,
* wsparcia bibliotecznego dla interakcji między wątkami (zob. sekcję o mechanizmach wątkowych w artykule).

Model pamięci definiuje, kiedy wiele wątków może uzyskiwać dostęp do tego samego miejsca w pamięci oraz określa, kiedy zmiany dokonane przez jeden wątek stają się widoczne dla innych wątków.

***

##### Pamięć lokalna dla wątku (thread-local storage)

W środowisku wielowątkowym powszechne jest, że każdy wątek ma pewne unikalne zmienne.
Dzieje się tak już dla zmiennych lokalnych funkcji, ale nie dotyczy to zmiennych globalnych i statycznych.

Nowy czas życia obiektu — **thread‑local** (oprócz istniejących: _static_, _dynamic_ i _automatic_) — jest oznaczany specyfikatorem przechowywania `thread_local`.

Każdy obiekt, który mógłby mieć statyczny czas życia (tj. żyć przez cały czas wykonywania programu), może zamiast tego mieć czas życia związany z wątkiem.
Intencją jest to, że podobnie jak inne zmienne o czasie życia statycznego, obiekt thread‑local może być inicjalizowany konstruktorem i niszczony destruktorem.

***

##### Jawnie domyślne funkcje specjalne (explicitly defaulted special member functions)

W C++03 kompilator dostarcza dla klas, które ich nie definiują samodzielnie:

* konstruktor domyślny,
* konstruktor kopiujący,
* operator przypisania kopiującego (`operator=`),
* destruktor.

Programista może nadpisać te domyślne implementacje, definiując własne wersje.
C++ definiuje także kilka globalnych operatorów (np. `operator new`), które działają dla wszystkich klas i które programista może nadpisać.

Jednak kontrola nad tworzeniem tych domyślnych funkcji była ograniczona.
Uczynienie klasy niekopiowalną często osiągano przez zadeklarowanie prywatnego konstruktora kopiującego i operatora przypisania **bez ich definicji**.
Próba użycia takich funkcji narusza Zasadę jednej definicji (One Definition Rule, ODR).
Choć diagnostyka nie jest wymagana, naruszenia mogą skutkować błędem linkera.

W przypadku konstruktora domyślnego kompilator **nie wygeneruje go**, jeśli klasa ma zdefiniowany **jakikolwiek inny konstruktor**.

C++11 pozwala na:

* **jawne zadeklarowanie użycia domyślnych** funkcji specjalnych (`= default`),
* **jawne usunięcie** funkcji (`= delete`).

Przykład:

```cpp
class JakisTyp
{
    JakisTyp() = default; // Konstruktor domyślny jest jawnie zadeklarowany.
    JakisTyp(InnyTyp wartosc);
};
```

***

##### Jawnie usunięte funkcje (explicitly deleted functions)

Funkcję można jawnie wyłączyć.
Jest to przydatne do zapobiegania niejawnych konwersji typów.

Specyfikator `= delete` może być użyty, aby zabronić wywołań funkcji z określonymi typami parametrów:

```cpp
void noInt(double i);
void noInt(int) = delete;
```

Próba wywołania `noInt()` z argumentem typu `int` zostanie odrzucona przez kompilator,
zamiast wykonywać cichą konwersję do `double`.
Wywołanie `noInt()` z `float` nadal działa.

Możliwe jest zabronienie wywołań funkcji dla dowolnego typu innego niż `double` przy użyciu szablonu:

```cpp
double onlyDouble(double d)
{
    return d;
}

template <typename T>
double onlyDouble(T) = delete;
```

Wywołanie `onlyDouble(1.0)` zadziała, natomiast `onlyDouble(1.0f)` spowoduje błąd kompilacji.

Funkcje składowe klas i konstruktory również można usuwać.
Na przykład można zapobiec kopiowaniu obiektów klasy przez usunięcie konstruktora kopiującego i operatora przypisania:

```cpp
class NieKopiowalny
{
    NieKopiowalny();
    NieKopiowalny(const NieKopiowalny&) = delete;
    NieKopiowalny& operator=(const NieKopiowalny&) = delete;
};
```
***

#### Typ `long long int`

W C++03 największym typem całkowitym był `long int`.
Gwarantowano, że ma co najmniej tyle użytecznych bitów, co `int`.
W praktyce powodowało to, że `long int` miał rozmiar **64 bity** w niektórych popularnych implementacjach, a **32 bity** w innych.

C++11 dodaje nowy typ całkowity: **`long long int`**, aby rozwiązać ten problem.

Gwarantuje się, że:

* jest co najmniej tak duży jak `long int`,
* ma **nie mniej niż 64 bity**.

Typ ten został pierwotnie wprowadzony w standardzie **C99**, a większość kompilatorów C++ już wcześniej wspierała go jako rozszerzenie.

***

#### (C++14): literały binarne (`0b`, `0B`)

C++14 wprowadza możliwość zapisu wartości liczbowych w postaci binarnej.
Nowa składnia wykorzystuje przedrostki:

* `0b`
* `0B`

Przykłady:
```cpp
int mask = 0b101010;     // 42
int flags = 0B1100'0011; // 195 (można łączyć z apostrofami)
```

Literały binarne są szczególnie przydatne przy:

* operacjach bitowych,
* programowaniu niskopoziomowym,
* definiowaniu masek i flag,
* pracy z rejestrami sprzętowymi.

Składnia ta jest zgodna z wieloma innymi językami (Java, C#, Swift, Go, Scala, Python, Ruby, OCaml) i była dostępna jako rozszerzenie w niektórych kompilatorach C już od 2007 roku.

***

#### (C++14): separatory cyfr w literałach liczbowych

C++14 pozwala używać apostrofu (`'`) jako **separatora cyfr** w literałach liczbowych.
Separator może być stosowany **dowolnie**, zarówno w literałach całkowitych, jak i zmiennoprzecinkowych, a także w literałach binarnych.

Przykłady:
```cpp
auto literal_calkowity          = 1'000'000;
auto literal_zmiennoprzecinkowy = 0.000'015'3;
auto literal_binarny            = 0b0100'1100'0110;
auto tuzin_krorow              = 12'00'00'000; // format indyjski (12 crore)
```

Separatory cyfr:

* nie wpływają na wartość liczbową,
* służą wyłącznie poprawie czytelności,
* mogą być stosowane w dowolnych miejscach między cyframi,
* są zgodne z podobnymi mechanizmami w innych językach (Java, C#, Swift, Python).

Mechanizm ten ułatwia szybkie rozpoznawanie dużych liczb przez człowieka (tzw. _subitizing_), szczególnie w kodzie niskopoziomowym, obliczeniach finansowych i pracy z dużymi stałymi.

***

#### Asercje statyczne (static assertions)

W C++03 istniały dwie metody testowania asercji:

* makro `assert` — sprawdzane **w czasie wykonywania**,
* dyrektywa preprocesora `#error` — sprawdzana **podczas preprocessingu**, czyli **przed** instancjacją szablonów.

Żadna z nich nie nadaje się do testowania własności zależnych od parametrów szablonu.

C++11 wprowadza nowe narzędzie: **asercje statyczne**, testowane **w czasie kompilacji**, za pomocą słowa kluczowego `static_assert`.

Deklaracja ma postać:

```cpp
static_assert(wyrazenie_stale, komunikat_bledu);
```

Przykłady:
```cpp
static_assert((GREEKPI > 3.14) && (GREEKPI < 3.15),
              "Wartość GREEKPI jest niedokładna!");
```

```cpp
template <class Typ>
struct Sprawdz
{
    static_assert(sizeof(int) <= sizeof(Typ),
                  "Typ T jest zbyt mały!");
};
```

```cpp
using std::is_integral;

template <class Liczbowy>
Liczbowy foo(Liczbowy x, Liczbowy y)
{
    static_assert(is_integral<Liczbowy>::value,
                  "Parametr foo() musi być typem całkowitoliczbowym.");
}
```

Jeśli wyrażenie stałe jest `false`, kompilator generuje komunikat o błędzie.

Pierwszy przykład jest podobny do `#error`, ale preprocesor obsługuje tylko typy całkowite.
W drugim przykładzie asercja jest sprawdzana **przy każdej instancjacji** szablonu `Sprawdz`.

Asercje statyczne są użyteczne także poza szablonami.
Na przykład implementacja algorytmu może zakładać, że `long long` jest większy niż `int` — założenie prawdziwe na większości systemów, ale **niegwarantowane** przez standard.
`static_assert` pozwala wykryć takie niezgodności **w czasie kompilacji**.

##### Uzupełnienie (C++17): komunikat błędu jest opcjonalny

Od C++17 komunikat błędu w `static_assert` stał się **opcjonalny**:

```cpp
static_assert(sizeof(int) == 4);
```

Jeśli warunek jest fałszywy, kompilator generuje domyślny komunikat.

##### Uzupełnienie (C++20): `static_assert` w modułach i konceptach

C++20 pozwala używać `static_assert`:

* w modułach (`module`),
* w definicjach konceptów,
* w kontekstach wymagających stałej ewaluacji.

***

#### Pozwolenie na użycie `sizeof` dla składowych klas bez jawnego obiektu

W C++03 operator `sizeof` można stosować do typów i obiektów, ale nie można było zrobić tego:

```cpp
struct JakisTyp
{
    InnyTyp skladowa;
};

sizeof(JakisTyp::skladowa); // Nie działa w C++03. Działa w C++11.
```

To wyrażenie powinno zwrócić rozmiar typu `InnyTyp`.
W C++03 takie użycie jest zabronione i powoduje błąd kompilacji.
C++11 pozwala na to.

To samo dotyczy operatora `alignof` wprowadzonego w C++11 — również może być użyty w analogiczny sposób dla składowych klasy.

> **Uwaga praktyczna:**
> To ułatwia pisanie metaprogramów i szablonów, gdzie chcemy odwołać się do właściwości typu składowej bez potrzeby tworzenia instancji obiektu.

***

#### Kontrola i odpytywanie wyrównania obiektów (Control and query object alignment)

C++11 pozwala odpytywać i kontrolować wyrównanie zmiennych za pomocą operatorów `alignof` i specyfikatora `alignas`.

**`alignof(T)`**:

* zwraca wymagane wyrównanie typu `T` (w bajtach, potęga dwójki),
* zwraca `std::size_t`,
* dla referencji zwraca wyrównanie typu, na który referencja wskazuje,
* dla tablic zwraca wyrównanie typu elementu tablicy.

**`alignas`**:

* kontroluje wyrównanie pamięci dla zmiennej,
* przyjmuje stałą lub typ,
* zapis `alignas(T)` jest równoważny `alignas(alignof(T))`.

Przykład:

```cpp
alignas(float) unsigned char bufor[sizeof(float)];
```

> **Wyjaśnienie dla początkujących:**
> Wyrównanie (alignment) oznacza, że adresy pamięci, pod którymi przechowywane są obiekty danego typu, muszą być wielokrotnością pewnej liczby bajtów.
> Nieprawidłowe wyrównanie może prowadzić do błędów sprzętowych lub spadku wydajności.

##### Uzupełnienie (C++17): interference sizes

C++17 wprowadza stałe:

```cpp
std::hardware_destructive_interference_size
std::hardware_constructive_interference_size
```

Pomagają one unikać _false sharing_ w programach wielowątkowych.

##### Uzupełnienie (C++20): alignas w kontekstach constexpr

Od C++20 `alignas` może być używany w obiektach `constexpr`, jeśli wyrównanie jest znane w czasie kompilacji.

***

#### Pozwolenie na implementacje z automatycznym zbieraniem śmieci (Allow garbage collected implementations)

W poprzednich standardach C++ przewidziano mechanizmy sterowane przez programistę (np. `set_new_handler`), ale **nie zdefiniowano pojęcia osiągalności obiektów** w kontekście automatycznego zbierania śmieci.

C++11 definiuje warunki, kiedy wartości wskaźnikowe są **„bezpiecznie pochodne”** od innych wartości.

Implementacja może zadeklarować, że działa w trybie **strict pointer safety**.
W takim przypadku wskaźniki, które nie są pochodne zgodnie z tymi regułami, mogą stać się nieprawidłowe.

> **Nota:**
> Standard **nie wymusza** implementacji garbage collectora,
> ale pozwala implementacjom, które go oferują, działać w sposób zgodny ze standardem.

***

#### Atrybuty (Attributes)

C++11 wprowadza ujednoliconą składnię dla rozszerzeń kompilatora i narzędzi w postaci **atrybutów**, zapisywanych w podwójnych nawiasach kwadratowych `[[...]]`.
Wcześniej rozszerzenia te były realizowane za pomocą dyrektywy `#pragma` lub vendor‑specyficznych słów kluczowych (np. `__attribute__` w GCC, `__declspec` w MSVC).

Atrybut można stosować do różnych elementów kodu źródłowego. Przykład:

```cpp
int [[atrybut1]] zmienna [[atrybut2, atrybut3]];

[[atrybut4(arg1, arg2)]] if (warunek)
{
    [[dostawca::atrybut5]] return zmienna;
}
```

W powyższym przykładzie:

* `atrybut1` odnosi się do **typu** zmiennej `zmienna`,
* `atrybut2` i `atrybut3` odnoszą się do **samej zmiennej**,
* `atrybut4` odnosi się do **instrukcji `if`**,
* `dostawca::atrybut5` odnosi się do **instrukcji `return`**.

Ogólne zasady (z pewnymi wyjątkami):

* atrybut dla **nazwanego bytu** umieszcza się **po nazwie**,
* atrybut dla **nienazwanego bytu** umieszcza się **przed** tym bytem,
* w jednej parze `[[...]]` można wymienić **wiele atrybutów**,
* atrybuty mogą przyjmować **argumenty**,
* atrybuty mogą być zdefiniowane w **przestrzeniach nazw dostawców** (np. `vendor::attr`).

Zalecenie: atrybuty **nie powinny zmieniać semantyki programu** — kod powinien zachowywać ten sam sens nawet wtedy, gdy atrybuty zostaną zignorowane.
Atrybuty służą głównie do przekazywania kompilatorowi dodatkowych informacji (diagnostyka, optymalizacje, analiza kodu).

C++11 definiuje dwa standardowe atrybuty:

* `[[noreturn]]` — informuje, że funkcja **nie zwraca** (np. funkcja kończąca program),
* `[[carries_dependency]]` — pomaga optymalizować kod wielowątkowy, wskazując, że argumenty funkcji lub wartość zwracana **niosą zależność pamięciową**.

> **Ostrzeżenie:** chociaż atrybuty są bezpiecznym mechanizmem rozszerzeń, używanie vendor‑specyficznych atrybutów może zmniejszyć przenośność kodu. Zawsze sprawdź, czy atrybut ma znaczenie w docelowych kompilatorach.

##### Uzupełnienie (C++14): atrybut `[[deprecated]]`

C++14 wprowadza atrybut:

```cpp
[[deprecated("Powód oznaczenia jako przestarzałe")]]
```

Służy do oznaczania elementów programu jako **przestarzałych**, co powoduje generowanie ostrzeżeń kompilatora przy ich użyciu.
Można podać opcjonalny komunikat wyjaśniający powód wycofania i sugerujący alternatywę.

Atrybut `[[deprecated]]` może być stosowany do:

* funkcji,
* metod klas,
* zmiennych,
* pól klas,
* typów,
* przestrzeni nazw,
* szablonów.

Przykład:
```cpp
[[deprecated]]
int funkcja_f();

[[deprecated("funkcja_g() nie jest bezpieczna wątkowo. Użyj funkcja_h()")]]
void funkcja_g(int& x);

void funkcja_h(int& x);

void test()
{
    int a = funkcja_f(); // ostrzeżenie: 'funkcja_f' jest przestarzała
    funkcja_g(a);        // ostrzeżenie: 'funkcja_g' jest przestarzała: funkcja_g() nie jest bezpieczna wątkowo. Użyj funkcja_h()
}
```

Atrybut ten pozwala stopniowo wycofywać stare API, jednocześnie zachowując kompatybilność wsteczną.

##### **Uzupełnienie (C++17): atrybuty `[[fallthrough]]`, `[[nodiscard]]`, `[[maybe_unused]]`**

C++17 dodaje trzy ważne atrybuty:

* `[[fallthrough]]` — oznacza zamierzone „przejście” między sekcjami `case` w `switch`,
* `[[nodiscard]]` — oznacza, że wartość zwracana **nie powinna być ignorowana**,
* `[[maybe_unused]]` — oznacza, że element **może nie być używany**, co zapobiega ostrzeżeniom.

Przykład:

```cpp
[[nodiscard]] int policz();
```
##### **Uzupełnienie (C++20): atrybut `[[likely]]` i `[[unlikely]]`**

C++20 dodaje atrybuty podpowiadające kompilatorowi przewidywanie gałęzi:

```cpp
if ([[likely]] warunek)
{
    ...
}
else [[unlikely]]
{
    ...
}
```
##### **Uzupełnienie (C++23): atrybut `[[assume]]`**

C++23 wprowadza:

```cpp
[[assume(warunek)]]
```

Informuje kompilator, że dany warunek **zawsze jest prawdziwy**, co może umożliwić dodatkowe optymalizacje.
***

## Zmiany w standardowej bibliotece C++

W standardzie C++11 wprowadzono szereg nowych funkcji do standardowej biblioteki.
Wiele z nich dałoby się zaimplementować w starym standardzie, ale część opiera się — w mniejszym lub większym stopniu — na nowych cechach rdzenia języka C++11.

Duża część nowych bibliotek została wcześniej zdefiniowana w dokumencie znanym jako **TR1 (Library Technical Report)**.
Różne implementacje TR1 były dostępne w przestrzeni nazw `std::tr1`.
W C++11 funkcje te przeniesiono do przestrzeni nazw `std`, a przy okazji niektóre z nich zostały zaktualizowane tak, by wykorzystywać nowe możliwości języka C++11 lub rozszerzone o funkcje, które były możliwe do zaimplementowania już w C++03, ale nie znalazły się w pierwotnym TR1.

***

### Ulepszenia istniejących komponentów biblioteki

C++11 wprowadza nowe cechy języka, z których mogą korzystać istniejące komponenty biblioteki standardowej.

Przykładowo większość kontenerów standardowych zyskuje na wsparciu dla **konstruktorów przenoszących opartych na rvalue references** — pozwala to szybko przenosić ciężkie obiekty lub przenosić zawartość kontenerów do nowej pamięci bez kosztownego kopiowania.

Komponenty biblioteki zostały tam, gdzie to miało sens, zaktualizowane o następujące cechy C++11 (lista nie jest wyczerpująca):

* rvalue references i związane z nimi wsparcie dla przenoszenia (move),
* wsparcie dla jednostek kodowania UTF‑16 i UTF‑32 (typy znakowe),
* szablony wariadyczne (w połączeniu z rvalue references umożliwiające perfect forwarding),
* wyrażenia stałoczasowe (`constexpr`),
* `decltype`,
* jawne `explicit` dla operatorów konwersji,
* funkcje zadeklarowane jako `= default` lub `= delete`.

Ponadto od czasu poprzedniego standardu powstało dużo kodu korzystającego ze standardowej biblioteki, co ujawniło obszary wymagające poprawy.
Jednym z takich obszarów są **alokatory**.
W C++11 wprowadzono dodatkowy, **zakresowy model alokatorów**, uzupełniający wcześniejszy model.

***

#### (C++14): heterogeniczne wyszukiwanie w kontenerach asocjacyjnych

C++14 rozszerza kontenery asocjacyjne (`std::map`, `std::set` i ich warianty) o możliwość wyszukiwania za pomocą typu innego niż typ klucza, o ile komparator potrafi porównać oba typy.

Przykładowo w `std::map<std::string, int>` można wywołać:

```cpp
std::map<std::string, int, std::less<>> mapa;

mapa["ala"] = 1;

auto it = mapa.find("ala"); // działa bez tworzenia std::string
```

Mechanizm ten pozwala:

* unikać kosztownych konwersji (np. `const char*` → `std::string`),
* wyszukiwać obiekty złożone po jednym polu bez tworzenia obiektu tymczasowego,
* pisać bardziej naturalny i wydajny kod.

Aby zachować kompatybilność wsteczną, heterogeniczne wyszukiwanie działa tylko wtedy, gdy komparator na to pozwala.
Standardowe `std::less<>` i `std::greater<>` zostały w C++14 odpowiednio rozszerzone.

***

#### Uzupełnienie (C++14): drobne rozszerzenia biblioteki

C++14 wprowadza szereg mniejszych, ale praktycznych rozszerzeń w standardowej bibliotece:

***

##### `std::make_unique`

Dodano funkcję `std::make_unique`, będącą odpowiednikiem `std::make_shared`, ale tworzącą obiekty zarządzane przez `std::unique_ptr`:

```cpp
auto ptr = std::make_unique<int>(42);
```

Zapobiega to błędom związanym z ręcznym użyciem `new` i poprawia bezpieczeństwo wyjątków.

***

##### `std::integral_constant` — operator wywołania

`std::integral_constant` zyskuje przeciążenie `operator()`, które zwraca wartość stałej:

```cpp
std::integral_constant<int, 7> c;
int x = c(); // x == 7
```

***

##### `std::integer_sequence` i aliasy (`index_sequence`, `make_index_sequence`)

Dodano narzędzia do reprezentowania sekwencji liczb całkowitych w czasie kompilacji — kluczowe dla metaprogramowania i pracy z param packami:

```cpp
template<std::size_t... I>
void foo(std::index_sequence<I...>);
```

***

##### Nowe funkcje globalne: `std::cbegin`, `std::cend`, `std::rbegin`, `std::rend`, `std::crbegin`, `std::crend`

Dodano stałe i odwrotne iteratory w formie funkcji globalnych:

```cpp
for (auto it = std::cbegin(v); it != std::cend(v); ++it) { ... }
```

***

##### `std::exchange`

Funkcja przypisuje nową wartość i zwraca starą:

```cpp
int x = 5;
int old = std::exchange(x, 10); // old == 5, x == 10
```

***

##### Nowe przeciążenia `std::equal`, `std::mismatch`, `std::is_permutation`

Dodano wersje przyjmujące **dwa zakresy** zamiast jednego zakresu i długości drugiego:

```cpp
std::equal(a.begin(), a.end(), b.begin(), b.end());
```

***

##### `std::is_final`

Nowy trait wykrywający, czy klasa została oznaczona jako `final`.

***

##### `std::quoted`

Manipulator strumieniowy umożliwiający bezpieczne wypisywanie i wczytywanie napisów zawierających spacje lub cudzysłowy:

```cpp
std::cout << std::quoted("ala ma kota");
```

***

#### (C++17): ulepszenia alokatorów i kontenerów

C++17 wprowadza m.in.:

* `std::pmr::*` — **polymorphic memory resources**, nowy model zarządzania pamięcią,
* ulepszenia w kontenerach, np. `try_emplace`, `insert_or_assign` w mapach,
* możliwość używania `constexpr` w większej liczbie funkcji bibliotecznych.

##### Uzupełnienie (C++20): kontenery i algorytmy constexpr

C++20 pozwala używać wielu kontenerów i algorytmów w kontekście `constexpr`, np.:

```cpp
constexpr std::vector<int> v = {1, 2, 3};
```
***

#### (C++23): rozszerzenia `ranges` i `format`

C++23 rozszerza:

* `std::ranges` o nowe algorytmy,
* `std::format` o dodatkowe możliwości formatowania.

***

### Mechanizmy wielowątkowe (threading facilities)

Choć język C++03 miał pewne podstawy dla modelu pamięci, to **praktyczne** wsparcie dla programowania wielowątkowego pojawia się dopiero w bibliotece standardowej C++11.

* Dostępna jest klasa wątku `std::thread`, która przyjmuje obiekt funkcyjny (oraz opcjonalnie argumenty) i uruchamia go w nowym wątku.
  Można poczekać na zakończenie wątku za pomocą `std::thread::join()`.
  Gdy to konieczne, biblioteka udostępnia dostęp do natywnego uchwytu wątku przez `std::thread::native_handle()` dla operacji specyficznych dla platformy.

* Do synchronizacji dodano odpowiednie mutexy (`std::mutex`, `std::recursive_mutex` itd.) oraz zmienne warunkowe (`std::condition_variable`, `std::condition_variable_any`).
  Są one zaprojektowane do użycia z mechanizmami RAII, takimi jak `std::lock_guard` i `std::unique_lock`, oraz z gotowymi algorytmami blokowania.

* Dla wydajnych, niskopoziomowych zastosowań, gdzie chcemy komunikować się między wątkami bez narzutu mutexów, biblioteka udostępnia **operacje atomowe** na lokalizacjach pamięci.
  Operacje atomowe mogą określać minimalne wymagania dotyczące widoczności pamięci (memory ordering).
  Możliwe jest też użycie jawnych barier pamięci (memory barriers).

* Biblioteka zawiera także mechanizmy `std::future` i `std::promise` do przekazywania wyników asynchronicznych między wątkami oraz `std::packaged_task` do opakowywania wywołań funkcji generujących takie wyniki.

* Nowa funkcja `std::async` ułatwia uruchamianie zadań powiązanych z `std::future`.
  Użytkownik może wskazać, czy zadanie ma być uruchomione asynchronicznie w osobnym wątku, czy synchronicznie w wątku wywołującym.
  Domyślnie implementacja może wybrać strategię wykonania, co pozwala wykorzystać sprzętową równoległość bez nadmiernego tworzenia wątków.

> **Nota praktyczna:** bardziej zaawansowane, wysokopoziomowe mechanizmy (np. w pełni ustandaryzowane pule wątków) zostały pozostawione do dalszych raportów technicznych; oczekuje się, że będą one budowane na podstawie podstawowych mechanizmów wprowadzonych w C++11.

#### Uzupełnienie (C++14): drobne poprawki

C++14 wprowadza:

* ulepszenia w `std::future` i `std::promise`,
* poprawki w `std::async` dotyczące harmonogramowania,
* **`std::shared_timed_mutex` — mutex współdzielony z obsługą timeoutów (`try_lock_for`, `try_lock_until`)**.

> **Nota:** `std::shared_timed_mutex` zostało wprowadzone w C++14, ale od C++17 preferowanym, lżejszym odpowiednikiem jest `std::shared_mutex`.
>`shared_timed_mutex` pozostaje częścią biblioteki i nie jest oznaczone jako przestarzałe.

***

#### (C++17): `std::shared_mutex` i `std::scoped_lock`

##### `std::shared_mutex` i `std::shared_lock` — wielu czytających, jeden zapisujący

W wielu programach wielowątkowych dane są często **czytane**, a rzadko **modyfikowane**.
W takim przypadku użycie zwykłego `std::mutex` jest zbyt restrykcyjne — blokuje wszystkich,
nawet gdy kilka wątków chce tylko czytać te same dane jednocześnie (co jest bezpieczne).

`std::shared_mutex` rozwiązuje ten problem, rozróżniając dwa tryby dostępu:

* **tryb współdzielony** (_shared_) — wiele wątków może jednocześnie trzymać blokadę
  do **odczytu**; żaden z nich nie może modyfikować danych,
* **tryb wyłączny** (_exclusive_) — tylko jeden wątek trzyma blokadę do **zapisu**;
  żaden inny wątek nie może ani czytać, ani pisać.

Do blokowania w trybie współdzielonym służy `std::shared_lock`,
a do trybu wyłącznego — `std::unique_lock` lub `std::lock_guard`
(tak samo jak przy zwykłym mutexie).

```cpp
#include <shared_mutex>
#include <mutex>
#include <string>

std::shared_mutex mutexDanych;
std::string wspolneDane = "poczatkowa wartosc";

// Wątek czytający — może działać równolegle z innymi czytającymi
void czytaj()
{
    std::shared_lock blokada(mutexDanych); // tryb współdzielony
    auto kopia = wspolneDane;             // bezpieczny odczyt
} // blokada zwolniona automatycznie

// Wątek zapisujący — wymaga wyłącznego dostępu
void zapisz(const std::string& nowaWartosc)
{
    std::unique_lock blokada(mutexDanych); // tryb wyłączny
    wspolneDane = nowaWartosc;
} // blokada zwolniona automatycznie
```

> **Uwaga:** `std::shared_timed_mutex` (C++14) oferuje te same możliwości, ale dodatkowo
> obsługuje timeouty (`try_lock_for`, `try_lock_until`). Jeśli timeouty nie są potrzebne,
> `std::shared_mutex` (C++17) jest lżejszym i preferowanym wyborem.

##### `std::scoped_lock` — jednoczesne blokowanie wielu mutexów bez zakleszczenia

Klasyczny problem z wieloma mutexami: jeśli dwa wątki próbują zablokować te same mutexy
w **odwrotnej kolejności**, mogą się wzajemnie zablokować (zakleszczenie, ang. _deadlock_).

```cpp
// Wątek A blokuje najpierw m1, potem m2
// Wątek B blokuje najpierw m2, potem m1
// → oba wątki czekają na siebie nawzajem → deadlock
```

C++17 rozwiązuje ten problem przez `std::scoped_lock`, który blokuje **wszystkie podane
mutexy jednocześnie** przy użyciu algorytmu unikania zakleszczeń:

```cpp
#include <mutex>

std::mutex m1, m2;

void funkcja()
{
    std::scoped_lock blokada(m1, m2); // oba mutexy zablokowane bezpiecznie jednocześnie
    // sekcja krytyczna
} // oba mutexy zwolnione automatycznie
```

`std::scoped_lock` jest uogólnieniem `std::lock_guard` na wiele mutexów.
Dla jednego mutexa zachowuje się identycznie jak `std::lock_guard`.

***

#### Uzupełnienie (C++20): `std::jthread` i stop tokens

C++20 wprowadza:

* `std::jthread` — wątek automatycznie dołączany (RAII),
* `std::stop_token`, `std::stop_source` — ustandaryzowane anulowanie wątków,
* `std::latch`, `std::barrier`, `std::semaphore`.

#### Uzupełnienie (C++23): ulepszenia atomików i futures

C++23 rozszerza:

* `std::atomic` o nowe operacje,
* `std::future` o lepszą integrację z `std::stop_token`.

***

### Typy krotek (Tuple types)

Krotki to kolekcje heterogenicznych obiektów o ustalonej liczbie elementów — można je traktować jako uogólnienie pól struktury.

Wersja krotek w TR1 korzystała z technik wymagających z góry określonego maksymalnego rozmiaru i sporej ilości kodu opartego na makrach.  
Dzięki szablonom wariadycznym w C++11 deklaracja krotki jest prosta i nie wymaga jawnego limitu liczby typów:

```cpp
namespace std
{
    template <class... Typy>
    class tuple;
}
```

Przykład definicji i użycia:

```cpp
typedef std::tuple<int, double, long&, const char*> KrotkaTestowa;

long dlugi = 12;
KrotkaTestowa dowod(18, 6.5, dlugi, "Ciao!");

dlugi = std::get<0>(dowod); // Przypisuje do 'dlugi' wartość 18.
std::get<3>(dowod) = " Pięknie!"; // Modyfikuje czwarty element krotki.
```

Kilka ważnych uwag:

* Można tworzyć krotkę bez podawania wartości elementów tylko wtedy, gdy typy elementów mają konstruktory domyślne.
* Można przypisać jedną krotkę do drugiej:
  - jeśli typy krotek są identyczne, każdy element musi mieć konstruktor kopiujący,
  - jeśli typy różnią się, elementy po prawej stronie muszą być konwertowalne do odpowiadających typów po lewej lub typ po lewej musi mieć odpowiedni konstruktor.

Przykład konwersji elementów:

```cpp
typedef std::tuple<int, double, std::string> Krotka1;
Krotka1 k1;

typedef std::tuple<char, short, const char*> Krotka2;
Krotka2 k2('X', 2, "Hola!");

k1 = k2; // OK: pierwsze dwa elementy da się skonwertować,
         // trzeci można skonstruować z 'const char *'.
```

Dodatkowe narzędzia:

* `std::make_tuple` — tworzy `std::tuple` z dedukcją typów,
* `auto` ułatwia deklarację zmiennych przechowujących krotki,
* `std::tie` tworzy krotki referencji do l‑value, co ułatwia rozpakowywanie krotek,
* `std::ignore` pozwala pominąć elementy podczas rozpakowywania.

Przykład:

```cpp
#include <string>
#include <tuple>

using std::string;

auto rekord = std::make_tuple("Hari Ram", "New Delhi", 3.5, 'A');

string imie;
float gpa;
char ocena;

std::tie(imie, std::ignore, gpa, ocena) = rekord; // std::ignore pomija nazwę miejsca

std::cout << imie << ' ' << gpa << ' ' << ocena << std::endl;
```

Dostępne są operatory relacyjne (dla krotek o tej samej liczbie elementów) oraz dwie metafunkcje kompilacyjne:

* `std::tuple_size<T>::value` — zwraca liczbę elementów w krotce `T`,
* `std::tuple_element<I, T>::type` — zwraca typ elementu o indeksie `I` w krotce `T`.

***

#### (C++14): pobieranie elementu krotki po typie (`std::get<T>`)

W C++11 elementy `std::tuple` można było pobierać wyłącznie za pomocą indeksu:

```cpp
auto x = std::get<2>(t);
```

C++14 rozszerza `std::get` o możliwość pobierania elementu **po typie**:

```cpp
using std::string;
using std::tuple;

tuple<string, string, int> t("foo", "bar", 7);

int liczba = std::get<int>(t); // OK — jedyny element typu int
int liczba2 = std::get<2>(t);  // nadal działa jak wcześniej
```

Jeśli krotka zawiera **więcej niż jeden element danego typu**, wywołanie `std::get<T>` powoduje **błąd kompilacji**:

```cpp
string s = std::get<string>(t); // błąd: typ string jest niejednoznaczny
```

Mechanizm ten poprawia czytelność kodu i eliminuje konieczność pamiętania indeksów, o ile typy w krotce są unikalne.

***

#### Uzupełnienie (C++14): `std::make_tuple` jako częściowo `constexpr`

W C++11 funkcja `std::make_tuple` nie była funkcją `constexpr`, co uniemożliwiało tworzenie krotek w kontekście stałoczasowym.

C++14 częściowo to zmienia — `std::make_tuple` staje się **`constexpr` tam, gdzie to możliwe**, co pozwala tworzyć proste krotki w czasie kompilacji:

```cpp
constexpr auto t = std::make_tuple(1, 2.5, 'x'); // OK w C++14
```

Ograniczenia wynikają z tego, że `constexpr` zależy od tego, czy wszystkie elementy krotki są `constexpr`‑konstruktywne.

***

#### Uzupełnienie (C++17/20/23)

* **C++17** — krotki stały się w pełni `constexpr`; dodano strukturę wiązań (`auto [a, b] = krotka;`).  
* **C++20** — krotki są kompatybilne z `std::ranges`.  
* **C++23** — usprawniono dedukcję typów i integrację z `std::format`.

***

### Hash tables

Dodanie tablic mieszających (unordered associative containers) było jednym z najczęściej zgłaszanych postulatów.  
Nie trafiły do C++03 wyłącznie z powodu ograniczeń czasowych.

Choć w najgorszym przypadku (przy wielu kolizjach) tablice mieszające są mniej wydajne niż zrównoważone drzewa, w wielu praktycznych zastosowaniach działają szybciej.

Kolizje są obsługiwane wyłącznie przez **łańcuchowanie liniowe**, ponieważ komitet uznał, że standaryzowanie rozwiązań z otwartym adresowaniem wprowadza zbyt wiele problemów (zwłaszcza przy usuwaniu elementów).

Aby uniknąć konfliktów nazw z bibliotekami niestandardowymi, użyto przedrostka **`unordered`** zamiast **`hash`**.

Nowa biblioteka udostępnia cztery typy kontenerów unordered:

| Typ kontenera               | Wartość powiązana | Klucze równoważne |
|-----------------------------|-------------------|--------------------|
| `std::unordered_set`        | Nie               | Nie                |
| `std::unordered_multiset`   | Nie               | Tak                |
| `std::unordered_map`        | Tak               | Nie                |
| `std::unordered_multimap`   | Tak               | Tak                |

Nowe klasy spełniają wszystkie wymagania kontenera i udostępniają metody takie jak `insert`, `erase`, `begin`, `end`.

Ta funkcja nie wymagała rozszerzeń rdzenia języka — jedynie niewielkiego rozszerzenia nagłówka `<functional>` oraz dodania `<unordered_set>` i `<unordered_map>`.

#### Uzupełnienie (C++17/20/23)

* **C++17** — dodano `try_emplace`, `insert_or_assign` w mapach.  
* **C++20** — poprawiono wydajność hashowania i dodano `contains()`.  
* **C++23** — rozszerzono API o nowe operacje i poprawiono integrację z `std::expected`.

***

### std::array i std::forward_list

Poza tablicami mieszającymi do biblioteki dodano jeszcze dwa kontenery:

* **`std::array`** — kontener o stałym rozmiarze, bardziej wydajny niż `std::vector` w scenariuszach, gdzie rozmiar jest znany i stały, a jednocześnie bezpieczniejszy i wygodniejszy w użyciu niż tablica w stylu C.
* **`std::forward_list`** — lista jednokierunkowa, która zajmuje mniej pamięci niż dwukierunkowa `std::list`, gdy nie potrzebujemy iteracji dwukierunkowej.

#### Uzupełnienie (C++17/20)

* **C++17** — `std::array` stał się w pełni `constexpr`.  
* **C++20** — `std::array` i `std::forward_list` współpracują z `std::ranges`.

***

### Wyrażenia regularne (Regular expressions)

Nowa biblioteka, dostępna w nagłówku `<regex>`, wprowadza kilka klas:

* wyrażenia regularne reprezentuje szablon `std::regex`,
* dopasowania reprezentuje `std::match_results`,
* `std::regex_iterator` służy do iterowania po wszystkich dopasowaniach wyrażenia.

Funkcja `std::regex_search` służy do wyszukiwania, a `std::regex_replace` do operacji „znajdź i zamień”, zwracając nowy łańcuch.

Przykład użycia `std::regex_iterator`:

```cpp
#include <regex>

using std::cregex_iterator;
using std::regex;
using std::string;

const char* wzorzec = R"([^ ,.\t\n]+)"; // znajdź słowa oddzielone spacją, przecinkiem, kropką, tabem, nową linią

regex re(wzorzec); // rzuca wyjątek przy niepoprawnym wzorcu

const char* tekst = "Unseen University - Ankh-Morpork";

// Użyj regex_iterator, aby zidentyfikować wszystkie słowa w 'tekst' rozdzielone znakami z 'wzorzec'.
for (cregex_iterator iter(tekst, tekst + strlen(tekst), re); iter != re.end(); ++iter)
{
    string dopasowanie = iter->str();
    std::cout << dopasowanie << std::endl;
}
```

Nagłówek `<regex>` nie wymaga modyfikacji istniejących nagłówków ani rozszerzeń rdzenia języka.
W systemach POSIX wyrażenia regularne są też dostępne przez bibliotekę C (`<regex.h>`), ale implementacje i interfejsy różnią się od C++ `<regex>`.

#### Uzupełnienie (C++17/20/23)

* **C++17** — poprawiono wydajność i stabilność implementacji `<regex>` (wiele kompilatorów dopiero wtedy zaczęło mieć w pełni działające regexy).
* **C++20** — dodano `constexpr` dla części operacji na `std::regex_constants`.
* **C++23** — trwają prace nad ujednoliceniem zachowania `<regex>` między kompilatorami (nie jest to część standardu, ale praktyczna uwaga).

***

### Ogólnego przeznaczenia inteligentne wskaźniki (General-purpose smart pointers)

C++11 dostarcza `std::unique_ptr` oraz ulepszenia dla `std::shared_ptr` i `std::weak_ptr` pochodzących z TR1.
`std::auto_ptr` jest **przestarzały** (deprecated) i nie powinien być używany w nowych programach - usunięty całkowicie w standardzie C++17.

> **Uwaga:** `std::unique_ptr` zastępuje `std::auto_ptr` w większości zastosowań, oferując bezpieczne semantyki przenoszenia bez niejednoznacznych zachowań kopiowania.

#### Uzupełnienie (C++14/17/20)

* **C++14** — dodano `std::make_unique`.
* **C++17** — poprawiono integrację `std::shared_ptr` z tablicami.
* **C++20** — inteligentne wskaźniki mogą być używane w większej liczbie kontekstów `constexpr`.

***

### Rozszerzalny mechanizm liczb losowych (Extensible random number facility)

Biblioteka standardowa C dostarczała funkcję `rand` do generowania pseudolosowych liczb, ale algorytm był całkowicie zależny od dostawcy biblioteki.
C++11 wprowadza nowy, bardziej elastyczny mechanizm generowania liczb pseudolosowych.

Mechanizm C++11 dzieli się na dwie części:

* **silnik generatora** (engine) — przechowuje stan generatora i produkuje surowe pseudolosowe wartości,
* **rozkład** (distribution) — określa zakres i rozkład matematyczny wyników.

Silnik i rozkład łączy się, tworząc obiekt generatora losowego.

W odróżnieniu od `rand`, C++11 dostarcza trzy podstawowe algorytmy silników:

* `linear_congruential_engine`,
* `subtract_with_carry_engine`,
* `mersenne_twister_engine` (np. `std::mt19937`).

C++11 udostępnia też wiele standardowych rozkładów, m.in.:

* `uniform_int_distribution`,
* `uniform_real_distribution`,
* `bernoulli_distribution`,
* `binomial_distribution`,
* `geometric_distribution`,
* `negative_binomial_distribution`,
* `poisson_distribution`,
* `exponential_distribution`,
* `gamma_distribution`,
* `weibull_distribution`,
* `extreme_value_distribution`,
* `normal_distribution`,
* `lognormal_distribution`,
* `chi_squared_distribution`,
* `cauchy_distribution`,
* `fisher_f_distribution`,
* `student_t_distribution`,
* `discrete_distribution`,
* `piecewise_constant_distribution` oraz
* `piecewise_linear_distribution`.

Przykład łączenia silnika i rozkładu:

```cpp
#include <functional>
#include <random>

using std::mt19937;
using std::uniform_int_distribution;

uniform_int_distribution<int> rozklad(0, 99);
mt19937 silnik; // Mersenne twister MT19937

auto generator = std::bind(rozklad, silnik);

int losowa1 = generator();            // Wygeneruj liczbę 0..99
int losowa2 = rozklad(silnik);        // Alternatywny sposób generowania
```

> **Wskazówka praktyczna:** nowy mechanizm pozwala wybrać odpowiedni silnik i rozkład do konkretnego zastosowania (np. symulacje, gry, statystyka), zamiast polegać na jednej, nieokreślonej implementacji `rand`.

#### Uzupełnienie (C++14/17/20/23)

* **C++14** — dodano `std::shuffle` oparty na silnikach `<random>`.
* **C++17** — poprawiono deterministyczność i stabilność implementacji.
* **C++20** — część rozkładów i silników stała się `constexpr`.
* **C++23** — trwają prace nad rozszerzeniem API generatorów (niektóre kompilatory już implementują propozycje).

***

### Wrapper reference (opakowanie referencji)

**Wrapper reference (opakowanie referencji)** uzyskuje się z instancji szablonu klasy `reference_wrapper`.
Opakowania referencji są podobne do zwykłych referencji języka C++ (`&`).
Aby uzyskać opakowanie referencji z dowolnego obiektu, używa się funkcji szablonowej `ref` (dla referencji stałej — `cref`).

Opakowania referencji są szczególnie przydatne w funkcjach szablonowych, gdy chcemy przekazywać **referencje** do parametrów zamiast ich **kopiować**:

```cpp
#include <functional>
#include <iostream>

// Ta funkcja przyjmie referencję do parametru 'r' i ją zwiększy.
void funkcja(int& r)
{
    r++;
}

// Funkcja szablonowa.
template <class F, class P>
void g(F f, P t)
{
    f(t);
}

int main()
{
    int i = 0;

    g(funkcja, i);
    // Instancjacja: 'g<void(int&), int>'
    // W efekcie 'i' nie zostanie zmodyfikowane.

    std::cout << i << std::endl; // Wyjście -> 0

    g(funkcja, std::ref(i));
    // Instancjacja: 'g<void(int&), reference_wrapper<int>>'
    // W efekcie 'i' zostanie zmodyfikowane.

    std::cout << i << std::endl; // Wyjście -> 1
}
```

Ta funkcjonalność została dodana do istniejącego nagłówka `<functional>` i nie wymagała zmian w rdzeniu języka.

#### Uzupełnienie (C++14/17/20/23)

**C++14**

* `reference_wrapper` zyskał bardziej konsekwentne konwersje do `T&`.
* `std::ref` i `std::cref` stały się częściowo `constexpr`.

**C++17**

* `reference_wrapper` stał się **literalnym typem** (`constexpr`).
* Można go używać w strukturach wiązań (`auto& [a, b] = ...;`).

**C++20**

* Wrappery referencji współpracują z `std::invoke` w kontekstach `constexpr`.
* `std::invoke` stał się centralnym mechanizmem wywoływania obiektów funkcyjnych.

**C++23**

* Wrappery są szerzej akceptowane w algorytmach ranges.
* Trwa integracja z `std::expected` i `std::function_ref`.

***

### Polimorficzne wrappery dla obiektów funkcyjnych

**Polimorficzne wrappery** dla obiektów funkcyjnych działają podobnie do wskaźników na funkcje pod względem semantyki i składni, ale są mniej ściśle związane z konkretnym typem.
Mogą odnosić się do **wszystkiego, co da się wywołać**:

* wskaźników na funkcje,
* wskaźników na metody składowe,
* funktorów,

o ile argumenty są zgodne z sygnaturą wrappera.

Przykład:

```cpp
#include <functional>

using std::function;
using std::plus;

// Tworzenie wrappera przy użyciu szablonu 'function'.
function<int(int, int)> funkcja;

plus<int> dodaj;
// 'plus' zadeklarowano jako 'template <class T> T plus(T, T);'
// więc 'dodaj' ma typ 'int dodaj(int x, int y)'.

funkcja = dodaj; // OK — parametry i typ zwracany są zgodne.

int a = funkcja(1, 2);

// UWAGA: jeśli wrapper 'funkcja' nie odnosi się do żadnej funkcji,
// rzucany jest wyjątek 'std::bad_function_call'.

function<bool(short, short)> funkcja2;

if (!funkcja2)
{
    // Prawda, ponieważ 'funkcja2' nie została jeszcze przypisana.

    bool adjacent(long x, long y);
    funkcja2 = &adjacent; // OK — parametry i typ zwracany są konwertowalne.

    struct Test
    {
        bool operator()(short x, short y);
    };

    Test obiekt;

    // 'std::ref' zwraca wrapper dla obiektu 'obiekt' (jego operator()).
    funkcja = std::ref(obiekt);
}

funkcja = funkcja2; // OK — parametry i typy zwracane są konwertowalne.
```

Szablonowa klasa `function` została zdefiniowana w nagłówku `<functional>` bez potrzeby zmiany języka.

#### Uzupełnienie (C++14/17/20/23)

**C++14**

* W wielu implementacjach pojawiło się `make_function` (nie w standardzie, ale popularne).
* `std::function` lepiej współpracuje z lambdami niekopiowalnymi.

**C++17**

* `std::function` korzysta z `std::invoke`, co ujednoliciło sposób wywoływania funkcji, metod i funktorów.
* Poprawiono wydajność i semantykę przenoszenia.

**C++20**

* `std::function` może być używany w kontekstach `constexpr` (częściowo zależne od implementacji).
* Dodano `std::bind_front`, lżejszą alternatywę dla `std::bind`.

**C++23**

* Wprowadzono `std::function_ref` — lekki, niewłaścicielski wrapper na obiekty wywoływalne.
* `std::function` zyskał lepszą integrację z ranges i `std::expected`.

***

### Cechy typów (type traits) do metaprogramowania

**Metaprogramowanie** polega na tworzeniu programu, który tworzy lub modyfikuje inny program (albo samego siebie).
W C++ wiele tego typu operacji wykonuje się **w czasie kompilacji** za pomocą szablonów.

Komitet standaryzacyjny wprowadził bibliotekę ułatwiającą metaprogramowanie kompilacyjne — zestaw **cech typów (type traits)** dostępny w nagłówku `<type_traits>`.

Przykład metaprogramu w C++03: rekurencyjne obliczanie potęgi całkowitej przy użyciu szablonów:

```cpp
template <int B, int N>
struct Potega
{
    // rekurencyjne wywołanie i rekombinacja
    enum
    {
        WARTOSC = B * Potega<B, N - 1>::WARTOSC
    };
};

template <int B>
struct Potega<B, 0>
{
    // warunek zakończenia: N == 0
    enum
    {
        WARTOSC = 1
    };
};

int wynik = Potega<3, 4>::WARTOSC;
```

Wiele algorytmów działa na różnych typach danych; szablony wspierają programowanie generyczne, ale często algorytm potrzebuje informacji o typie użytym w instancjacji.
Taką informację dostarczają **cechy typów (type traits)** — metafunkcje i struktury, które:

* identyfikują kategorię typu lub jego właściwości,
* umożliwiają transformacje typów,
* pozwalają podejmować decyzje w czasie kompilacji.

Przykład użycia cech typów do wyboru implementacji:

```cpp
#include <type_traits>

using std::is_floating_point;
using std::is_integral;

// Pierwszy sposób działania.
template <bool B>
struct Algorytm
{
    template <class T1, class T2>
    static int wykonaj(T1& a, T2& b)
    {
        // ...
    }
};

// Drugi sposób działania (specjalizacja dla true).
template <>
struct Algorytm<true>
{
    template <class T1, class T2>
    static int wykonaj(T1 a, T2 b)
    {
        // ...
    }
};

// Instancjacja 'opracuj' automatycznie wybierze właściwy sposób działania.
template <class T1, class T2>
int opracuj(T1 a, T2 b)
{
    // Użyj drugiego sposobu tylko jeśli 'T1' jest całkowity, a 'T2' jest zmiennoprzecinkowy.
    return Algorytm<is_integral<T1>::value && is_floating_point<T2>::value>::wykonaj(a, b);
}
```

Dzięki cechom typów można też wykonywać **transformacje typów** (np. usuwanie `const`, dodawanie referencji), co jest niezbędne w zaawansowanych szablonach, gdzie `static_cast` i `const_cast` są niewystarczające.

**Uwaga praktyczna:** metaprogramowanie daje eleganckie i zwarte rozwiązania, ale debugowanie błędów kompilacji może być trudne — komunikaty kompilatora bywają długie i nieintuicyjne.

***

#### Uzupełnienie (C++14/17/20/23)

**C++14**

* Dodano wiele nowych traitsów, m.in. `std::is_final`, `std::is_null_pointer`.
* Wprowadzono aliasy `_t` i `_v`, np. `std::remove_const_t<T>`, `std::is_integral_v<T>` — ogromne uproszczenie metaprogramowania.

**C++17**

* Wiele traitsów stało się `constexpr`.
* Dodano `std::void_t`, kluczowy element nowoczesnego SFINAE.
* Dodano `std::is_invocable`, `std::invoke_result`, `std::is_swappable`, `std::is_nothrow_swappable`.

**C++20**

* Wprowadzenie **konceptów** (`std::integral`, `std::floating_point`, `std::regular`…) — w praktyce zastępują wiele klasycznych traitsów.
* Dodano `std::type_identity` i `std::remove_cvref_t`.
* Traitsy stały się szerzej dostępne w kontekstach `constexpr`.

**C++23**

* Rozszerzono `std::is_scoped_enum`.
* Dodano nowe narzędzia do detekcji typów w kontekście ranges i `std::expected`.
* Traitsy są szerzej wykorzystywane w standardowych konceptach.

***

### Jednolita metoda wyznaczania typu zwracanego obiektów funkcyjnych

Określenie typu zwracanego funkcji szablonowej w czasie kompilacji bywa nieintuicyjne, zwłaszcza gdy typ zwracany zależy od parametrów. Przykład:

```cpp
struct Jasny
{
    // Typ parametru jest równy typowi zwracanemu.
    int operator()(int) const;
    double operator()(double) const;
};

template <class Obj>
class Kalkulator
{
private:
    Obj element;
public:
    template <class Arg>
    Arg operator()(Arg& a) const
    {
        return element(a);
    }
};
```

Dla `Kalkulator<Jasny>` zwracany typ będzie zgodny z typem parametru `Arg`.
Jednak dla klasy `Zdezorientowany`:

```cpp
struct Zdezorientowany
{
    // Typ parametru nie jest równy typowi zwracanemu.
    double operator()(int) const;
    int operator()(double) const;
};
```

Instancjacja `Kalkulator<Zdezorientowany>` może prowadzić do niejednoznaczności i konwersji między `int` i `double`, co skutkuje ostrzeżeniami lub błędami.

TR1 wprowadziło, a C++11 przyjęło, szablonową metafunkcję **`std::result_of`**, która pozwala wyznaczyć typ zwracany wywołania obiektu funkcyjnego.
Przykład użycia w poprawionej wersji `Kalkulator`:

```cpp
#include <type_traits>

using std::result_of;

template <class Obj>
class KalkulatorVer2
{
private:
    Obj element;
public:
    template <class Arg>
    typename result_of<Obj(Arg)>::type operator()(Arg& a) const
    {
        return element(a);
    }
};
```

W ten sposób `KalkulatorVer2<Zdezorientowany>` nie wymaga konwersji ani nie generuje ostrzeżeń.

Różnica względem wersji TR1 polega na tym, że TR1 dopuszczał implementacje, które nie były w stanie określić typu wyniku w pewnych przypadkach.
Dzięki wprowadzeniu `decltype` w C++11, wersja `std::result_of` w C++11 **musi** wyznaczać typ wyniku we wszystkich przypadkach.

#### Uzupełnienie (C++14/17/20/23)

**C++14**

* Dodano alias `std::result_of_t<T>`.

**C++17**

* `std::result_of` zostało oznaczone jako **przestarzałe**.
* Zastępuje je **`std::invoke_result`** i alias `std::invoke_result_t`.

**C++20**

* `std::result_of` zostało **usunięte**.
* Jedynym poprawnym sposobem określania typu zwracanego jest `std::invoke_result_t`.

**C++23**

* `invoke_result` jest szeroko stosowane w ranges i nowych algorytmach.

***

## Ulepszona zgodność z C

Standard **C++11** wprowadził zestaw zmian mających na celu poprawę zgodności z językiem **C99**.

### **C++11**

#### Preprocesor

* makra wariadyczne (_variadic macros_),
* łączenie sąsiednich literałów łańcuchowych (wąskich i szerokich),
* funkcja `_Pragma()` — odpowiednik `#pragma`.

#### Typy i makra

* `long long` — typ całkowity gwarantowany co najmniej na 64 bity,
* `__func__` — makro zwracające nazwę bieżącej funkcji.

#### Nagłówki

* `cstdbool` (odpowiednik `stdbool.h`),
* `cstdint` (odpowiednik `stdint.h`),
* `cinttypes` (odpowiednik `inttypes.h`).

### **C++14 / C++17 / C++20 / C++23**

Brak zmian — żadna z późniejszych wersji standardu nie rozszerzała ani nie modyfikowała tej sekcji.

***

## Funkcje usunięte lub oznaczone jako przestarzałe (C++11 → C++17 → C++20)

Ta sekcja w C++11 obejmowała elementy oznaczone jako **przestarzałe (deprecated)** lub **usunięte**.
Nowsze standardy — szczególnie **C++17** — kontynuowały proces usuwania tych elementów, a **C++20** wprowadził ponownie `export`, ale w zupełnie innym znaczeniu (moduły).

Poniżej znajduje się uporządkowana lista zmian, z zaznaczeniem ewolucji w kolejnych standardach.

### C++11

* Termin **sequence point** został usunięty i zastąpiony precyzyjnym określeniem relacji między operacjami:
  _sequenced before_, _unsequenced_, _indeterminately sequenced_.

* Słowo kluczowe `export` oraz mechanizm eksportowanych szablonów zostały usunięte.
  Pozostało zarezerwowane (powróci dopiero w C++20, ale w innym znaczeniu — moduły).

* Dynamiczne specyfikacje wyjątków (`throw(...)`) zostały oznaczone jako przestarzałe.
  Zastępuje je **`noexcept`**.

* `std::auto_ptr` zostało oznaczone jako przestarzałe — zastępuje je `std::unique_ptr`.

* Klasy bazowe dla obiektów funkcyjnych (`std::unary_function`, `std::binary_function`),
  adaptery wskaźników (`ptr_fun`, `mem_fun`, `mem_fun_ref`) oraz bindery (`bind1st`, `bind2nd`)
  zostały oznaczone jako przestarzałe.

* Słowo kluczowe `register` zostało oznaczone jako przestarzałe.

### C++14

Standard C++14 **nie wprowadził żadnych zmian** dotyczących elementów przestarzałych lub usuniętych w tej sekcji.
Wszystkie pozycje z C++11 pozostały w tym samym stanie.

### C++17 (usunięcia elementów przestarzałych)

C++17 usuwa większość elementów oznaczonych jako przestarzałe w C++11:

* Dynamiczne specyfikacje wyjątków (`throw(...)`) — **całkowicie usunięte** z języka.

* `std::auto_ptr` — **usunięte**.

* `std::unary_function`, `std::binary_function` — **usunięte**.

* Adaptery wskaźników (`ptr_fun`, `mem_fun`, `mem_fun_ref`) — **usunięte**.

* Bindery (`bind1st`, `bind2nd`) — **usunięte**.

* Słowo kluczowe `register` — **usunięte** jako specyfikator klasy przechowywania.

### C++20

* Słowo kluczowe `export` zostało **przywrócone**, ale wyłącznie jako element **modułów**.
  Nie ma żadnego związku z eksportowanymi szablonami z C++98/03.

* Brak dodatkowych usunięć lub deprecacji w zakresie elementów wymienionych w tej sekcji.

### C++23

Standard C++23 **nie wprowadza nowych deprecacji ani usunięć** dotyczących elementów opisanych powyżej.
