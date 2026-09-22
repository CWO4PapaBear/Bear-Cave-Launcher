from launcher.app import main

if __name__ == '__main__':
    import sys
    if '--self-test' in sys.argv:
        from launcher.app import ROOT
        from launcher.updater import REPOSITORY
        assert (ROOT/'ui/preview.html').is_file()
        assert (ROOT/'ui/runtime.js').is_file()
        assert (ROOT/'ui/assets/bear-cave-logo.png').is_file()
        print('LAUNCHER BUNDLE OK: '+REPOSITORY)
    else:
        main()
