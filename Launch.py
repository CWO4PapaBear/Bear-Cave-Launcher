from launcher.app import main

if __name__ == '__main__':
    import sys
    if '--pick-folder' in sys.argv:
        from launcher.folder_picker import main as pick_folder
        index=sys.argv.index('--pick-folder')
        pick_folder(sys.argv[index+1] if len(sys.argv)>index+1 else '')
    elif '--self-test' in sys.argv:
        from launcher.app import ROOT
        from launcher.updater import REPOSITORY
        assert (ROOT/'ui/preview.html').is_file()
        assert (ROOT/'ui/runtime.js').is_file()
        assert (ROOT/'ui/assets/bear-cave-logo.png').is_file()
        print('LAUNCHER BUNDLE OK: '+REPOSITORY)
    else:
        main()
