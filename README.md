# cro-respondent-resolve

About&hellip;

## Install

...

## Usage

...

--- 

(Bude později přesunuto.)

# Zadání

## Motivace

Pro všechny osoby v daném datasetu pocházejícim z OpenMedia se snažíme zjistit, jaká je to osoba. Přesněji řečeno, snažíme se ji identifikovat tzn. přiřadit ji jedinečný identifikátor osoby (UUID) uvedené v databázi. Pokud je respondent jednoznačně identifikován, pak mu přiřadíme do sloupce `matching_ids` UUID nalezené osoby, jinak ponecháme slupec nevyplněný. Pokud je nalezeno více osob, které se by se mohli shodovat,
pak oddělíme všechny nalezené identifikátory uvedeme ve sloupci `matching_ids` oddělené středníkem.

Pro respondenty, kteří nebyli nejsou jednoznačně identifikováni musíme provést manuální kontrolu/úpravu atributů respondenta. Důvod, proč se osoby nepárují vzhledem m databázi osob je:

a) v databázi se nenalézá požadovaná osoba
b) některé údaje, podle kteráých se sosoby párují jsou ve vstupních datech odlišné.

Pro potřeby čištění těchto neidentifikovaných respondentů potřebujeme vytvořit vhodné uživatelské prostředí, které celou práci usnadní a urychlí.

Datový soubor prozatím dostaneme jako Excel nebo v budoucnu bude již uložen v nějaké databázi a dostupný bude přes REST.

## Požadavky

### Funkční požadavky

- Pro každou osobu, která nebyla identifikována chceme:
  1. Označit ji jako nechtěnou tzv. obecnou osobu.
  2. Označit ji jako chtěnou tzn. chceme ji přidat do katalogu respondentů.
  3. Bylo nalezeno více osob a pak po uživateli chceme, aby vybral práve jedno UUID.

### Technické požadavky

- [ ] Aplikace poběží v kontejnerech (Docker).
- [ ] Aplikace bude konfigurovatelná.
- [ ] Server bude poskytovat REST API.
- [ ] Server bude řádně otestován -- stačí na úrovni REST API.
- [ ] Server bude naprogramován pomocí Python a Flask (doporučené)
- [ ] Klient bude naprogramován pomocí HTML/CSS/JavaScript.

- [ ] `README.md` file
- [ ] `docs` directory
- [ ] `src/` directory
  - [ ] `src/cro` namaspace package directory
  - [ ] `src/cro/respondent_resolve` package directory
  - [ ] `src/cro/respondent_resolve/__init__.py` top-level module
- [ ] `tests/` directory
- [ ] `setup.py` and/or `setup.cfg`
- [ ] `.gitignore`
- [ ] `Dockerfile`

- [ ] `.dockerignore`
- [ ] `docker-compose`

## Řešení (Poznámky)

Data co přicházejí z OpenMedia tzn. že v datech může být v podstatě cokoliv.
Dostaneme pole (data-frame) obsahující atributy osoby (respondenta).

```
Respondent
  + openmedia_id (String / UUID)
  + given_name (String, required)
  + family_name (String, optional)
  + affiliation (String, required)  # Zkratka nebo název politické strany nebo BEZPP
  + gender (int, required)
  + foreigner (int, required)
  + labels (String, required) # jednotlivé položky jsou oddělené středníky.
  + matching_ids (String / UUID, required)
```

```python
def identify_respondent(respondent) -> list[UUID]
  """
      Tato funkce vrací pole UUID, která mapují osobu z datasetu (OpenMedia) na osobu v katalogu (registru) osob.

  Tato funkce buď bude volat REST API registru osob nebo dodá DL požadovaný databázový dotaz.
  """
```

```
matching_ids (String / UUID, required) = ""
matching_ids (String / UUID, required) = "00000023-93ee-4754-a3c4-5748a4f420ad"
matching_ids (String / UUID, required) = "00000023-93ee-4754-a3c4-5748a4f420ad;00000023-11ee-2724-a3c4-5748a4f420ac"
```
