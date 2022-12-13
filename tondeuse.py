from dataclasses import dataclass
import sys
import math


@dataclass
class Joueur:
    id: int
    matter = 0
    cases = []
    robots = {}
    recycleurs = {}

    def reset(self):
        self.matter = 0
        self.cases.clear()
        self.robots.clear()
        self.recycleurs.clear()


@dataclass(frozen=True)
class Coord:
    ligne: int
    colonne: int

    def __repr__(self):
        return f"({self.ligne},{self.colonne})"


@dataclass
class Case:
    scrap_amount = 0
    owner = -1
    coord: Coord
    nb_unit = 0
    nb_recycler = 0
    can_build = False
    can_spawn = False
    in_recycler_range = False

    def __repr__(self):
        return f"{coord} owned by {self.owner}. {self.nb_unit} units / {self.nb_recycler} recycler"


@dataclass
class Robot:
    coord: Coord


@dataclass
class Recycleur:
    coord: Coord


def debug(msg):
    print(msg, file=sys.stderr, flush=True)


def afficheMap():
    debug(map_table)


map_table = []
width, height = [int(i) for i in input().split()]
j_ally, j_ennemy, j_neutre = Joueur(1), Joueur(0), Joueur(-1)
while True:
    # Nb matière a dispo par joueur
    j_ally.matter, j_ennemy.matter = [int(i) for i in input().split()]

    debug("Nouveau tour")

    # Vide les infos des joueurs
    [joueur.reset() for joueur in [j_ally, j_ennemy, j_neutre]]

    for i in range(height):
        map_table.append([])
        for j in range(width):
            coord = Coord(ligne=i, colonne=j)
            new_case = Case(coord)
            # owner: 1 = me, 0 = foe, -1 = neutral
            scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = [int(k) for k in
                                                                                                input().split()]
            if owner == -1:
                current_owner = j_neutre
            elif owner == 0:
                current_owner = j_ennemy
            else:
                current_owner = j_ally

            # INIT CASES
            new_case.scrap_amount = scrap_amount
            new_case.owner = current_owner
            new_case.nb_unit = units
            new_case.nb_recycler = recycler
            new_case.can_build = can_build
            new_case.can_spawn = can_spawn
            new_case.in_recycler_range = in_range_of_recycler
            map_table[i].append(new_case)

            # INIT JOUEUR
            current_owner.cases.append(new_case)
            # Add robots
            if units > 0:
                robolisto = []
                [robolisto.append(r) for r in range(units)]
                # for num in range(units):
                #     robolisto.append(Robot(coord))
                current_owner.robots.update({coord: robolisto})
            # Add recycler
            if recycler > 0:
                current_owner.recycleurs.update({coord:Recycleur(coord)})

    # TODO init les cases avec objets si c'est utile
    # TODO implementer une logique de jeu
    print("WAIT;")
