from engine.physics import entity


# ========================================================================= #
# boid object
# ========================================================================= #


class Boid(entity.Entity):
    def __init__(self, name="boid", zlayer=0):
        super().__init__(name, zlayer)

    # ----------------------------------------------------------------------- #
    # logic
    # ---------------------------------------------------------------------- #

    def update(self):
        # update boid logic here
        print(self)
        pass
