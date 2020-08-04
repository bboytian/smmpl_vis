# data
'''
directories seen by python C:/Program Files (x86)/...;  '/' or '\\' is allowed
directories seen by gitbash, i.e. os.system C:/Program\ Files\ \(x86\)/...
                                         or 'C:/Program Files (x86)/...'
directories seen by rsync in os.system /c/Program\ Files\ \(x86\)/...
'''

## on smmpl laptop
MPLSIGMADIR = 'C:/Program Files (x86)/SigmaMPL'
MPLSIGMADATADIR = MPLSIGMADIR + '/DATA'
MPLSIGMALOGDIR = MPLSIGMADIR + '/Log'
MPLCONFIGFILE = MPLSIGMADIR + '/mpl.ini'
MPLSIGMAPROG = 'SigmaMPL2015R2.3.exe'
MPLSIGMAPROGDIR = MPLSIGMADIR + '/' + MPLSIGMAPROG
MPLDESKDIR = 'C:/Users/mpluser/Desktop'
MPLDATADIR = MPLDESKDIR + '/smmpl_E2'
MPLOPCODESDIR = MPLDESKDIR + '/smmpl_opcodes'

## on solaris server
SOLARISIP = '137.132.39.187'  # public IP
SOLARISUSER = 'tianli'
SOLARISDATADIR = '/home/tianli/SOLAR_EMA_project/data'
SOLARISMPLDATADIR = SOLARISDATADIR + '/smmpl_E2'
SOLARISRAZONDATADIR = SOLARISDATADIR + '/razon_E2'

## data nomenclature; indices to change manually when fmts are adjusted
DATEFMT, TIMEFMT = '{:%Y%m%d}', '{:%Y%m%d%H%M}'  # has to be compatible for pandas
DATELEN, TIMELEN = 8, 12
SCANPATSDATEIND, SCANPATEDATEIND, SCANPATDATEIND = -37, -24, -12
SCANPATFILE = TIMEFMT + '_' + TIMEFMT + '_skyscan.txt'
MPLDATEIND, MPLTIMEIND = -8, -4
MPLFILE = TIMEFMT + '.mpl'
MPLEOMTIMEIND = -9
MPLEOMFILE = TIMEFMT + '_eom.flag'  # indicates end of measurement
MPLLOGDATEIND, MPLLOGTIMEIND = -14, -10
MPLLOGFILE = TIMEFMT + 'MPLLog.txt'
MPLLOGCURFILE = 'mplLog.txt'
PSLOGFILE = DATEFMT + '_{}.log'  # names are controlled in __main__



# scripting
AVERAGINGTIME = 15           # [s], lidar shot duration
BINRESMODE = 3               # '2', '3', '4', '5' -> 5m, 15m, 30m, 75m
ENABLESCANPATBOO = 1         # '0' -> disable, '1' -> enable
ENABLESCANNER = 1            # '0' -> disable, '1' -> enable

## __main__
NORMALOPSBOO = True

## quickscan_main & quickscanpat_calc.__main__
QUICKSCANTIMES = 10       # num of times we want to perform measurement
QUICKSCANWAITTIME = (630-343)  # [min] waittime between measurements
QUICKSCANTYPE = 'horisweep'
QUICKSCANFILE = TIMEFMT + '_' + QUICKSCANTYPE + '.txt'
HIGHSUNTHRES = 0.05                              # [deg]

## skyscan_main
SIGMAMPLWARMUP = 35 + AVERAGINGTIME  # [s] so that fileman holds off first
DAYSINADV = 1                  # [day] in adv to calculate scanpat in coldstart
FILEMANWAIT = 10               # [min]
WAITCHECK = 60                 # [s]

## sop
WINDOWFILESDIR = MPLOPCODESDIR + '/window_files'

### sop.file_man.mpl2solaris_datasync
RSYNCFILE = 'rsync/rsync.exe'
SSHFILE = 'ssh/ssh.exe'
IDRSADIR = 'C:/Users/mpluser/.ssh/id_rsa'  # private key location for rsync

### sop.sigmampl_boot.scan_init
SEDFILE = 'sed/sed.exe'


# computations

## scanpat_calc.__main__
CALCDURATION = 1         # [day] # also in __main__
UTCINFO = 0              # [hr] # '0' if run on computer with gmt time
FINEDELTATIME = 2               # [min]
SEGDELTA = 30                   # [min]

ELEVATION = 70                              # [m]
LATITUDE, LONGITUDE = 1.299119, 103.771232 # [deg]

ANGOFFSET = 141                 # [deg]
PRIMARYAXIS = 'elevation'       # 'azimuth' or 'elevation'

## scanpat_calc.pathplanner.calc_dirpointsara
RAVELSTR = 's'                  # only 's' for now
RAVELARGS = 0                   # 0 to 3

## scanpat_calc.sunforcaster.__init__
SFAPI = 'pysolar_API'           # 'pysolar_API' or 'pysolarfast_API'

## scanpat_calc.targetgenerator.plotshapes.__init__
R = 15                  # [km] lidar SNR range limit
L0 = 6                  # [km] size of grid
LP = 5                  # [km] size of pixel
THETAS = 0.05          # [rad] solid angle of sun cone
CLOSEPROXTHRES = LP/3   # [km] for targ_aimlines

## scanpat_calc.targetgenerator.plotshapes.grid
POLYLENALPHA = 3/5

## scanpat_calc.targetgenerator.plotshapes.cone
PHINUMINTS = 4        # discretisation
RHONUMINTS = 1
LNUMSWATH = 10
ALPHASHAPE = 0.1      # alphashape parameter for cone swath optimising
SWATHPLOTANG = 85     # [deg], angle range where sun swath is well defined
                      # this has to be scaled with THETAS

## scanpat_calc.targetgenerator.plotshapes.aimlines
FILLERNUM = 1e4                 # [km] for resample_func, !> grid size



# visualisation; params specific to plotting are left in the scripts

## scan_vis.__main__
REALTIMEBOO = False
REALTIMEFPS = 2

FAKETIMESTARTTIME = '2020-07-21 10:00:00'
FAKETIMEFPS = 1000
FAKETIMEEQUIVTIME = 20          # [s]
FAKETIMEINTERVAL = 0

VISDURATION = 2                 # [hr]

## scan_vis.plotshapes.__init__
SHOWCHECKBOO = False            # cannot be True if running visualisation for
                                # the first time

## scanpat_calc.pathplanner.calc_pathara
ANGLERES = 0.1                  # [deg] for visualisation
