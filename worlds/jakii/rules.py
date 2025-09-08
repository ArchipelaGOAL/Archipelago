def slums_to_port(state, player) -> bool:
    return (state.has("Red Security Pass", player)
            or state.has_all(("Green Security Pass", "Yellow Security Pass"), player)
            or state.has_all(("Air Train Pass", "JET-Board"), player))


def slums_to_stadium(state, player) -> bool:
    return (state.has("Green Security Pass", player)
            or state.has_all(("Red Security Pass", "Yellow Security Pass"), player)
            or state.has_all(("Air Train Pass", "JET-Board", "Yellow Security Pass"), player))


def slums_to_market(state, player) -> bool:
    return (state.has_all(("Green Security Pass", "Yellow Security Pass"), player)
            or state.has_all(("Red Security Pass", "Yellow Security Pass"), player)
            or state.has_all(("Air Train Pass", "JET-Board", "Yellow Security Pass"), player))


def port_to_stadium(state, player) -> bool:
    return (state.has("Yellow Security Pass", player)
            or state.has_all(("Red Security Pass", "Green Security Pass"), player)
            or state.has_all(("Air Train Pass", "JET-Board", "Green Security Pass"), player))


def port_to_market(state, player) -> bool:
    return state.has("Yellow Security Pass", player)


def market_to_stadium(state, player) -> bool:
    return state.has("Yellow Security Pass", player)


def slums_to_landing(state, player) -> bool:
    return (state.has("JET-Board", player)
            or state.has_all(("Red Security Pass", "Air Train Pass"), player)
            or state.has_all(("Green Security Pass", "Yellow Security Pass", "Air Train Pass"), player))


def slums_to_nest(state, player) -> bool:
    return (state.has_all(("JET-Board", "Air Train Pass"), player)
            or state.has_all(("Red Security Pass", "Air Train Pass"), player)
            or state.has_all(("Green Security Pass", "Yellow Security Pass", "Air Train Pass"), player))


def any_gun(state, player) -> bool:
    return state.has_any(("Scatter Gun", "Blaster", "Vulcan Fury", "Peacemaker"), player)
