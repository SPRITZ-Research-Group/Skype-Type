class Config:
    def __init__(self):
        pass

    VERSION = "1.0"
    PROJECT_URL = "http://spritz.math.unipd.it/projects/dst"
    LICENSE = "GPLv3"
    SPLASHSCREEN = """
       SSSSSSSSSSSSSSS      &&&&&&&&&&  TTTTTTTTTTTTTTTTTTTTTTT
     SS:::::::::::::::S    &::::::::::& T:::::::::::::::::::::T
    S:::::SSSSSS::::::S   &::::&&&:::::&T:::::::::::::::::::::T
    S:::::S     SSSSSSS  &::::&   &::::&T:::::TT:::::::TT:::::T
    S:::::S              &::::&   &::::&TTTTTT  T:::::T  TTTTTT
    S:::::S               &::::&&&::::&         T:::::T
     S::::SSSS            &::::::::::&          T:::::T
      SS::::::SSSSS        &:::::::&&           T:::::T
        SSS::::::::SS    &::::::::&   &&&&      T:::::T
           SSSSSS::::S  &:::::&&::&  &:::&      T:::::T
                S:::::S&:::::&  &::&&:::&&      T:::::T
                S:::::S&:::::&   &:::::&        T:::::T
    SSSSSSS     S:::::S&:::::&    &::::&      TT:::::::TT
    S::::::SSSSSS:::::S&::::::&&&&::::::&&    T:::::::::T
    S:::::::::::::::SS  &&::::::::&&&::::&    T:::::::::T
     SSSSSSSSSSSSSSS      &&&&&&&&   &&&&&    TTTTTTTTTTT

    Skype&Type! Attack - v{}
    {}


    SPRITZ Group (www.spritz.math.unipd.it)
        - Dr. Alberto Compagno (Sapienza University of Rome, IT)
        - Prof. Mauro Conti (Univ. of Padua, IT)
        - M.Sc. Daniele Lain (Univ. of Padua, IT)

    SPROUT Group (sprout.ics.uci.edu)
        - Prof. Gene Tsudik (UC Irvine, USA)

    This Software developed by Daniele Lain

    2017 - {}
    ___________________________________________________________
        """.format(VERSION, PROJECT_URL, LICENSE).split("\n")

    # Dispatcher options
    dispatcher_threshold = 90
    dispatcher_min_interval = 8000
    dispatcher_window_size = 100
    dispatcher_step_size = 1
    dispatcher_persistence = True
    # Number of worker processes
    workers = 4
    # Output options
    dict_sep_threshold = 5
    dict_folder = 'dictionaries'


CONFIG = Config()
