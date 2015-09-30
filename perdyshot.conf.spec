[Settings]
    background   = string(default = '')
    shadowColour = string(default = '#949494')
    filename     = string(default = '')

    cornerImage   = string(default = '')
    cornerImageDM = string(default = '')
    borderImage   = string(default = '')
    borderImageDM = string(default = '')

[Applications]
    [[__many__]]
        sizeBugged  = integer(default = 0)
        roundTop    = boolean(default = None)
        roundBottom = integer(0, 2, default = None)
