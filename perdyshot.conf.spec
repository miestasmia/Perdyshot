[Settings]
    background   = string(default = '')
    shadowColour = string(default = '#949494')
    filename     = string(default = '')

    cornerImage   = string(default = '')
    cornerImageDM = string(default = '')
    borderImage   = string(default = '')
    borderImageDM = string(default = '')

[GUI]
    [[CaptureModes]]
        [[[__many__]]]
            type                    = option('simple', 'script')
            mode                    = option('window', 'selection', default = None)
            file                    = string(default = None)
            program                 = string(default = None)
            copy                    = boolean(default = False)
            notification            = boolean(default = False)
            notificationImage       = string(default = None)
            notificationTitle       = string(default = 'Screenshot taken!')
            notificationDescription = string(default = '')

[Applications]
    [[__many__]]
        sizeBugged  = integer(default = 0)
        roundTop    = boolean(default = None)
        roundBottom = integer(0, 2, default = None)
