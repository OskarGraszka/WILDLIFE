<img src="images\qgis-logo.png" alt="qgis" width="200">

# WILDLIFE
<img src="images\wildlife.png" alt="wildlife" height="150">




WILDLIFE to moduł programu QGIS do przechowywania i edytowania obserwacji dotyczących występowania dzikich zwierząt zaprojektowany dla przyrodników i fotografów. Pozwala na przeglądanie i porządkowanie w jednym miejscu danych o gatunkach, liczności zaobserwowanych zwierząt, a także o tropach i śladach, siedlisku występowania oraz zdjęć poglądowych. Po pierwsze stanowi zbiór potrzebnych narzędzi do sprawnego i dokładnego zapisywania tzw. stwierdzeń w oparciu o notatki prowadzone w terenie albo punkty zapisane za pomocą urządzenia GPS. Po drugie, wyświetla wygodny podgląd wszystkich elementów wprowadzonej obserwacji w widoku mapy, a także etykiety. Razem z możliwościami dostosowania stylu wyświetlania warstw, jakie daje QGIS, zapewnia to maksymalną czytelność i pozwala na wizualną ocenę ilościową obserwacji nawet bez wykonywania specjalistycznych analiz na danych przestrzennych.
Do zastosowań WILDLIFE należą programy monitoringu gatunków i siedlisk przyrodniczych oraz monitoring ptaków, inwentaryzacje przyrodnicze, również na potrzeby ocen oddziaływania inwestycji na środowisko, zbieranie danych do opracowań naukowych, pracy profesjonalnych fotografów i zastosowań amatorskich. Wtyczka może stanowić ulepszoną wersję listy zaobserwowanych gatunków dla birdwatchera, pomagać w optymalnym rozmieszczeniu fotopułapek, projektowaniu drogowych przejść dla zwierząt, przyspieszać przenoszenie do postaci cyfrowej archiwalnych danych z kartowania gatunków.

Przyrodnicy poruszają się często w terenie z turystycznymi odbiornikami GPS, zapisując na tych urządzeniach lokalizację swoich obserwacji w formacie GPX. Format ten pozwala na zapis poza samą lokalizacją, również opisu daty i godziny wprowadzenia punktu, tzw. waypoint. Jednym z założeń wtyczki WILDLIFE jest ułatwienie użytkownikowi przenoszenia danych z pliku GPX (dodanego uprzednio do mapy w QGIS) do bazy danych.

<img src="images\schemat_1.png" alt="s1" height="300">

## Struktura wtyczki

Katalog wtyczki WILDLIFE oprócz plików zawierających kod i interfejs wtyczki zawiera także folder WILDLIFE_database. Znajdują się w nim dane dotyczące wszystkich wprowadzonych obserwacji. W podkatalogu shp umieszczone zostały pliki shapefile, zawierające tabele obserwacji i fotopułapek oraz ich lokalizację. W podkatalogu photos przechowywane są natomiast przypisane do obserwacji zdjęcia.

<img src="images\struktura_wtyczki.jpg" alt="s_w" height="500">

Katalog WILDLIFE_database można zastępować innym katalogiem (z inną bazą danych) przy ścisłym zachowaniu struktury i nazw podkatalogów oraz tabel plików shapefile. Najbezpieczniej jest tworzyć nowy katalog bazy danych poprzez skopiowanie pierwotnie pobranego wraz z wtyczką katalogu WILDLIFE_database. Zmiana bazy danych używanej przez wtyczkę nie musi odbywać się poprzez podmianę folderu WILDLIFE_database w katalogu wtyczki. Katalog bazy danych można również wskazać z poziomu okna wtyczki (por. rozdział Zakładka Ustawienia bazy danych). Lokalizacja ostatnio używanej bazy danych jest zapamiętywana przez wtyczkę. Przy uruchomieniu wtyczka łączy się z ostatnio używaną bazą danych.

## Schemat bazy danych

Baza danych WILDLIFE realizowana jest przez tabele plików shapefile oraz katalog przechowujący pliki graficzne. Relacja typu „jeden do wielu” realizowana jest poprzez nadanie wartości atrybutowi id_fotop w tabeli obserwacji. Wartość tego atrybutu odpowiada numerowi identyfikacyjnemu fotopułapki, z której została zarejestrowana obserwacja. Jeśli wartość ta nie jest nadana, obserwacja nie jest przyporządkowana do żadnej fotopułapki. Każdy obiekt bazy danych (zarówno obserwacja jak i fotopułapka) ma przypisaną georeferencję, nadawaną poprzez pobranie współrzędnych z pliku GPX lub bezpośrednie wskazanie lokalizacji na mapie. Współrzędne obiektów bazy danych przechowywane w plikach shapefile są współrzędnymi układu geodezyjnego geograficznego World Geodetic System’84 (EPSG: 4326).

<img src="images\spis.jpg" alt="spis" height="700">

# PRZEGLĄDANIE DANYCH
## Wizualizacja danych

Obserwacje z bazy danych wizualizowane są na mapie za pomocą znaków kartograficznych przedstawionych w poniższej tabeli. Wygląd etykiety zależny jest od typu obserwacji (ssak/ptak) oraz tego czy gatunek oznaczony został jako drapieżny. Na wyświetlany tekst etykiety składa się liczba odpowiadająca liczności obserwacji oraz skrót nazwy gatunku nadawany przez użytkownika na potrzeby wyświetlania etykiet. Przy znaku fotopułapki nie wyświetla się żadna etykieta.

<img src="images\tab.jpg" alt="tab" height="200">

<img src="images\poglad.jpg" alt="poglad" height="600">

## Podpowiedzi na mapie

Oprócz informacji zawartych w etykiecie obiektu użytkownik może podejrzeć pełnię informacji dotyczących obiektu poprzez wyświetlenie podpowiedzi na mapie. Aktywowanie podpowiedzi na
mapie wymaga ich włączenia w menu Widok lub w Pasku narzędzi atrybutów. Warstwa, z której chcemy zobaczyć podpowiedzi musi być warstwą aktywną w Panelu warstwa

<img src="images\maptips.jpg" alt="maptips" height="200">

Podpowiedź do obiektu będącego fotopułapką zawiera opis, datę i godzinę instalacji oraz siedlisko, natomiast podpowiedzi do obserwacji zawierają dodatkowo pełną nazwę gatunku, informację dotyczącą dokładności liczności obserwacji, kierunek przemieszczania oraz informację czy była to bezpośrednia obserwacja zwierzęcia, odchody, tropy czy też inne ślady jego bytności. W tym przypadku w podpowiedzi wyświetlają się też miniatury zdjęć przypisanych do danej obserwacji.

<img src="images\maptip_f.jpg" alt="maptip_f" height="200">
<img src="images\maptip.jpg" alt="maptip" height="200">

## Tryb przeglądania i edycji obserwacji

Uzyskanie pełnej informacji dotyczącej obiektu bazy danych umożliwia również Tryb przeglądania i edycji obserwacji w oknie głównym wtyczki WILDLIFE. Po włączeniu tego trybu i wskazaniu obiektu na mapie w oknie wtyczki wyświetlą się wszystkie dotyczące go informacje oraz miniatury przypisanych zdjęć. Po kliknięciu na miniaturę zdjęcia pojawia okno z jego powiększeniem.
Jeśli w bliskim otoczeniu wskazanej na mapie lokalizacji znajduje się więcej niż jeden obiekt lub obiekty nachodzą na siebie, pojawi się okno z wybieralną listą fotopułapek i obserwacji znajdujących się w bliskim otoczeniu wskazanego miejsca. Wybór obiektu listy skutkuje wyświetleniem informacji o nim w oknie wtyczki.

<img src="images\przegladanie.jpg" alt="przegladanie" height="500">

<img src="images\gesto.jpg" alt="gesto" height="300">

# WPROWADZANIE I EDYCJA DANYCH
## Przyciski zakładek

Wtyczka WILDLIFE składa się z trzech zakładek: Ustawienia bazy danych, Nowa obserwacja oraz Tryb przeglądania i edycji obserwacji. Zmiany zakładek umożliwiają trzy przyciski umieszczone w górnej części wtyczki. Ponad nimi umieszczony został także pasek wyświetlający komunikaty i podpowiedzi ułatwiające użytkownikowi pracę z wtyczką.

<img src="images\zakladki.jpg" alt="zakladki" height="500">

## Zakładka Ustawienia bazy danych

Domyślną bazą danych która ustawia się automatycznie przy pierwszym uruchomieniu wtyczki jest baza danych zapisana w plikach wtyczki WILDLIFE. Zmianę katalogu bazy danych przeprowadza się za pomocą przycisku Ustaw katalog ‚Wildlife_database’. Po kliknięciu tego przycisku pojawia się okno wyboru katalogu. Należy wskazać katalog Wildlife_database bazy danych, którą chcemy ustawić. Jeśli wskazana baza danych nie jest poprawna (występuje niezgodność struktury, nazw katalogów lub nazw plików shapefile) pojawi się okno dialogowe informujące o błędzie i baza nie zostanie zmieniona. Po poprawnym połączeniu z bazą danych, do widoku mapy zostaną dodane warstwy Obserwacja i Fotopułapka. W przypadku próby zmiany bazy danych program wyświetli również zapytanie czy usunąć z mapy warstwy poprzedniej bazy danych.

<img src="images\ustawiono_bd.jpg" alt="ustawiono_bd" height="500">
<img src="images\dodatkowy_komunikat.jpg" alt="dodatkowy_komunikat" height="500">
<img src="images\elements.jpg" alt="elements" height="500">

Należy pamiętać, że wtyczka nie będzie działać poprawnie, jeżeli katalog bazy danych Wildlife_database będzie miał inną nazwę lub strukturę plików shapefile i podkatalogów niż pierwotnie przygotowana baza danych. Możliwe jest więc korzystanie z kilku baz danych (choć nie jednocześnie za pomocą wtyczki WILDLIFE). Takie rozwiązanie może okazać się korzystne dla użytkownika, który chce podzielić zestawy przechowywanych danych (na przykład ze względu na kryterium czasowe, przestrzenne lub inne). Dobrą praktyką w takim przypadku jest wykonanie kopii pustej bazy danych przed rozpoczęciem edycji. Taka kopia pozwoli zachować strukturę bazy danych.

Kopię bazy danych można wykonać znajdując odpowiedni katalog Wildlife_database i kopiując go do lokalizacji docelowej lub za pomocą przycisku Wykonaj backup. Po wciśnięciu tego przycisku otwiera się okno dialogowe, w którym należy wskazać katalog docelowy kopii bazy danych. Można również wykonać kopię bazy danych spakowaną do pliku zip. Służy do tego przycisk Wykonaj backup ZIP.
Przy każdym kolejnym uruchomieniu wtyczka łączy się z ostatnio używaną bazą danych.

## Zakładka Nowa obserwacja

Zakładka Nowa obserwacja pozwala wprowadzać do bazy danych nowe obserwacje i fotopułapki.

<img src="images\nowa_obs.jpg" alt="nowa_obs" height="500">

Wprowadzenie nowego obiektu bazy danych powinno się zacząć od określenia jego typu. Rozwijalna lista w lewym górnym rogu zakładki pozwala określić czy wprowadzana będzie fotopułapka, obserwacja ptaka czy obserwacja ssaka. Od wyboru elementu tej listy zależy które elementy zakładki będą aktywne (właściwe dla fotopułapki czy właściwe dla obserwacji) oraz jakimi wartościami wypełnią się wybieralne listy gatunków (nazwami gatunkowymi ssaków czy ptaków). Po wybraniu odpowiedniej pozycji na tej liście można przejść do wypełniania kolejnych pól zakładki.

<img src="images\rodzaj.jpg" alt="rodzaj" height="500">

Liczność obserwacji określa się wskazując wartość w polu wyboru pokazanym na poniższym rysunku. Nie da się w tym polu ustawić wartości mniejszej niż 1. Obok znajduje się pole wyboru, w którym można zaznaczyć czy podana liczność jest wartością precyzyjną czy przybliżoną. Warto zwrócić uwagę na to, że wartość tego atrybutu w przypadku obserwacji, przy których nie da się określić liczby osobników (jak ślady żerowania czy odchody) może służyć do wagowania obserwacji, co może przydać się przy analizach gęstości występowania.

<img src="images\licznosc.jpg" alt="licznosc" height="500">

Kierunek przemieszczania obserwowanego osobnika można określić poprzez wybór odpowiedniego elementu listy wyboru kierunku.

<img src="images\kierunek.jpg" alt="kierunek" height="500">

Jeśli obserwacji dokonano z fotopułapki, w oknie wyboru fotopułapki należy wybrać fotopułapkę. Można to zrobić wskazując fotopułapkę na mapie lub wybierając ją z listy wszystkich fotopułapek. W ten sposób zostanie utworzona relacja między rekordem z tabeli obserwacji a rekordem fotopułapki. Obserwacja, która nie jest zdjęciem z fotopułapki, powinna mieć na tej liście wybraną wartość Brak.

<img src="images\wybor_fotopulapki.jpg" alt="wybor_fotopulapki" height="500">

Kolejna grupa pól wyboru służy do określania czy obserwacja była obserwacją bezpośrednią zwierzęcia, rejestracją tropów, odchodów czy inną. Można zaznaczyć wiele pól wyboru, jeśli wymaga tego sytuacja.

<img src="images\grupa_pol_wyboru.jpg" alt="grupa_pol_wyboru" height="500">

Po wyborze typu obserwacji (ptaka lub ssaka) lista gatunków uzupełnia się wartościami właściwymi dla ssaków lub ptaków (są to unikalne wartości wybrane spośród już wprowadzonych do bazy danych, jak na poniższym rysunku). Po uruchomieniu pustej bazy danych (czyli bazy nie zawierającej żadnych rekordów typu obserwacja ssaka lub obserwacja ptaka) lista ta będzie pusta. Do wprowadzania nowych elementów listy gatunków służy przycisk oznaczony znakiem „+” (por. rysunek). Po jego przyciśnięciu pojawią się dwa pola tekstowe; jedno z nich służy do wprowadzenia skrótu nazwy gatunkowej, drugie do wprowadzania pełnej nazwy gatunkowej. Choć maksymalna długość ciągu znaków przewidziana dla pola skrótu nazwy gatunkowej to 20 znaków, zalecane jest stosowanie skrótów o długości do 3 znaków. Ponieważ skrót ten (razem z licznością obserwacji) jest wykorzystywany do tworzenia etykiety obserwacji na mapie, dobrą praktyką jest stosowanie skrótów nazw łacińskich, które można również umieszczać w nawiasie przy pełnej nazwie gatunkowej. Po wypełnieniu pól tekstowych ważne jest ich zatwierdzenie przyciskiem OK, który doda nowy gatunek do listy gatunków. Domyślnym elementem tej listy staje się ostatnio dodana wartość. Każdy element listy gatunków składa się z przyporządkowanego skrótu oraz pełnej nazwy gatunkowej. Elementy listy szeregowane są alfabetycznie po wartości pełnej nazwy gatunkowej.

<img src="images\gatunek.jpg" alt="gatunek" height="500">

Wtyczka WILDLIFE przewiduje dla każdej obserwacji nadanie dodatkowej wartości oznaczającej czy jest to obserwacja gatunku drapieżnego.
Edytowalna lista wyboru widoczna na poniższym rysunku służy wprowadzaniu siedlisk, w których dokonano obserwacji. Po włączeniu zakładki na liście pojawiają się unikatowe wartości spośród nazw siedlisk już wprowadzonych do bazy danych. Można wybrać siedlisko z listy lub wpisać nazwę, jeśli nie występuje na liście.

<img src="images\siedlisko.jpg" alt="siedlisko" height="500">

Blok przycisków i pól edycyjnych widoczny na poniższym rysunku to część zakładki Nowa obserwacja grupująca pola danych, których pobranie jest możliwe z pliku GPX (format pliku, w którym odbiornik GPS zapisuje dodawane przez użytkownika istotne punkty trasy, tzw. waypointy). Wymagane jest do tego wcześniejsze wczytanie pliku GPX do mapy. Po naciśnięciu przycisku z symbolem odbiornika GPS (podświetlenie przycisku na zielono oznacza aktywację na mapie funkcji wskazywania obiektu z warstwy GPX), można wskazać punkt typu waypoint na warstwie GPX, reprezentujący lokalizację właśnie wprowadzanej obserwacji. W celu ułatwienia użytkownikowi wskazania właściwego punktu, wtyczka – w czasie aktywacji narzędzia wskazywania – wyświetla etykiety z nazwą jaką użytkownik nadał punktowi w terenie. Po poprawnym wskazaniu punktu pobierane są jego współrzędne, data, godzina, a także opis (do którego kopiowany jest nazwa punktu nadana przez obserwatora w terenie).

<img src="images\GPX.jpg" alt="GPX" height="500">

Po włączeniu zakładki Nowa obserwacja pola daty i godziny uzupełniają się automatycznie (data i godzina włączenia zakładki), pole dotyczące opisu jest domyślnie puste. Jeśli użytkownik nie pobiera lokalizacji obserwacji lub fotopułapki z pliku GPX, musi ją wskazać na mapie. W tym celu musi wcisnąć przycisk Wskaż. Podświetlenie tego przycisku na zielono oznacza aktywację na mapie narzędzia wskazywania lokalizacji na mapie. Po wskazaniu położenia obserwacji lub fotopułapki, w jej miejscu pojawi się czerwony znacznik. W celu skorygowania lokalizacji obserwacji należy wcisnąć jeszcze raz przycisk Wskaż i wskazać miejsce powtórnie.

<img src="images\wskaz.jpg" alt="wskaz" height="500">

Nie jest możliwy zapis obserwacji lub fotopułapki bez nadania georeferencji (wskazania lub po-brania z GPX jej lokalizacji).
Wtyczka przewiduje dodanie do każdej obserwacji do trzech zdjęć. Zdjęcia dodaje się za pomocą przycisku Dodaj zdjęcia, który otwiera okno dialogowe wyboru plików graficznych. Można w tym oknie wskazać kilka zdjęć na raz. Miniatury dodawanych zdjęć pojawiają się na pasku widocznym na poniższym rysunku. Zdjęcia usuwa się przez kliknięcie przycisku „x” w prawym górnym rogu miniatury. Można również włączyć podgląd zdjęcia, klikając na jego miniaturę.

<img src="images\zdjecia.jpg" alt="zdjecia" height="500">

Wprowadzenie nowego obiektu bazy danych potwierdza się lub anuluje przyciskami przedstawionymi na poniższym rysunku.

<img src="images\anuluj_zapisz.jpg" alt="anuluj_zapisz" height="500">

## Zakładka Tryb przeglądania i edycji obserwacji

Zakładka Tryb przeglądania i edycji obserwacji nie różni się od zakładki Nowa obserwacja pod względem layout’u. Wartości atrybutów przechowywanych w bazie wyświetlają się w odpowiednich polach dokładnie w ten sam sposób, co w zakładce wcześniej omówionej i w ten sam sposób mogą być zmieniane. Ich edycja jest możliwa po wciśnięciu przycisku Edytuj w lewym dolnym rogu okna wtyczki. W trybie edycji można również usunąć obiekt. Jedynym ograniczeniem edycji jest brak możliwości zmiany rodzaju raz wprowadzonej obserwacji (np. nie można zmienić fotopułapki na obserwację lub obserwacji ptaka na obserwację ssaka). Użytkownik chcąc zmienić rodzaj obserwacji musi usunąć jeden obiekt i zastąpić go tworząc nowy w jego miejsce.

<img src="images\edycja_rodzaju.jpg" alt="edycja_rodzaju" height="500">
<img src="images\Zakladka_przegladanie.jpg" alt="Zakladka_przegladanie" height="500">

Po naciśnięciu przycisku uruchamiającego zakładkę, uruchamia się narzędzie na mapie pozwalające wskazać obiekt (o aktywności tego narzędzia świadczy podświetlenie przycisku zakładki na zielono). Po wskazaniu obiektu na mapie (jeśli w bliskim otoczeniu wskazanej lokalizacji jest więcej niż jeden obiekt, należy wybrać go z listy obiektów, która się pojawi) w oknie zakładki pojawią się wszystkie dotyczące go informacje i zdjęcia.
Po wskazaniu na mapie w trybie przeglądania obiektu będącego fotopułapką, w części okna odpowiadającej za relacje między obserwacjami a fotopułapką, aktywuje się przycisk Obserwacje z tej fotopułapki. Po jego naciśnięciu pojawi się lista z obserwacjami wykonanymi z tej fotopułapki. Po naciśnięciu elementu tej listy, w oknie zakładki wyświetlą się informacje dotyczące danej obserwacji.

<img src="images\z_fotopułapki.jpg" alt="z_fotopułapki" height="500">
<img src="images\sarna_z_foto.jpg" alt="sarna_z_foto" height="500">

Rysunki poniższej galerii przedstawiają przykłady prawdziwych obserwacji wyświetlane w opisywanej zakładce, razem z podglądem zdjęcia i podpowiedzią na mapie.

<img src="images\Alces.jpg" alt="Alces" height="500">
<img src="images\Bison.jpg" alt="Bison" height="500">
<img src="images\Cervus.jpg" alt="Cervus" height="500">
<img src="images\Ursus.jpg" alt="Ursus" height="500">


## ANALIZY PRZESTRZENNE

Dane zebrane i przechowywane za pomocą wtyczki WILDLIFE można również przeglądać w tabeli atrybutów warstw bazy danych. Nie zaleca się jednak edycji danych w tabeli z pominięciem okna wtyczki. W szczególności nie dopuszczalna jest edycja pól z nazwami zdjęć; usunięcie nazwy zdjęcia w tabeli nie powoduje usunięcia zdjęcia z bazy, co skutkuje niepotrzebnym przechowywaniem zbędnych obrazów. Tabele z rozdziału Schemat bazy danych opisują dokładnie, które kolumny tabel Obserwacja i Fotopułapka odpowiadają poszczególnym atrybutom opisowym bądź ilościowym. Posiadając te informacje, można przetwarzać dane z tabel i przeprowadzać różnorodne analizy przestrzenne.

<img src="images\tabela_atr.jpg" alt="tabela_atr" height="500">

Jako przykład przetworzenia danych można tutaj podać eksport danych odnoszących się do jednego gatunku do innej warstwy i nadanie jej własnego stylu wizualizacji. Dla potrzeb wykonania niniejszej instrukcji wyeksportowano dane dotyczące obserwacji danieli w Puszczy Bolimowskiej z okresu jednego roku. Następnie przeprowadzono na tych danych kilka prostych analiz i wizualizacji. Wykonano mapę liczności obserwowanych stad danieli, analizę występowania danieli zależnie od pory roku oraz mapę skupień obserwacji. Mapa występowania w zależności od pory roku może nie mieć większego sensu w przypadku tak nielicznego zbioru obserwacji danieli, ale nie brak gatunków, w przypadku których zbadanie takiej zależności wyglądałoby znacznie ciekawiej. Są to jedynie przykłady dalszego wykorzystania zgromadzonych danych i służą zarysowaniu możliwości jakie daje baza danych.

<img src="images\stada_danieli.jpg" alt="stada_danieli" height="500">
<img src="images\mapa_skupien.jpg" alt="mapa_skupien" height="500">
<img src="images\woy.jpg" alt="woy" height="500">
