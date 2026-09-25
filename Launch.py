from launcher.app import main

if __name__ == '__main__':
    import sys
    if '--desktop-smoke-test' in sys.argv:
        from pathlib import Path
        main(Path(sys.argv[sys.argv.index('--desktop-smoke-test')+1]).resolve())
    elif '--self-test' in sys.argv:
        import webview
        from launcher.app import ROOT
        from launcher.updater import REPOSITORY
        assert (ROOT/'ui/preview.html').is_file()
        assert (ROOT/'ui/runtime.js').is_file()
        assert (ROOT/'ui/assets/bear-cave-logo.png').is_file()
        if (ROOT/'connection.json').exists():
            from launcher.connection import load
            load(ROOT)
        print('LAUNCHER BUNDLE OK: '+REPOSITORY)
    else:
        try:
            main()
        except Exception as error:
            if sys.platform=='win32':
                import ctypes
                ctypes.windll.user32.MessageBoxW(None,'The launcher could not start. Microsoft Edge WebView2 Runtime is required.\n\n'+str(error),'The Bear Cave Launcher',0x10)
            raise
