from dataclasses import dataclass, field
import sys
import math

# region dataclass
@dataclass
class Joueur:
    id: int
    matter : int = field(default_factory=int)
    # si on ne fait pas field mais direct le type, on aura une variable de classe au lieu de variable d'instance
    cases: list = field(default_factory=list)
    robots: dict = field(default_factory=dict)
    recycleurs: dict = field(default_factory=dict)

    def reset(self):
        self.matter = 0
        self.cases.clear()
        self.robots.clear()
        self.recycleurs.clear()


@dataclass(eq=False)
class Coord:
    x: int
    y: int

    def __repr__(self):
        return f"({self.x},{self.y})"


@dataclass
class Case(Coord):
    scrap_amount : int = field(default_factory=int)
    owner : int = field(default_factory=int)
    nb_unit : int = field(default_factory=int)
    nb_recycler : int = field(default_factory=int)
    can_build = False
    can_spawn = False
    in_recycler_range = False
    scrap_value = 0  # Total scrap avec case adjacente

    def __init__(self, c: Coord):
        super().__init__(c.x, c.y)

    def __repr__(self):
        return f"Case{super().__repr__()} a {self.owner} [{self.nb_unit} units/{self.nb_recycler} recycler]"

    def calcul_scrap_value(self):
        # TODO
        pass

# @dataclass
# class Robot(Coord):
#     def __init__(self, c: Coord):
#         super().__init__(c.x, c.y)
#
#
# @dataclass
# class Recycleur(Coord):
#     def __init__(self, c: Coord):
#         super().__init__(c.x, c.y)
# endregion dataclass

# region helper
def debug(msg):
    print(msg, file=sys.stderr, flush=True)


def afficheMap():
    # TODO faire mieux quand on aura la motiv
    debug(map_table)
# endregion helper


def move_all_to(dest : Coord):
    robots = j_ally.robots
    for coord, nb_robot in robots.items():
        output.append(f"MOVE {nb_robot} {coord.x} {coord.y} {dest.x} {dest.y}")


def attack_recycler():
    recyclers = j_ennemy.recycleurs
    if len(recyclers) > 0:
        move_all_to(list(recyclers.keys())[0])
    else:
        # TODO gerer le else
        move_all_to(Coord(5,5))

map_table = []
width, height = [int(i) for i in input().split()]
j_ally, j_ennemy, j_neutre = Joueur(1), Joueur(0), Joueur(-1)
output = []


def build_recycler():
    """
    On regarde si construire un recycler peut rapporter +10 matériaux
    Si oui, on prend celui qui rapporte un max
    """
    # TODO
    pass


def build_robot():
    """
    Après avoir fait des recyclers, s'il reste des matérieux
    On voit pour construire des robots
    """
    # TODO
    pass


while True:
    # Nb matière a dispo par joueur
    j_ally.matter, j_ennemy.matter = [int(i) for i in input().split()]

    # Vide les infos des joueurs
    [joueur.reset() for joueur in [j_ally, j_ennemy, j_neutre]]
    output = []

    for i in range(height):
        map_table.append([])
        for j in range(width):
            # owner: 1 = me, 0 = foe, -1 = neutral
            scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = [int(k) for k in
                                                                                                input().split()]
            coord = Coord(j,i)
            new_case = Case(coord)
            if owner == -1:
                current_owner = j_neutre
            elif owner == 0:
                current_owner = j_ennemy
            else:
                current_owner = j_ally

            # INIT CASES
            new_case.scrap_amount = scrap_amount
            new_case.owner = owner
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
                current_owner.robots.update({coord: units})
            # Add recycler
            if recycler > 0:
                current_owner.recycleurs.update({coord:recycler})

    # REFRESH CASE WITH SCRAP POSSIBLE VALUE
    for i in range(height):
        for j in range(width):
            map_table[i][j].calcul_scrap_value()

    # BUILD
    build_recycler()
    build_robot()
    # MOVE
    attack_recycler()
    # SPAWN

    print("WAIT") if len(output) == 0 else print(";".join(output))
