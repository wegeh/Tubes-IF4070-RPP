% FEATURES
% ======================================
% 1. BASE: Primary coffee component (espresso, brewed_coffee)
% 2. MILK: Type of milk used (none, steamed_milk, foamed_milk, microfoam, cold_milk)
% 3. ADDITIVES: Extra ingredients (none, hot_water, sugar, chocolate)
% 4. PREPARATION: Method of preparation (pressure, boiled, diluted, combined)
% 5. SERVING: Serving style (small_cup, tall_glass, large_cup, demitasse, unfiltered)
% 6. ORIGIN: Country/region of origin
% ======================================

coffee(espresso, espresso, none, hot_water, pressure, small_cup, italy).
coffee(bica, espresso, none, hot_water, pressure, demitasse, portugal).
coffee(americano, espresso, none, hot_water, diluted, large_cup, italy).
coffee(latte, espresso, steamed_milk, none, combined, tall_glass, italy).
coffee(caffe_macchiato, espresso, foamed_milk, none, combined, small_cup, italy).
coffee(cappuccino, espresso, steamed_and_foamed, none, combined, cup, italy).
coffee(flat_white, espresso, microfoam, none, combined, small_cup, australia_new_zealand).
coffee(latte_macchiato, espresso, steamed_milk, none, combined, tall_glass, italy).
coffee(kopi_tubruk, brewed_coffee, none, sugar, boiled, unfiltered, indonesia).
coffee(greek_coffee, brewed_coffee, none, sugar, boiled, unfiltered, greece).
coffee(cafe_mocha, espresso, steamed_milk, chocolate, combined, cup, italy).

% ======================================
% DETAILED FEATURE VALUES FOR EACH COFFEE
% ======================================
% 
% 1. ESPRESSO
%    - Base: espresso (finely ground coffee, hot water forced under pressure)
%    - Milk: none
%    - Additives: hot_water
%    - Preparation: pressure (espresso machine, ~9 bar pressure)
%    - Serving: small_cup (demitasse, ~30ml shot)
%    - Origin: italy
%
% 2. BICA
%    - Base: espresso (similar to espresso but lighter roast)
%    - Milk: none
%    - Additives: hot_water
%    - Preparation: pressure (extracted to greater volume than espresso)
%    - Serving: demitasse (Portuguese style)
%    - Origin: portugal
%
% 3. AMERICANO
%    - Base: espresso
%    - Milk: none
%    - Additives: hot_water (1:3 to 1:4 ratio with espresso)
%    - Preparation: diluted (hot water added to espresso)
%    - Serving: large_cup
%    - Origin: italy
%
% 4. LATTE
%    - Base: espresso
%    - Milk: steamed_milk (large amount, topped with small foam)
%    - Additives: none
%    - Preparation: combined (espresso mixed with steamed milk)
%    - Serving: tall_glass (or large cup, ~240ml+)
%    - Origin: italy
%
% 5. CAFFÈ MACCHIATO
%    - Base: espresso
%    - Milk: foamed_milk (small amount, "stained" espresso)
%    - Additives: none
%    - Preparation: combined (espresso with milk foam spot)
%    - Serving: small_cup (demitasse)
%    - Origin: italy
%
% 6. CAPPUCCINO
%    - Base: espresso
%    - Milk: steamed_and_foamed (equal parts: espresso, steamed milk, foam)
%    - Additives: none
%    - Preparation: combined (layered thirds)
%    - Serving: cup (150-180ml)
%    - Origin: italy
%
% 7. FLAT WHITE
%    - Base: espresso
%    - Milk: microfoam (velvety steamed milk with fine bubbles)
%    - Additives: none
%    - Preparation: combined (higher coffee to milk ratio than latte)
%    - Serving: small_cup (smaller than latte)
%    - Origin: australia_new_zealand
%
% 8. LATTE MACCHIATO
%    - Base: espresso
%    - Milk: steamed_milk (milk "stained" with espresso, layered)
%    - Additives: none
%    - Preparation: combined (espresso added to milk, not vice versa)
%    - Serving: tall_glass (shows distinct layers)
%    - Origin: italy
%
% 9. KOPI TUBRUK
%    - Base: brewed_coffee (coarsely ground)
%    - Milk: none
%    - Additives: sugar (boiled together with coffee)
%    - Preparation: boiled (grounds boiled with water and sugar)
%    - Serving: unfiltered (grounds settle at bottom)
%    - Origin: indonesia
%
% 10. GREEK COFFEE
%     - Base: brewed_coffee (very finely ground)
%     - Milk: none
%     - Additives: sugar (optional, boiled with coffee in briki)
%     - Preparation: boiled (boiled in small pot called briki)
%     - Serving: unfiltered (grounds in cup, strong brew)
%     - Origin: greece
%
% 11. CAFÉ MOCHA
%     - Base: espresso
%     - Milk: steamed_milk
%     - Additives: chocolate (chocolate syrup or cocoa powder)
%     - Preparation: combined (espresso + chocolate + steamed milk)
%     - Serving: cup (often topped with whipped cream)
%     - Origin: italy
%
% ======================================

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, espresso) :-
    Base = espresso, Milk = none, Additives = hot_water, 
    Preparation = pressure, Origin = italy, Serving = small_cup.

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, bica) :-
    Base = espresso, Milk = none, Additives = hot_water, 
    Preparation = pressure, Origin = portugal, Serving = demitasse.

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, americano) :-
    Base = espresso, Additives = hot_water, Preparation = diluted.

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, latte) :-
    Base = espresso, Milk = steamed_milk, Additives = none,
    Serving = tall_glass, Origin = italy.

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, caffe_macchiato) :-
    Base = espresso, Milk = foamed_milk, Additives = none,
    Serving = small_cup, Origin = italy.

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, cappuccino) :-
    Base = espresso, Milk = steamed_and_foamed, Additives = none.

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, flat_white) :-
    Base = espresso, Milk = microfoam, Additives = none.

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, latte_macchiato) :-
    Base = espresso, Milk = steamed_milk, Serving = tall_glass, 
    Preparation = combined, Origin = italy,
    !.

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, kopi_tubruk) :-
    Base = brewed_coffee, Additives = sugar, 
    Preparation = boiled, Origin = indonesia.

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, greek_coffee) :-
    Base = brewed_coffee, Preparation = boiled, 
    Serving = unfiltered, Origin = greece.

classify_coffee(Base, Milk, Additives, Preparation, Serving, Origin, cafe_mocha) :-
    Base = espresso, Milk = steamed_milk, Additives = chocolate.

classify_coffee(_, _, _, _, _, _, unknown).

identify_coffee(Name, Base, Milk, Additives, Preparation, Serving, Origin) :-
    coffee(Name, Base, Milk, Additives, Preparation, Serving, Origin).

has_espresso_base(Name) :- coffee(Name, espresso, _, _, _, _, _).
has_milk(Name) :- coffee(Name, _, Milk, _, _, _, _), Milk \= none.
is_boiled(Name) :- coffee(Name, _, _, _, boiled, _, _).
from_italy(Name) :- coffee(Name, _, _, _, _, _, italy).