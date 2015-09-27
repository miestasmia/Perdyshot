[Settings]
    background = string(default = '')
    filename   = string(default = '')

[Applications]
    [[__many__]]
        sizeBugged  = integer(default = 0)
        roundTop    = boolean(default = None)
        roundBottom = integer(0, 2, default = None)
