# LAB 05

## Co zostało zrealizowane
Skrypt generuje proceduralny las w Blenderze (bpy).  
Dodano słownik `TYPY_ROSLIN` z parametrami drzew, krzewów, paproci i grzybów.  
Typ rośliny wybierany jest na podstawie pozycji (prosty system biomów).  
Rośliny są losowo rozmieszczane na terenie, mają losowe rozmiary i kolory.  
Wszystkie obiekty trafiają do kolekcji `Las` i podkolekcji: Drzewa, Krzewy, Paprocie, Grzyby.  
Dodano teren z modyfikatorem Displace, ustawiono kamerę i światła.  
Render zapisuje się automatycznie jako `las_05.png`.

## Uruchomienie
W trybie bez interfejsu:
`blender --background --python las05.py`

Z interfejsem Blendera:
`blender --python las05.py`