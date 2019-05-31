# coding: utf-8
DEBUGFLAG = False
COUNTsilosdobavka = 5  # от 0
COUNTsiloszerno = 9  # от 0
COUNTsiloskorm = 5  # от 0
OFFSETsiloszerno = 37  # rg37
OFFSETsilosdobavka = 47  # rg28
OFFSETsilosmaslo = 53
OFFSETsiloskorm = None
OFFSETflagstate = 7  # rg7
LASTREGADDR = 57
# SQL
IDPRODUCT = 0
NAMEPRODUCT = 1
IDZERNO = 1
IDDOBAVKA = 2
IDKORM = 3

REG_ERROR = 14
REG_STATUS = 36
REG_CMD = 0

REALVES1INDEX = 54
REALVES2INDEX = 55
REALVES3INDEX = 56

VES1INDEX = 4
VES2INDEX = 5
VES3INDEX = 6
VESCHASTOTAINDEX = 3
VESMAX = 15
# DBSTATUS
VES1READYUNLOAD = 0
VES2READYUNLOAD = 1
VES3READYUNLOAD = 2
VES1READYLOAD = 3
VES2READYLOAD = 4
VES3READYLOAD = 5
MIXERREADYLOAD = 6
MIXERREADYUNLOAD = 7
# DBSTATUS2

NORIAREADYLOAD = 8
LINE1READYLOAD = 9
LINE2READYLOAD = 10
DOPDOBAVKAREADY = 11
MASLOREADY = 12  # МАСЛО ЗАГРУЖЕНО

COMMAND_SHNEKMIXER_ON = 51
COMMAND_SHNEKMIXER_OFF = 50
COMMAND_INIT = 111
COMMAND_MIXER_ON = 41
COMMAND_MIXER_OFF = 40
COMMAND_MIXER_UNLOAD = 42
COMMAND_LINE1_START = 101
COMMAND_LINE1_STOP = 100
COMMAND_LINE2_START = 201
COMMAND_LINE2_STOP = 200
COMMAND_VES12_START = 11
COMMAND_VES3_START = 13
COMMAND_DOPDOBAVKA_START = 14
COMMAND_OIL_START = 15
COMMAND_OIL_STOP = 16
COMMAND_OIL_START_HAND = 17

COMMAND_VES1_UNLOAD = 110
COMMAND_VES2_UNLOAD = 120
COMMAND_VES3_UNLOAD = 130
# COMMAND_VES3_UNLOAD_HAND = 131
COMMAND_NORIA_INIT = 199
COMMAND_NORIA_STOP = 198
COMMAND_ZERO_WEIGHT1 = 31
COMMAND_ZERO_WEIGHT2 = 32
COMMAND_ZERO_WEIGHT3 = 33
COMMAND_CAL_WEIGHT1 = 34
COMMAND_CAL_WEIGHT2 = 35
COMMAND_CAL_WEIGHT3 = 36
COMMAND_STOP = 1
COMMAND_PAUSE = 2
COMMAND_RUN = 3

IDVES2 = 0
IDVES3 = 1
IDMASLO = 2
IDLINE1 = 3
IDLINE2 = 4
IDMIXER = 5
IDLINEK = 6


# Error Warning
ERRORWEIGHT1 = 0 #   0 ves1error (слишком большое значение в заказе) -> не грузится
ERRORWEIGHT2 = 1 #   1 ves2error (слишком большое значение в заказе) ->
ERRORWEIGHT3 = 2  #   2 ves3error (слишком большое значение в заказе)->
ERRORLINEK = 3 #   3 errorlineK (ошибка при команде на включение шнека смесителя при  выключенной нории) -> не включается шнек смеситель
ERRORPERKLAPAN = 4  #   4 errorperklapan (перекидование клапана нории происходит больше 1 минуты) ->
ERRORMIXER = 5  #   5  errormixer( выключено тепловое реле)
ERRORLINE1 = 6 #   6 errorline1  выключено тепловое реле
ERRORLINE2 = 7 #   7 errorline2 выключено тепловое реле
# reg14 plc16
ERRORAWILA = 8 #   0 AWILA ERR (Загорелась лампа fault)
ERRORMIXERNOTUNLOAD = 9 #   1 mixer not unload
ERRORMIXERNOTOPEN = 10  #   2 миксер не открывается, так как бункер под миксером не пустой
ERROREXECUTECMD = 101 # ошибка выполнения команды(scada передал, плк не исполнил(бывает изза потери связи))