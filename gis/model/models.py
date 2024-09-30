

class GISModel:
    pass


class Point_T(GISModel):

    def __init__(self, x, y, srid="32638") -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.srid = srid
