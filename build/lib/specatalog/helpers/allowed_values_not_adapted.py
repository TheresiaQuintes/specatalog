from enum import Enum

class Names(str, Enum):
    richert = "richert"
    maylaender = "maylaender"
    thielert = "thielert"
    redman = "redman"


class Solvents(str, Enum):
    toluene = "toluene"
    water = "water"


class Devices(str, Enum):
    elexsys = "elexsys"
    emx_nano = "emx_nano"


class FrequencyBands(str, Enum):
    s = "s"
    x = "x"
    q = "q"
    w = "w"


class PulseExperiments(str, Enum):
    peanut = "peanut"
    peldor = "peldor"
    tn = "tn"
    saturation_recovery = "sr"
    esenut = "esenut"

class Timedomains(str, Enum):
    ns = "ns"
    fs = "fs"

class Chromophores(str, Enum):
    bdp0 = "bdp0"
    bdp1 = "bdp1"
    ndi0 = "ndi0"
    pent = "pent"
    per = "per"
    pdi0 = "pdi0"
    pdi2 = "pdi2"
    pdi4 = "pdi4"
    por0 = "por0"
    por1 = "por1"
    por2 = "por2"


class Doublets(str, Enum):
    no1 = "no1"
    no2 = "no2"
    no3 = "no3"
    no4 = "no4"
    no5 = "no5"
    tri = "tri"


class Linker(str, Enum):
    bi = "bi"
    co = "co"
    sup_h_tz = "sup_h_tz"
    xy = "xy"


class Radicals(str, Enum):
    trp = "trp"
    flav = "flav"
