[Settings]
    background = string(default = '')

[Applications]
    [[__many__]]
        sizeBugged  = boolean(default = False)
        roundTop    = boolean(default = None)
        roundBottom = integer(0, 2, default = None)
