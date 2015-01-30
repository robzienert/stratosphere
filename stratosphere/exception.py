class StratosphereError(StandardError):
    pass


class StackNotFoundError(StratosphereError):
    pass


class PlanError(StratosphereError):
    pass
